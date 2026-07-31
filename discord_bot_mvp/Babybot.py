import os
import re
import json
import sqlite3
import logging
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from rapidfuzz import fuzz
from openai import OpenAI

# ==================== CẤU HÌNH ====================
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise RuntimeError("Thiếu DISCORD_TOKEN trong file .env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Tên role được phép "dạy" bot (thả ✅ để lưu câu trả lời vào cache).
# Nếu để trống, MẶC ĐỊNH KHÔNG cho phép ai học cả (an toàn hơn là mở toang).
COACH_ROLE_NAME = os.getenv("COACH_ROLE_NAME", "").strip()

# Tầng 1 - fuzzy match cục bộ (free, tức thì):
# >= AUTO_THRESHOLD -> chấp nhận luôn, không cần gọi OpenAI.
AUTO_THRESHOLD = int(os.getenv("SIMILARITY_AUTO_THRESHOLD", "92"))
# >= CANDIDATE_THRESHOLD -> đưa vào danh sách ứng viên để OpenAI xét ngữ nghĩa.
CANDIDATE_THRESHOLD = int(os.getenv("SIMILARITY_CANDIDATE_THRESHOLD", "40"))
# Số ứng viên tối đa gửi cho OpenAI (tránh gửi cả database, tốn tiền + chậm khi cache lớn)
CANDIDATE_LIMIT = int(os.getenv("SIMILARITY_CANDIDATE_LIMIT", "12"))
# Ngưỡng % để coi 1 câu hỏi mới lưu là "trùng" câu đã có -> ghi đè thay vì tạo dòng mới
UPSERT_THRESHOLD = int(os.getenv("SIMILARITY_UPSERT_THRESHOLD", "90"))
# Ngưỡng % để coi câu hỏi mới trùng với 1 Thread đang chờ Coach trả lời
# -> trỏ người hỏi vào Thread đó thay vì tạo Thread mới
PENDING_MATCH_THRESHOLD = int(os.getenv("SIMILARITY_PENDING_THRESHOLD", "70"))

DB_PATH = os.getenv("DB_PATH", "memory.db")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("qa-bot")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True  # cần để đọc role của người thả reaction

bot = commands.Bot(command_prefix="!", intents=intents)


# ==================== DATABASE (CACHE LAYER) ====================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS qa_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_question TEXT,
            clean_question TEXT,
            answer TEXT,
            hit_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    # Theo dõi các Thread đang chờ Coach trả lời, để tránh tạo Thread trùng
    # khi nhiều người hỏi cùng một vấn đề trước khi có câu trả lời được xác nhận.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pending_threads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_question TEXT,
            clean_question TEXT,
            thread_id INTEGER,
            guild_id INTEGER,
            resolved INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def normalize_text(text: str) -> str:
    """Viết thường, bỏ ký tự đặc biệt, gọn khoảng trắng.
    Giữ nguyên dấu tiếng Việt vì dấu mang nghĩa (không strip accent)."""
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _bump_hit_count(row_id: int, current_hits: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE qa_cache SET hit_count = ? WHERE id = ?", (current_hits + 1, row_id))
    conn.commit()
    conn.close()


def find_pending_thread(user_query: str):
    """Tìm Thread đang mở (chưa được Coach xác nhận) hỏi về vấn đề tương tự.
    Trả về (thread_id, guild_id) hoặc None."""
    clean_query = normalize_text(user_query)
    if not clean_query:
        return None

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT clean_question, thread_id, guild_id FROM pending_threads WHERE resolved = 0"
    )
    rows = cursor.fetchall()
    conn.close()

    best_score = 0
    best_match = None
    for saved_clean_q, thread_id, guild_id in rows:
        score = fuzz.token_sort_ratio(clean_query, saved_clean_q)
        if score > best_score:
            best_score = score
            best_match = (thread_id, guild_id)

    if best_match and best_score >= PENDING_MATCH_THRESHOLD:
        log.info("Tìm thấy Thread đang chờ tương tự (score=%s): %s", best_score, clean_query[:50])
        return best_match
    return None


def add_pending_thread(raw_question: str, thread_id: int, guild_id: int):
    clean_q = normalize_text(raw_question)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO pending_threads (raw_question, clean_question, thread_id, guild_id)
        VALUES (?, ?, ?, ?)
        """,
        (raw_question, clean_q, thread_id, guild_id),
    )
    conn.commit()
    conn.close()


def resolve_pending_thread(thread_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE pending_threads SET resolved = 1 WHERE thread_id = ? AND resolved = 0",
        (thread_id,),
    )
    conn.commit()
    conn.close()


def _ask_openai_for_match(user_query: str, candidates: list):
    """Nhờ OpenAI xét xem user_query có tương đồng NGỮ NGHĨA với câu nào
    trong danh sách candidates không. candidates là list các dict
    {id, question, answer}. Trả về id được chọn (int) hoặc None.
    Dùng JSON mode để kết quả có cấu trúc, tránh parse text không ổn định."""
    if not openai_client or not candidates:
        return None

    knowledge = "\n".join(
        f"- id={c['id']}: \"{c['question']}\"" for c in candidates
    )
    system_prompt = (
        "Bạn là bộ phân loại câu hỏi. Bạn nhận một câu hỏi mới và một danh sách "
        "các câu hỏi đã có sẵn (kèm id). Nhiệm vụ: xác định xem câu hỏi mới có "
        "CÙNG Ý NGHĨA / CÙNG MỤC ĐÍCH với một trong các câu hỏi đã có không, "
        "kể cả khi cách diễn đạt khác nhau. Chỉ chọn khi bạn tự tin là hỏi về "
        "cùng một vấn đề. Nếu không chắc chắn hoặc không có câu nào phù hợp, "
        "trả về null.\n\n"
        'Trả lời DUY NHẤT bằng JSON theo format: {"matched_id": <id hoặc null>, '
        '"confidence": <"high"|"medium"|"low">}'
    )
    user_prompt = f"Câu hỏi mới: \"{user_query}\"\n\nDanh sách câu hỏi đã có:\n{knowledge}"

    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content)
        matched_id = result.get("matched_id")
        confidence = result.get("confidence", "low")

        if matched_id is None or confidence == "low":
            return None
        return int(matched_id)
    except Exception as e:
        log.warning("Lỗi khi gọi OpenAI để xét câu hỏi tương tự: %s", e)
        return None


def find_in_cache(user_query: str):
    """Tìm câu hỏi TƯƠNG TỰ trong cache theo 2 tầng:
    1) fuzzy matching cục bộ (nhanh, free) - nếu score rất cao thì chấp nhận luôn.
    2) nếu không rõ ràng, nhờ OpenAI xét ngữ nghĩa trên tập ứng viên đã lọc bằng fuzzy.
    Trả về (answer, matched_id) hoặc (None, None)."""
    clean_query = normalize_text(user_query)
    if not clean_query:
        return None, None

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, clean_question, answer, hit_count FROM qa_cache")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return None, None

    # ---- Tầng 1: fuzzy match cục bộ ----
    scored = []
    for row_id, saved_clean_q, saved_answer, hits in rows:
        score = fuzz.token_sort_ratio(clean_query, saved_clean_q)
        scored.append((score, row_id, saved_clean_q, saved_answer, hits))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_score, top_id, top_q, top_answer, top_hits = scored[0]

    if top_score >= AUTO_THRESHOLD:
        _bump_hit_count(top_id, top_hits)
        log.info("Fuzzy auto-match (score=%s) cho: %s", top_score, clean_query[:50])
        return top_answer, top_id

    # ---- Tầng 2: nhờ OpenAI xét ngữ nghĩa trên các ứng viên ----
    candidates = [
        {"id": row_id, "question": saved_q, "answer": saved_answer, "hits": hits}
        for score, row_id, saved_q, saved_answer, hits in scored
        if score >= CANDIDATE_THRESHOLD
    ][:CANDIDATE_LIMIT]

    if not candidates:
        return None, None

    matched_id = _ask_openai_for_match(user_query, candidates)
    if matched_id is None:
        return None, None

    for c in candidates:
        if c["id"] == matched_id:
            _bump_hit_count(c["id"], c["hits"])
            log.info("OpenAI semantic match cho: %s -> id=%s", clean_query[:50], matched_id)
            return c["answer"], c["id"]

    return None, None


def save_to_cache(raw_question: str, answer: str):
    clean_q = normalize_text(raw_question)
    if not clean_q or not answer or not answer.strip():
        log.warning("Bỏ qua lưu cache: câu hỏi hoặc câu trả lời rỗng.")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Kiểm tra xem câu hỏi này đã tồn tại trong cache chưa (fuzzy match).
    # Nếu đã có -> GHI ĐÈ (update) câu trả lời cũ thay vì tạo dòng trùng.
    # Điều này cho phép Coach sửa lại nếu lỡ tick nhầm câu trả lời sai trước đó.
    cursor.execute("SELECT id, clean_question FROM qa_cache")
    rows = cursor.fetchall()

    existing_id = None
    best_score = 0
    for row_id, saved_clean_q in rows:
        score = fuzz.token_sort_ratio(clean_q, saved_clean_q)
        if score > best_score:
            best_score = score
            existing_id = row_id

    if existing_id is not None and best_score >= UPSERT_THRESHOLD:
        cursor.execute(
            """
            UPDATE qa_cache
            SET raw_question = ?, clean_question = ?, answer = ?, created_at = ?
            WHERE id = ?
            """,
            (raw_question, clean_q, answer, datetime.now(timezone.utc), existing_id),
        )
        conn.commit()
        conn.close()
        log.info("Đã CẬP NHẬT cache (ghi đè câu trả lời cũ, id=%s, score=%s): %s",
                  existing_id, best_score, clean_q[:50])
        return True

    cursor.execute(
        """
        INSERT INTO qa_cache (raw_question, clean_question, answer, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (raw_question, clean_q, answer, datetime.now(timezone.utc)),
    )
    conn.commit()
    conn.close()
    log.info("Đã lưu cache mới: %s", clean_q[:50])
    return True


# ==================== HELPERS ====================
def is_coach(member: discord.Member) -> bool:
    """Kiểm tra người dùng có role Coach được cấu hình hay không.
    Nếu COACH_ROLE_NAME chưa được set trong .env, mặc định KHÔNG ai được học
    (an toàn hơn là cho phép tất cả)."""
    if not COACH_ROLE_NAME:
        return False
    if not isinstance(member, discord.Member):
        return False
    return any(role.name == COACH_ROLE_NAME for role in member.roles)


async def _require_coach(interaction: discord.Interaction) -> bool:
    """Kiểm tra quyền Coach cho slash command. Nếu không đủ quyền, tự phản hồi
    lỗi (ephemeral - chỉ người gọi lệnh thấy) và trả về False."""
    if not is_coach(interaction.user):
        await interaction.response.send_message(
            f"⛔ Lệnh này chỉ dành cho role **{COACH_ROLE_NAME or '(chưa cấu hình)'}**.",
            ephemeral=True,
        )
        return False
    return True


# ==================== SLASH COMMANDS: QUẢN LÝ CACHE (chỉ Coach) ====================
cache_group = app_commands.Group(
    name="cache", description="Quản lý bộ nhớ Q&A đã học của bot (chỉ Coach)"
)


@cache_group.command(name="list", description="Xem danh sách các câu hỏi đã lưu trong cache")
@app_commands.describe(page="Trang muốn xem (mỗi trang 10 mục, mặc định trang 1)")
async def cache_list(interaction: discord.Interaction, page: int = 1):
    if not await _require_coach(interaction):
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, raw_question, answer, hit_count FROM qa_cache ORDER BY id")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await interaction.response.send_message("📭 Cache hiện đang trống.", ephemeral=True)
        return

    page = max(page, 1)
    page_size = 10
    total_pages = (len(rows) - 1) // page_size + 1
    page = min(page, total_pages)
    start = (page - 1) * page_size
    page_rows = rows[start:start + page_size]

    lines = []
    for row_id, q, a, hits in page_rows:
        q_short = q if len(q) <= 60 else q[:60] + "…"
        a_short = a if len(a) <= 80 else a[:80] + "…"
        lines.append(f"**#{row_id}** (dùng {hits} lần)\n❓ {q_short}\n💬 {a_short}")

    embed = discord.Embed(
        title=f"📚 Cache Q&A — Trang {page}/{total_pages} (tổng {len(rows)} mục)",
        description="\n\n".join(lines),
        color=discord.Color.blurple(),
    )
    embed.set_footer(text="Dùng /cache view id:<id> để xem chi tiết, /cache edit hoặc /cache delete để chỉnh sửa.")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@cache_group.command(name="view", description="Xem chi tiết đầy đủ 1 mục trong cache theo ID")
@app_commands.describe(entry_id="ID của mục cần xem (lấy từ /cache list hoặc /cache search)")
async def cache_view(interaction: discord.Interaction, entry_id: int):
    if not await _require_coach(interaction):
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT raw_question, answer, hit_count, created_at FROM qa_cache WHERE id = ?",
        (entry_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        await interaction.response.send_message(f"Không tìm thấy mục #{entry_id}.", ephemeral=True)
        return

    q, a, hits, created = row
    embed = discord.Embed(title=f"📄 Chi tiết mục #{entry_id}", color=discord.Color.green())
    embed.add_field(name="Câu hỏi", value=q or "(rỗng)", inline=False)
    embed.add_field(name="Câu trả lời", value=a or "(rỗng)", inline=False)
    embed.add_field(name="Số lần dùng lại", value=str(hits), inline=True)
    embed.add_field(name="Cập nhật lúc", value=str(created), inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@cache_group.command(name="search", description="Tìm các mục gần giống với 1 câu hỏi (để lấy ID)")
@app_commands.describe(query="Câu hỏi hoặc từ khoá muốn tìm")
async def cache_search(interaction: discord.Interaction, query: str):
    if not await _require_coach(interaction):
        return

    clean_query = normalize_text(query)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, clean_question, answer FROM qa_cache")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await interaction.response.send_message("📭 Cache hiện đang trống.", ephemeral=True)
        return

    scored = [
        (fuzz.token_sort_ratio(clean_query, cq), row_id, a)
        for row_id, cq, a in rows
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    top5 = scored[:5]

    lines = [
        f"**#{row_id}** (giống {score:.0f}%) — {a[:70] + ('…' if len(a) > 70 else '')}"
        for score, row_id, a in top5
    ]
    await interaction.response.send_message(
        "🔎 Kết quả gần giống nhất:\n" + "\n".join(lines), ephemeral=True
    )


@cache_group.command(name="edit", description="Sửa lại câu trả lời của 1 mục trong cache")
@app_commands.describe(entry_id="ID của mục cần sửa", new_answer="Nội dung câu trả lời mới")
async def cache_edit(interaction: discord.Interaction, entry_id: int, new_answer: str):
    if not await _require_coach(interaction):
        return

    if not new_answer.strip():
        await interaction.response.send_message("⚠️ Câu trả lời mới không được để trống.", ephemeral=True)
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM qa_cache WHERE id = ?", (entry_id,))
    if not cursor.fetchone():
        conn.close()
        await interaction.response.send_message(f"Không tìm thấy mục #{entry_id}.", ephemeral=True)
        return

    cursor.execute(
        "UPDATE qa_cache SET answer = ?, created_at = ? WHERE id = ?",
        (new_answer.strip(), datetime.now(timezone.utc), entry_id),
    )
    conn.commit()
    conn.close()
    log.info("Coach %s đã sửa cache #%s qua slash command.", interaction.user, entry_id)
    await interaction.response.send_message(f"✅ Đã cập nhật câu trả lời cho mục #{entry_id}.", ephemeral=True)


@cache_group.command(name="delete", description="Xoá 1 mục khỏi cache")
@app_commands.describe(entry_id="ID của mục cần xoá")
async def cache_delete(interaction: discord.Interaction, entry_id: int):
    if not await _require_coach(interaction):
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM qa_cache WHERE id = ?", (entry_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    if deleted:
        log.info("Coach %s đã xoá cache #%s qua slash command.", interaction.user, entry_id)
        await interaction.response.send_message(f"🗑️ Đã xoá mục #{entry_id}.", ephemeral=True)
    else:
        await interaction.response.send_message(f"Không tìm thấy mục #{entry_id}.", ephemeral=True)


bot.tree.add_command(cache_group)


# ==================== DISCORD EVENT HANDLERS ====================
@bot.event
async def on_ready():
    init_db()
    try:
        synced = await bot.tree.sync()
        log.info("Đã đồng bộ %d slash command(s).", len(synced))
    except Exception as e:
        log.warning("Lỗi khi đồng bộ slash command: %s", e)

    log.info(
        "🤖 Bot %s đã sẵn sàng! (auto=%s%%, candidate=%s%%, openai=%s, role coach=%s)",
        bot.user.name,
        AUTO_THRESHOLD,
        CANDIDATE_THRESHOLD,
        "bật" if openai_client else "TẮT (thiếu OPENAI_API_KEY)",
        COACH_ROLE_NAME or "(chưa cấu hình - học bị TẮT)",
    )


@bot.event
async def on_message(message: discord.Message):
    print(f">>> MESSAGE EVENT: author={message.author} bot={message.author.bot} content={message.content!r}", flush=True)
    if message.author.bot:
        return

    # Chỉ coi là "được hỏi" khi bot bị @mention TRỰC TIẾP
    # (loại trừ @everyone/@here, vì mentioned_in() mặc định trả về True
    # luôn cho cả 2 trường hợp đó - nên dùng message.mentions để chỉ bắt
    # mention thật sự nhắm vào bot).
    is_mentioned = bot.user in message.mentions

    if is_mentioned:
        user_query = message.content.replace(f"<@{bot.user.id}>", "").strip()
        user_query = user_query.replace(f"<@!{bot.user.id}>", "").strip()

        if not user_query:
            await message.channel.send("Em đây ạ! Bạn cần hỗ trợ câu hỏi gì thế?")
            return

        cached_answer, _ = find_in_cache(user_query)

        if cached_answer:
            await message.channel.send(f"🧠 **[Từ bộ nhớ Bot]:**\n{cached_answer}")
        else:
            # Trước khi tạo Thread mới, kiểm tra xem đã có Thread nào đang
            # chờ Coach trả lời cho câu hỏi tương tự chưa -> tránh trùng lặp.
            pending = find_pending_thread(user_query)
            if pending:
                thread_id, guild_id = pending
                jump_url = f"https://discord.com/channels/{guild_id}/{thread_id}"
                await message.channel.send(
                    f"👀 Câu hỏi này có vẻ giống một câu đang chờ Coach trả lời rồi nè! "
                    f"Bạn xem thử ở đây nhé: {jump_url}"
                )
                return

            reply_msg = await message.channel.send(
                "❓ Câu hỏi này em chưa có trong dữ liệu! Đã tạo Thread hỗ trợ."
            )
            thread = await reply_msg.create_thread(
                name=f"Hỏi đáp: {user_query[:25]}..."
            )
            add_pending_thread(user_query, thread.id, message.guild.id)
            await thread.send(
                f"📌 **Câu hỏi từ {message.author.mention}:**\n> {user_query}\n\n"
                f"👉 Nhờ Lab Coach hỗ trợ giải đáp giúp bạn với ạ! "
                f"(Coach trả lời xong nhớ thả ✅ vào tin nhắn trả lời để bot ghi nhớ nhé)"
            )

    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    print(f">>> RAW REACTION EVENT: emoji={payload.emoji} user={payload.user_id} channel={payload.channel_id}", flush=True)
    log.info(
        "Reaction nhận được: emoji=%s, user_id=%s, channel_id=%s",
        payload.emoji, payload.user_id, payload.channel_id,
    )

    # 1. Bỏ qua reaction của chính bot
    if payload.user_id == bot.user.id:
        log.info("-> Bỏ qua: đây là reaction của chính bot.")
        return

    # 2. Chỉ quan tâm reaction ✅
    if str(payload.emoji) != "✅":
        log.info("-> Bỏ qua: emoji không phải ✅ (nhận được: %s).", payload.emoji)
        return

    try:
        channel = await bot.fetch_channel(payload.channel_id)

        # 3. Chỉ xử lý reaction trong Thread
        if not isinstance(channel, discord.Thread):
            log.info("-> Bỏ qua: reaction không nằm trong Thread (type=%s).", type(channel))
            return

        guild = channel.guild
        reactor = await guild.fetch_member(payload.user_id)
        log.info("-> Người thả reaction: %s, roles: %s",
                  reactor.display_name, [r.name for r in reactor.roles])

        # 4. Chỉ Coach mới được phép "dạy" bot
        if not is_coach(reactor):
            log.info("-> Bỏ qua: %s không có role '%s'.", reactor.display_name, COACH_ROLE_NAME)
            return

        answer_msg = await channel.fetch_message(payload.message_id)
        log.info("-> Tin nhắn được react: author=%s (bot=%s), content=%s",
                  answer_msg.author, answer_msg.author.bot, answer_msg.content[:80])

        # 5. Không học từ tin nhắn do chính bot gửi
        if answer_msg.author.bot:
            log.info("-> Bỏ qua: tin nhắn được react là tin nhắn hệ thống của bot/APP.")
            return

        # 6. Tin nhắn gốc (câu hỏi) chính là message khởi tạo Thread
        if channel.parent is None:
            log.info("-> Bỏ qua: thread không có parent channel.")
            return
        parent_msg = await channel.parent.fetch_message(channel.id)

        # Tin nhắn khởi tạo Thread là thông báo của bot ("❓ Câu hỏi này..."),
        # câu hỏi thật nằm trong nội dung Thread (dòng "📌 Câu hỏi từ ...").
        # Lấy trực tiếp từ lịch sử thread để chắc chắn đúng câu hỏi gốc.
        raw_question = None
        async for msg in channel.history(oldest_first=True, limit=5):
            if msg.author.bot and "📌" in msg.content:
                # Trích phần câu hỏi ở dòng bắt đầu bằng ">" (blockquote).
                # Bắt buộc anchor đầu dòng để không nhầm với dấu ">" đóng
                # trong mention dạng <@id>.
                match = re.search(r"^>\s*(.+)$", msg.content, flags=re.MULTILINE)
                if match:
                    raw_question = match.group(1).strip()
                break

        if not raw_question:
            # fallback: dùng nội dung tin nhắn khởi tạo thread
            raw_question = parent_msg.content.replace(f"<@{bot.user.id}>", "").strip()

        coach_answer = answer_msg.content.strip()
        log.info("-> Câu hỏi gốc trích được: %s", raw_question[:80] if raw_question else "(rỗng)")

        saved = save_to_cache(raw_question, coach_answer)
        if saved:
            resolve_pending_thread(channel.id)
            await channel.send(
                "💾 **[Hệ thống tự động học]:** Đã ghi nhớ câu trả lời này cho các câu hỏi tương tự sau!"
            )
        else:
            await channel.send("⚠️ Không lưu được — câu trả lời rỗng hoặc không hợp lệ.")

    except discord.NotFound:
        log.warning("Không tìm thấy tin nhắn/kênh khi xử lý reaction (có thể đã bị xoá).")
    except discord.Forbidden:
        log.warning("Bot không có quyền truy cập tin nhắn/kênh này.")
    except Exception as e:
        log.exception("Lỗi khi xử lý reaction học dữ liệu: %s", e)


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
