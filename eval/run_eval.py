"""Chạy golden-set eval cho luồng truy xuất thông báo của ViniBot.

Script không kết nối Discord và không gửi tin nhắn. Nó dùng record cố định trong
golden_set.json, gọi model đang cấu hình qua OpenRouter, sau đó dùng chính lớp
xác thực/fallback của bot để chấm nguồn và dữ kiện.
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime
import json
import os
from pathlib import Path
import sys
from typing import Any

from dotenv import load_dotenv


EVAL_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EVAL_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

# Eval không đăng nhập Discord nhưng bot.py cần biến này khi import.
os.environ.setdefault("DISCORD_TOKEN", "eval-only-not-used")

if not os.getenv("OPENROUTER_API_KEY"):
    raise RuntimeError(
        "Thiếu OPENROUTER_API_KEY trong .env; không thể chạy live eval."
    )

import bot  # noqa: E402  (cần nạp .env và PROJECT_ROOT trước)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Đánh giá retrieval và grounding của ViniBot."
    )
    parser.add_argument(
        "--golden-set",
        type=Path,
        default=EVAL_DIR / "golden_set.json",
    )
    parser.add_argument(
        "--raw-output",
        type=Path,
        default=EVAL_DIR / "raw_results.json",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=EVAL_DIR / "results.md",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
        raise ValueError("golden_set.json phải chứa object có mảng cases.")

    return data


def normalize_record(record: dict[str, Any]) -> dict[str, object]:
    normalized: dict[str, object] = dict(record)
    normalized.setdefault("author", "Eval fixture")
    normalized.setdefault("edited_at_utc_plus_7", None)
    normalized.setdefault("mentions_everyone_or_here", False)
    normalized.setdefault("mentioned_roles", [])
    normalized.setdefault("attachments", [])
    normalized.setdefault("facts_to_copy_exactly", [])
    normalized.setdefault("logistics_evidence", [])
    return normalized


def filter_official_records(
    records: list[dict[str, Any]],
    suite: dict[str, Any],
) -> list[dict[str, object]]:
    official_channels = set(suite.get("official_channels", []))
    official_roles = set(suite.get("official_roles", []))
    return [
        normalize_record(record)
        for record in records
        if (
            record.get("source_channel") in official_channels
            and record.get("official_role") in official_roles
        )
    ]


def make_context(records: list[dict[str, object]]) -> bot.StaffSummaryContext:
    return bot.StaffSummaryContext(
        archive="\n".join(
            json.dumps(record, ensure_ascii=False)
            for record in records
        ),
        candidate_count=len(records),
        scanned_channels=("thông-báo-chung",),
        unreadable_channels=(),
        history_truncated=False,
        context_truncated=False,
        status_message=(
            "Không tìm thấy thông báo chính thức phù hợp trong golden set."
        ),
    )


def prepare_candidates(
    case: dict[str, Any],
    suite: dict[str, Any],
) -> tuple[list[dict[str, object]], list[str]]:
    official_records = filter_official_records(case["messages"], suite)
    official_ids = [str(record["message_id"]) for record in official_records]
    context = make_context(official_records)
    mode = case.get("mode", "daily_summary")

    if mode == "latest_announcements":
        context = bot.select_latest_announcements(
            context,
            int(case.get("latest_count", 1)),
        )
    else:
        context = bot.filter_daily_logistics_context(context)

    return bot.parse_context_records(context), official_ids


def build_model_messages(
    case: dict[str, Any],
    candidates: list[dict[str, object]],
) -> list[dict[str, str]]:
    mode = str(case.get("mode", "daily_summary"))
    system_prompt = (
        "Bạn là ViniBot, trợ lý logistics cho học viên. Các record đầu vào đã "
        "được code lọc theo đúng kênh, role chính thức và tín hiệu logistics. "
        "Hãy trả lời đúng câu hỏi bằng tiếng Việt, ngắn gọn, không suy đoán. "
        "Chỉ các deadline, thời gian, ngày và URL trong facts_to_copy_exactly "
        "được dùng và phải sao chép nguyên văn. Nếu có cập nhật mới hơn, ưu "
        "tiên cập nhật mới. Không viết nguồn Discord trong answer. Chỉ trả một "
        "JSON object theo schema "
        '{"answer":"câu trả lời","selected_message_ids":["id"]}. '
        "selected_message_ids chỉ chứa ID của record thực sự dùng để trả lời. "
    )

    if mode in {"daily_summary", "latest_announcements"}:
        system_prompt += (
            "Phải tóm tắt các record được cung cấp và đưa ID của mọi record "
            "được dùng vào selected_message_ids; không được nói không có dữ "
            "liệu khi danh sách record không rỗng."
        )
    else:
        system_prompt += (
            "Nếu record không trả lời được câu hỏi, answer phải nói không tìm "
            "thấy và selected_message_ids phải rỗng."
        )

    user_prompt = (
        f"Câu hỏi: {case['question']}\n"
        f"Chế độ: {mode}\n\n"
        "RECORDS:\n"
        + "\n".join(
            json.dumps(record, ensure_ascii=False)
            for record in candidates
        )
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


async def call_model(
    case: dict[str, Any],
    candidates: list[dict[str, object]],
) -> tuple[str, dict[str, object]]:
    try:
        response = await bot.ai_client.chat.completions.create(
            model=bot.OPENROUTER_MODEL,
            messages=build_model_messages(case, candidates),
            temperature=0.1,
            max_tokens=600,
            response_format={"type": "json_object"},
        )
    except Exception as error:
        return "", {
            "answer": "",
            "selected_message_ids": [],
            "_request_error": f"{type(error).__name__}: {error}",
        }

    raw_output = response.choices[0].message.content or ""

    try:
        model_result = bot.parse_model_json(raw_output)
    except (json.JSONDecodeError, ValueError) as error:
        model_result = {
            "answer": "",
            "selected_message_ids": [],
            "_parse_error": f"{type(error).__name__}: {error}",
        }

    return raw_output, model_result


def answer_without_sources(answer: str) -> str:
    return answer.split("\n\n**Nguồn đã xác thực**", 1)[0].strip()


def contains_no_data_phrase(answer: str) -> bool:
    normalized = bot.normalize_search_text(answer)
    return any(
        phrase in normalized
        for phrase in (
            "khong tim thay",
            "khong co thong bao",
            "khong co du lieu",
        )
    )


def evaluate_run(
    case: dict[str, Any],
    candidates: list[dict[str, object]],
    official_ids: list[str],
    raw_model_output: str,
    model_result: dict[str, object],
) -> dict[str, Any]:
    expected = case.get("expected", {})
    require_selection = case.get("mode") in {
        "daily_summary",
        "latest_announcements",
    }
    grounded = bot.finalize_grounded_answer(
        model_result,
        candidates,
        require_selection=require_selection,
    )
    selected_ids = list(grounded.selected_message_ids)
    answer_body = answer_without_sources(grounded.answer)
    expected_ids = [str(item) for item in expected.get("selected_message_ids", [])]
    forbidden_ids = [str(item) for item in expected.get("forbidden_message_ids", [])]
    required_facts = [str(item) for item in expected.get("required_facts", [])]
    forbidden_facts = [str(item) for item in expected.get("forbidden_facts", [])]
    required_terms = [str(item) for item in expected.get("required_terms", [])]
    expect_no_data = bool(expected.get("expect_no_data", False))

    selected_by_id = {
        str(record["message_id"]): record
        for record in candidates
        if str(record["message_id"]) in selected_ids
    }
    allowed_facts = {
        str(fact)
        for record in selected_by_id.values()
        for fact in record.get("facts_to_copy_exactly", [])
    }
    answer_facts = set(bot.extract_exact_facts(answer_body))
    unexpected_facts = sorted(answer_facts - allowed_facts)

    checks = {
        "selected_ids_match": selected_ids == expected_ids,
        "forbidden_ids_absent": not (set(selected_ids) & set(forbidden_ids)),
        "selected_ids_are_official": set(selected_ids).issubset(set(official_ids)),
        "required_facts_present": all(
            fact in answer_body
            for fact in required_facts
        ),
        "forbidden_facts_absent": all(
            fact not in answer_body
            for fact in forbidden_facts
        ),
        "required_terms_present": all(
            bot.normalize_search_text(term)
            in bot.normalize_search_text(answer_body)
            for term in required_terms
        ),
        "no_unexpected_facts": not unexpected_facts,
        "no_data_behavior": (
            contains_no_data_phrase(answer_body)
            if expect_no_data
            else not contains_no_data_phrase(answer_body)
        ),
    }

    return {
        "raw_model_output": raw_model_output,
        "model_result": model_result,
        "final_answer": grounded.answer,
        "selected_message_ids": selected_ids,
        "allowed_facts": sorted(allowed_facts),
        "answer_facts": sorted(answer_facts),
        "unexpected_facts": unexpected_facts,
        "checks": checks,
        "passed": all(checks.values()),
    }


async def evaluate_case(
    case: dict[str, Any],
    suite: dict[str, Any],
) -> dict[str, Any]:
    candidates, official_ids = prepare_candidates(case, suite)
    requested_runs = max(1, int(case.get("runs", 1)))
    run_results: list[dict[str, Any]] = []

    for _ in range(requested_runs):
        if candidates:
            raw_output, model_result = await call_model(case, candidates)
        else:
            raw_output = ""
            model_result = {
                "answer": "Không tìm thấy thông báo chính thức phù hợp.",
                "selected_message_ids": [],
            }

        run_results.append(
            evaluate_run(
                case,
                candidates,
                official_ids,
                raw_output,
                model_result,
            )
        )

    selections = {
        tuple(result["selected_message_ids"])
        for result in run_results
    }
    stable_selection = len(selections) == 1
    stable_checks = all(result["passed"] for result in run_results)

    return {
        "id": case["id"],
        "question": case["question"],
        "mode": case.get("mode", "daily_summary"),
        "tags": case.get("tags", []),
        "official_candidate_ids": official_ids,
        "logistics_candidate_ids": [
            str(record["message_id"])
            for record in candidates
        ],
        "runs": run_results,
        "stability": {
            "selection_stable": stable_selection,
            "all_runs_passed": stable_checks,
        },
        "passed": stable_selection and stable_checks,
    }


def metric_for_tag(results: list[dict[str, Any]], tag: str) -> tuple[int, int]:
    matching = [result for result in results if tag in result["tags"]]
    return sum(bool(result["passed"]) for result in matching), len(matching)


def metric_label(metric: tuple[int, int]) -> str:
    passed, total = metric

    if total == 0:
        return "Chưa có case"

    return f"{'Đạt' if passed == total else 'Chưa đạt'} ({passed}/{total} case)"


def build_report(payload: dict[str, Any]) -> str:
    results = payload["cases"]
    passed_cases = sum(bool(result["passed"]) for result in results)
    total_cases = len(results)
    official_metric = metric_for_tag(results, "official_source")
    noise_metric = metric_for_tag(results, "noise_filter")
    latest_metric = metric_for_tag(results, "latest_update")
    fact_metric = metric_for_tag(results, "fact_grounding")
    no_data_metric = metric_for_tag(results, "no_data")
    stability_metric = metric_for_tag(results, "stability")

    lines = [
        "# Kết quả đánh giá ViniBot",
        "",
        f"- Thời điểm chạy: `{payload['generated_at']}`",
        f"- Model: `{payload['model']}` qua OpenRouter",
        f"- Golden set: `{payload['suite_name']}` v{payload['suite_version']}",
        f"- Tổng kết: **{passed_cases}/{total_cases} case đạt**",
        "",
        "## Kết quả từng case",
        "",
        "| Case | Chế độ | Số lần chạy | Kết quả | ID nguồn ổn định |",
        "|---|---|---:|---|---|",
    ]

    for result in results:
        lines.append(
            "| {id} | {mode} | {runs} | {status} | {stable} |".format(
                id=result["id"],
                mode=result["mode"],
                runs=len(result["runs"]),
                status="Đạt" if result["passed"] else "Chưa đạt",
                stable=(
                    "Có"
                    if result["stability"]["selection_stable"]
                    else "Không"
                ),
            )
        )

    lines.extend(
        [
            "",
            "## Trả lời các câu hỏi đánh giá",
            "",
            "### Bot có lấy đúng thông báo chính thức không?",
            "",
            f"**{metric_label(official_metric)}.** Case kiểm tra trộn tin từ "
            "ADMIN, LEARNER và kênh không chính thức; chỉ ID thuộc role và kênh "
            "chính thức được phép xuất hiện trong kết quả.",
            "",
            "### Có bỏ qua chat linh tinh không?",
            "",
            f"**{metric_label(noise_metric)}.** Tin cảm ơn của staff, kể cả có "
            "ping mọi người, không được coi là thông báo nếu thiếu tín hiệu "
            "logistics.",
            "",
            "### Có dùng thông báo mới nhất thay cho thông báo cũ không?",
            "",
            f"**{metric_label(latest_metric)}.** Case Workshop có bản 18:00 và "
            "bản cập nhật mới hơn sang 20:00; eval yêu cầu chỉ dùng message ID "
            "của bản cập nhật.",
            "",
            "### Có bịa deadline, link hoặc thời gian không?",
            "",
            f"**{metric_label(fact_metric)}.** Runner so khớp nguyên văn các "
            "facts bắt buộc, cấm facts đã khai báo sai và đánh dấu mọi thời "
            "gian/ngày/URL không có trong nguồn đã chọn là unexpected_facts.",
            "",
            "### Khi không có dữ liệu, bot có biết nói “không tìm thấy” không?",
            "",
            f"**{metric_label(no_data_metric)}.** Case không dữ liệu chỉ chứa "
            "tin đồn của learner và chat thường của staff; kết quả phải có thông "
            "điệp không tìm thấy và không có source ID.",
            "",
            "### Kết quả có ổn định qua nhiều lần chạy không?",
            "",
            f"**{metric_label(stability_metric)}.** Case stability được gọi 3 "
            "lần. Tiêu chí ổn định là cùng tập message ID đã xác thực và mọi "
            "lần đều qua kiểm tra facts; cách diễn đạt có thể khác nhau.",
            "",
            "## Chạy lại",
            "",
            "```powershell",
            ".\\.venv\\Scripts\\python.exe eval\\run_eval.py",
            "```",
            "",
            "Kết quả chi tiết từng lần gọi model nằm trong `raw_results.json`. "
            "File này không chứa API key hoặc Discord token.",
        ]
    )
    return "\n".join(lines) + "\n"


async def async_main(args: argparse.Namespace) -> dict[str, Any]:
    suite = load_json(args.golden_set)
    case_results = []

    for case in suite["cases"]:
        print(f"Running {case['id']}...")
        case_results.append(await evaluate_case(case, suite))

    return {
        "suite_name": suite.get("suite_name", "ViniBot eval"),
        "suite_version": suite.get("version", 1),
        "generated_at": datetime.now(bot.VIETNAM_TIMEZONE).isoformat(),
        "model": bot.OPENROUTER_MODEL,
        "cases": case_results,
        "summary": {
            "passed_cases": sum(
                bool(result["passed"])
                for result in case_results
            ),
            "total_cases": len(case_results),
        },
    }


def main() -> None:
    args = parse_args()
    payload = asyncio.run(async_main(args))
    args.raw_output.parent.mkdir(parents=True, exist_ok=True)
    args.raw_output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    args.report.write_text(build_report(payload), encoding="utf-8")
    passed = payload["summary"]["passed_cases"]
    total = payload["summary"]["total_cases"]
    print(f"Completed: {passed}/{total} cases passed.")
    print(f"Raw: {args.raw_output}")
    print(f"Report: {args.report}")


if __name__ == "__main__":
    main()
