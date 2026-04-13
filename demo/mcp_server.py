"""업무 도구 MCP 서버 — 일정/이메일/업무/매출 조회 도구를 제공합니다.

MCPStdioTool을 통해 에이전트가 이 서버에 연결하여 도구를 호출합니다.
실행: python demo/mcp_server.py (stdio 전송)

⚠️ 이 서버의 모든 도구는 **시뮬레이션(mock) 데이터**를 반환합니다.
실제 환경에서는 각 함수를 실제 API(Microsoft Graph, Jira, SAP 등)로 교체하세요.
"""

import json
import os
import random
from datetime import datetime

from mcp.server.fastmcp import FastMCP

server = FastMCP("enterprise-tools")

# mock_data.json 로드 (3월~12월 월별 데이터)
_DATA_PATH = os.path.join(os.path.dirname(__file__), "mock_data.json")
with open(_DATA_PATH, encoding="utf-8") as f:
    _MOCK = json.load(f)


def _current_month() -> str:
    """현재 월을 문자열로 반환 (예: '3', '12')"""
    return str(datetime.now().month)


def _get_month_data(category: str, month: str | None = None) -> list | dict:
    """해당 월의 mock 데이터를 반환합니다. 1~2월은 3월 샘플로 대체합니다.

    Args:
        category: 데이터 카테고리 (calendar, emails, tasks, sales)
        month: 월 문자열 (미입력 시 현재 월)

    Returns:
        해당 월의 mock 데이터 (list 또는 dict)
    """
    if month is None:
        month = _current_month()
    return _MOCK[category].get(month, _MOCK[category]["3"])


@server.tool()
def get_calendar_events(date: str = "") -> str:
    """특정 날짜의 일정 목록을 조회합니다.

    Args:
        date: 조회할 날짜 (YYYY-MM-DD 형식, 미입력 시 오늘)
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    # 입력된 날짜에서 월 추출, 해당 월 데이터 조회
    try:
        month = str(int(date.split("-")[1]))
    except (IndexError, ValueError):
        return f"⚠️ 날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요. (입력값: {date})"

    events = _get_month_data("calendar", month)

    lines = [f"📅 {date} 일정:"]
    for ev in events:
        lines.append(f"  • {ev['time']} — {ev['title']}")
    return "\n".join(lines)


@server.tool()
def create_calendar_event(
    title: str, date: str, time: str, duration_minutes: int = 60
) -> str:
    """새 일정을 생성합니다 (시뮬레이션 — 실제 저장되지 않음).

    Args:
        title: 일정 제목
        date: 날짜 (YYYY-MM-DD)
        time: 시작 시간 (HH:MM)
        duration_minutes: 소요 시간(분)
    """
    return (
        f"✅ 일정이 생성되었습니다:\n"
        f"  • 제목: {title}\n"
        f"  • 일시: {date} {time}\n"
        f"  • 소요: {duration_minutes}분"
    )


@server.tool()
def search_emails(query: str, max_results: int = 5) -> str:
    """이메일을 검색합니다.

    Args:
        query: 검색 키워드
        max_results: 최대 결과 수
    """
    if not query.strip():
        return "⚠️ 검색어를 입력해주세요."

    month = _current_month()
    emails = _get_month_data("emails", month)

    results = [
        e
        for e in emails
        if query.lower() in e["subject"].lower()
        or query.lower() in e["preview"].lower()
    ]
    if not results:
        results = emails[:max_results]

    lines = [f"📧 '{query}' 검색 결과 ({len(results[:max_results])}건):"]
    for e in results[:max_results]:
        lines.append(f"  • [{e['date']}] {e['from']}")
        lines.append(f"    제목: {e['subject']}")
        lines.append(f"    미리보기: {e['preview'][:60]}...")
    return "\n".join(lines)


@server.tool()
def get_tasks(status: str = "all") -> str:
    """업무(태스크) 목록을 조회합니다.

    Args:
        status: 필터 (all, pending, in_progress, done)
    """
    month = _current_month()
    tasks = _get_month_data("tasks", month)

    if status != "all":
        tasks = [t for t in tasks if t["status"] == status]

    status_emoji = {"pending": "⏳", "in_progress": "🔄", "done": "✅"}
    lines = [f"📋 업무 목록 (필터: {status}):"]
    for t in tasks:
        emoji = status_emoji.get(t["status"], "📌")
        lines.append(f"  {emoji} [{t['id']}] {t['title']}")
        lines.append(
            f"     우선순위: {t['priority']} | 마감: {t['due']} | 상태: {t['status']}"
        )
    return "\n".join(lines)


@server.tool()
def create_task(title: str, priority: str = "보통", due_date: str = "") -> str:
    """새 업무(태스크)를 생성합니다 (시뮬레이션).

    Args:
        title: 업무 제목
        priority: 우선순위 (높음, 보통, 낮음)
        due_date: 마감일 (YYYY-MM-DD)
    """
    valid_priorities = ("높음", "보통", "낮음")
    if priority not in valid_priorities:
        return f"⚠️ 우선순위는 {', '.join(valid_priorities)} 중 하나여야 합니다. (입력값: {priority})"
    task_id = f"T-{random.randint(200, 999)}"
    return (
        f"✅ 업무가 생성되었습니다:\n"
        f"  • ID: {task_id}\n"
        f"  • 제목: {title}\n"
        f"  • 우선순위: {priority}\n"
        f"  • 마감일: {due_date or '미정'}"
    )


@server.tool()
def query_sales_data(period: str = "monthly", product: str = "") -> str:
    """매출 데이터를 조회합니다.

    현재 mock 데이터는 월별(monthly) 집계만 지원합니다.
    period 값은 응답 헤더에 표시되지만, 실제 데이터 집계 단위는 월별로 고정됩니다.

    Args:
        period: 조회 기간 (daily, weekly, monthly, quarterly)
        product: 제품명 필터 (미입력 시 전체)
    """
    month = _current_month()
    sales = _get_month_data("sales", month)

    if product:
        sales = {k: v for k, v in sales.items() if product in k}

    total_value = sum(v["amount"] for v in sales.values())
    total_억 = int(total_value)
    total_만 = round((total_value - total_억) * 10000)
    total = f"{total_억}억 {total_만:,}만원"

    lines = [f"💰 매출 현황 ({period}):"]
    for name, info in sales.items():
        억 = int(info["amount"])
        만 = round((info["amount"] - 억) * 10000)
        amount_str = f"{억}억 {만:,}만원"
        lines.append(
            f"  • {name}: {amount_str} ({info['change']}, {info['count']}건)"
        )
    lines.append(f"\n  📊 총 매출: {total}")
    return "\n".join(lines)


if __name__ == "__main__":
    server.run(transport="stdio")
