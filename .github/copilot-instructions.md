# 프로젝트 글로벌 인스트럭션

<!-- 🔒 프로젝트 전용: 이 프로젝트(foundry-agent-x-github-copilot)에만 해당하는 규칙입니다. 다른 프로젝트에 복사하지 마세요. -->

> 공통 규칙(Python 컨벤션, Azure 인증, 한국어 작성)은 `.github/instructions/` 아래 파일에서 관리합니다.
> 이 파일에는 **이 프로젝트에만 해당하는 규칙**을 작성합니다.

## 프로젝트 개요

이 프로젝트는 **Microsoft Foundry** 기반 엔터프라이즈 AI 데모로,
일반 기업 환경에서 가장 많이 사용되는 3가지 시나리오를 실제 기술 스택으로 구현합니다:

1. **사내 문서 Q&A (RAG)** — Foundry IQ(Knowledge Base) 기반 문서 검색
2. **업무 도구 에이전트 (MCP)** — MCPStdioTool로 MCP 서버에 연결하여 도구 호출
3. **멀티 에이전트 워크플로우** — WorkflowBuilder + AgentExecutor + Switch 라우팅 (RAG / TOOL / BOTH 순차 파이프라인)

## 기술 스택

- **UI**: Streamlit
- **AI Framework**: Microsoft Agent Framework (`agent-framework-core`, `agent-framework-azure-ai`, `agent-framework-azure-ai-search`)
- **RAG**: `agent-framework-azure-ai-search` → `AzureAISearchContextProvider` (Foundry IQ)
- **MCP**: `MCPStdioTool` → `mcp_server.py` (FastMCP, stdio 전송)
- **멀티 에이전트**: `WorkflowBuilder` + `AgentExecutor` + `Case`/`Default` → `WorkflowAgent`
  - RAG/TOOL 단독 경로 + BOTH 순차 파이프라인 (`add_chain`으로 RAG → Tool → Summarizer)
- **인증**: `azure-identity` → `DefaultAzureCredential`
- **모델**: Azure AI Foundry 배포 모델 (기본 `gpt-4.1`)
- **환경변수**: `python-dotenv`

## 프로젝트 코드 패턴

- 코드 생성 시 이 프로젝트의 기존 패턴을 따른다:
  - AI 클라이언트는 `AzureAIAgentClient`로 생성 (`credential` 사용)
  - 에이전트는 `Agent`로 생성 (`client`, `tools` 리스트, `context_providers` 리스트 전달)
  - RAG는 `AzureAISearchContextProvider`를 `context_providers` 리스트에 전달
  - RAG Knowledge Base 연동은 `KNOWLEDGE_BASE_NAME`을 `AzureAISearchContextProvider(knowledge_base_name=...)`에 직접 전달
  - MCP 도구는 `MCPStdioTool`을 `tools` 리스트에 전달
  - 멀티 에이전트는 `WorkflowBuilder` + `AgentExecutor` + `WorkflowAgent`로 구성
  - BOTH 경로는 `add_chain([rag, tool, summarizer])`로 순차 파이프라인 구성
- MCP 서버는 `demo/mcp_server.py`에 `FastMCP`로 정의하고 stdio 전송을 사용한다.
- Mock 데이터는 `demo/mock_data.json`에 3월~12월 월별 데이터로 관리한다.
- 새 기능 추가 시 기존 `demo/` 디렉토리 구조를 유지한다.

## Streamlit 캐싱 규칙

- 단일 에이전트 생성 함수(`create_rag_agent`, `create_tool_agent`)에는 `@st.cache_resource`를 적용하여 재실행 시 재생성을 방지한다.
- 이벤트 루프, 클라이언트 등 **프로세스 수명 동안 유지해야 하는 리소스**에만 사용한다.
- **`WorkflowAgent`(`create_workflow_agent`)에는 `@st.cache_resource`를 사용하지 않는다.** `WorkflowAgent`는 내부 실행 상태를 추적하므로, 캐시된 인스턴스를 재사용하면 "Concurrent executions are not allowed" 오류가 발생한다. 매 요청마다 새 인스턴스를 생성한다.
- 요청마다 달라지는 입력값이 있는 함수에는 사용하지 않는다.

## SDK Import 경로 매핑

코드 생성 시 다음 import 경로를 정확히 사용한다:

```python
# Agent Framework 핵심 클래스
from agent_framework import (
    Agent,              # 에이전트 생성
    AgentExecutor,      # 워크플로우에서 에이전트 래핑
    Case,               # Switch 라우팅 조건
    Default,            # Switch 기본 경로
    MCPStdioTool,       # MCP 서버 연결 (stdio)
    WorkflowAgent,      # 워크플로우를 에이전트처럼 실행
    WorkflowBuilder,    # 워크플로우 그래프 빌더
)

# Azure AI Search (RAG) 컨텍스트 프로바이더
from agent_framework.azure import AzureAISearchContextProvider

# Azure AI 클라이언트
from agent_framework_azure_ai import AzureAIAgentClient
```

## WorkflowBuilder API 사용법

멀티 에이전트 워크플로우는 다음 API 조합으로 구성한다:

```python
# 1. 각 에이전트를 AgentExecutor로 래핑 (id 필수)
classifier_exec = AgentExecutor(agent=classifier, id="classifier")
rag_exec = AgentExecutor(agent=rag_sub, id="rag")
tool_exec = AgentExecutor(agent=tool_sub, id="tool")

# 2. 조건 함수 정의 (AgentExecutorResponse → bool)
def is_rag(response) -> bool:
    return response.agent_response.text.strip().upper() == "RAG"

def is_both(response) -> bool:
    return response.agent_response.text.strip().upper() == "BOTH"

# 3. WorkflowBuilder로 그래프 구성
workflow = (
    WorkflowBuilder(start_executor=classifier_exec)
    .add_switch_case_edge_group(
        source=classifier_exec,
        cases=[
            Case(condition=is_rag, target=rag_exec),
            Case(condition=is_both, target=rag_both_exec),
            Default(target=tool_exec),         # 나머지는 TOOL로
        ],
    )
    # BOTH 경로: 순차 파이프라인 (RAG → Tool → Summarizer)
    .add_chain([rag_both_exec, tool_both_exec, summarizer_exec])
    .build()
)

# 4. WorkflowAgent로 최종 래핑
agent = WorkflowAgent(workflow=workflow, name="...", description="...")
```

## 비동기/스트리밍 패턴

Streamlit은 동기 환경이므로, Agent Framework의 비동기 API를 호출할 때 다음 패턴을 사용한다:

1. **공유 이벤트 루프**: `@st.cache_resource`로 백그라운드 데몬 스레드에서 `asyncio` 이벤트 루프를 하나 생성하고 앱 전체에서 공유한다.
2. **스트리밍 실행**: `agent.run(prompt, stream=True)`로 토큰 단위 스트리밍을 사용한다. 비동기 스트림을 `queue.Queue`로 동기 제너레이터로 변환하고, `st.write_stream()`으로 실시간 표시한다.
3. **`asyncio.run()` 사용 금지**: Streamlit 메인 스레드에서 `asyncio.run()`을 호출하면 이벤트 루프 충돌이 발생하므로 사용하지 않는다.

### 스트리밍 구현 코드

```python
import queue as queue_mod

def stream_agent(agent, prompt: str):
    """에이전트를 스트리밍으로 실행 (Streamlit write_stream 호환)."""
    q = queue_mod.Queue()
    sentinel = object()

    async def _run():
        try:
            stream = agent.run(prompt, stream=True)
            async for update in stream:
                if update.text:
                    q.put(update.text)
        except Exception as e:
            q.put(e)
        finally:
            q.put(sentinel)

    loop = _get_event_loop()             # 캐시된 백그라운드 루프
    asyncio.run_coroutine_threadsafe(_run(), loop)

    while True:
        item = q.get(timeout=120)
        if item is sentinel:
            break
        if isinstance(item, Exception):
            raise item
        yield item
```

## Mock 데이터 스키마 (`demo/mock_data.json`)

3월~12월(키: `"3"`~`"12"`) 월별 데이터로 관리한다. 최상위 키 4개:

```jsonc
{
  "calendar": {
    "3": [{"time": "09:00", "title": "팀 스탠드업 미팅"}],
    // ... 월별 5개 항목 (list of {time, title})
  },
  "emails": {
    "3": [{"from": "김부장 <kim@company.com>", "subject": "...", "date": "2026-03-27", "preview": "..."}],
    // ... 월별 (list of {from, subject, date, preview})
  },
  "tasks": {
    "3": [{"id": "T-301", "title": "...", "status": "in_progress", "priority": "높음", "due": "2026-03-29"}],
    // ... 월별 (list of {id, title, status, priority, due})
    // status: "pending" | "in_progress" | "done"
  },
  "sales": {
    "3": {"엔터프라이즈 라이선스": {"amount": 12.34, "change": "+8.2%", "count": 45}, ...},
    // ... 월별 (dict of 제품명 → {amount(억 단위), change, count})
    // 제품 카테고리: 엔터프라이즈 라이선스, 클라우드 서비스, 기술 컨설팅, 교육/트레이닝
  }
}
```

## Streamlit UI 구조

### 전체 레이아웃
- `st.set_page_config(page_title="Enterprise AI Demo", page_icon="🏢", layout="wide")`
- 사이드바에 시나리오 선택 (`st.radio`), 아키텍처 다이어그램 (ASCII art)
- 메인 영역에 채팅 인터페이스 (시나리오별 분기)

### 시나리오별 UI 분기 패턴
```python
# 시나리오별 설정값을 변수로 분리
if "📄" in scenario:
    agent_key = "rag"
    agent_factory = create_rag_agent
    example_qs = ["연차 휴가 규정 알려줘", ...]
elif "🔧" in scenario:
    agent_key = "tool"
    agent_factory = create_tool_agent
    example_qs = ["오늘 일정 알려줘", ...]
else:
    agent_key = "orch"
    agent_factory = create_workflow_agent
    example_qs = ["연차 규정 알려줘", "오늘 일정 보여줘", ...]
```

### 채팅 인터페이스 패턴
- **세션 상태**: `st.session_state[f"history_{agent_key}"]`에 `[{"role": "user"|"assistant", "content": "..."}]` 저장
- **예시 질문**: `st.columns()` + `st.button()`으로 가로 배치 → 클릭 시 `st.session_state[f"pending_{agent_key}"]`에 저장
- **입력**: `st.chat_input("질문을 입력하세요...")`
- **표시**: `st.chat_message(role)` 컨텍스트에서 `st.markdown()` 사용
- **스트리밍 표시**: `st.empty()`로 placeholder 생성 → chunk를 누적하며 `placeholder.markdown("".join(chunks))`로 실시간 갱신
- **에러**: `st.error()`로 표시 후 히스토리에도 기록

## MCP 도구 작성 규칙

- `demo/mcp_server.py`에 `@server.tool()` 데코레이터로 정의한다.
- 파라미터에 타입 힌트와 기본값을 명시한다.
- 시스템 경계 입력(사용자로부터 전달되는 `query`, `keyword` 등)은 빈 문자열·범위 초과를 검증한다.
- 반환값은 `str` 타입의 한국어 텍스트로 통일한다.
