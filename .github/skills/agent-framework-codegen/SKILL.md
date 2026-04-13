---
name: agent-framework-codegen
description: "Microsoft Agent Framework SDK를 사용한 AI 에이전트·워크플로우 코드 생성. USE FOR: Agent Framework 코드 생성, 에이전트 추가, 워크플로우 구성, MCP 도구 연동, RAG 설정, Streamlit 비동기 통합, Foundry Agent v2 패턴. DO NOT USE FOR: Azure 배포(azure-deploy 사용), Foundry 리소스 관리(microsoft-foundry 사용)."
---

# Microsoft Agent Framework 코드 생성 스킬

이 프로젝트에서 Microsoft Agent Framework SDK로 에이전트·워크플로우를 작성할 때 따라야 하는 상세 패턴과 레퍼런스입니다.

---

## 1. SDK Import 경로

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

> **주의**: `agent_framework` / `agent_framework.azure` / `agent_framework_azure_ai`는 각각 별도 패키지. 경로를 혼동하지 않는다.

---

## 2. 에이전트 생성 패턴

### 2-1. AI 클라이언트

```python
from azure.identity.aio import DefaultAzureCredential

client = AzureAIAgentClient(
    project_endpoint=PROJECT_ENDPOINT,
    model_deployment_name=MODEL,       # 예: "gpt-4.1"
    credential=DefaultAzureCredential(),
)
```

- 비동기 `DefaultAzureCredential` 사용 (`azure.identity.aio`)
- 클라이언트는 앱 수명 동안 한 번만 생성 (Streamlit에서는 `@st.cache_resource`)

### 2-2. 기본 에이전트

```python
agent = Agent(
    client=client,
    name="my-agent",
    instructions="에이전트 역할 지시문...",
    tools=[...],                # MCPStdioTool 리스트 (선택)
    context_providers=[...],    # AzureAISearchContextProvider 리스트 (선택)
)
```

### 2-3. RAG 에이전트 (Foundry IQ)

```python
kb_provider = AzureAISearchContextProvider(
    knowledge_base_name=KNOWLEDGE_BASE_NAME,  # Foundry IQ KB 이름
    credential=DefaultAzureCredential(),
    mode="agentic",
    top_k=3,
    retrieval_reasoning_effort="low",
)

rag_agent = Agent(
    client=client,
    name="rag-agent",
    instructions="...",
    context_providers=[kb_provider],
)
```

### 2-4. MCP 도구 에이전트

```python
mcp_tool = MCPStdioTool(
    name="enterprise-tools",
    command=sys.executable,         # Python 인터프리터 경로
    args=["demo/mcp_server.py"],    # MCP 서버 스크립트 경로
    description="도구 설명...",
)

tool_agent = Agent(
    client=client,
    name="tool-agent",
    instructions="...",
    tools=[mcp_tool],
)
```

---

## 3. 멀티 에이전트 워크플로우 (WorkflowBuilder)

### 3-1. 전체 구성 흐름

```
분류기(Classifier) → Switch 라우팅
  ├─ RAG  → RAG 에이전트 (종료)
  ├─ TOOL → MCP 도구 에이전트 (종료)
  └─ BOTH → RAG(both) → Tool(both) → Summarizer (순차 파이프라인)
```

### 3-2. 코드 예제

```python
# 1. 각 에이전트를 AgentExecutor로 래핑 (id 필수)
classifier_exec = AgentExecutor(agent=classifier, id="classifier")
rag_exec = AgentExecutor(agent=rag_sub, id="rag")
tool_exec = AgentExecutor(agent=tool_sub, id="tool")

# BOTH 체인 전용 Executor (단독 경로와 별도 인스턴스)
rag_both_exec = AgentExecutor(agent=rag_both, id="rag-both")
tool_both_exec = AgentExecutor(agent=tool_both, id="tool-both")
summarizer_exec = AgentExecutor(agent=summarizer, id="summarizer")

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
            Default(target=tool_exec),
        ],
    )
    .add_chain([rag_both_exec, tool_both_exec, summarizer_exec])
    .build()
)

# 4. WorkflowAgent로 최종 래핑
agent = WorkflowAgent(
    workflow=workflow,
    name="multi-agent-workflow",
    description="...",
)
```

### 3-3. WorkflowBuilder API 요약

| 메서드 | 용도 |
|--------|------|
| `WorkflowBuilder(start_executor=...)` | 시작 노드 지정 |
| `.add_switch_case_edge_group(source, cases=[...])` | Switch 라우팅 (Case + Default) |
| `.add_chain([exec1, exec2, ...])` | 순차 파이프라인 |
| `.build()` | Workflow 객체 생성 |
| `WorkflowAgent(workflow=..., name=..., description=...)` | 워크플로우를 에이전트 인터페이스로 래핑 |

### 3-4. BOTH 경로: 에이전트 분리 원칙

- 단독 경로(RAG/TOOL)용 에이전트와 BOTH 체인용 에이전트는 **별도 인스턴스**로 생성
- BOTH 체인 에이전트의 instructions에는 역할 범위 제한을 명시:
  - RAG(both): "도구 호출이 필요한 부분은 답변하지 마세요"
  - Tool(both): "문서 검색은 하지 마세요 (이미 처리됨)"
  - Summarizer: "두 결과를 통합하여 하나의 일관된 답변 제공"

---

## 4. Streamlit 비동기 통합

### 4-1. 핵심 원칙

- **`asyncio.run()` 사용 금지** — Streamlit 메인 스레드에서 호출 시 이벤트 루프 충돌
- **공유 이벤트 루프** — 백그라운드 데몬 스레드 하나에 루프를 만들고 앱 전체에서 공유
- **`asyncio.run_coroutine_threadsafe()`** — 공유 루프에 코루틴을 제출

### 4-2. 이벤트 루프 생성

```python
import asyncio
import threading
import streamlit as st

@st.cache_resource
def _get_event_loop():
    """단일 이벤트 루프를 백그라운드 스레드에서 유지합니다."""
    loop = asyncio.new_event_loop()
    t = threading.Thread(target=loop.run_forever, daemon=True)
    t.start()
    return loop
```

### 4-3. 스트리밍 실행 (write_stream 호환)

```python
import queue

def stream_agent(agent, prompt: str):
    """에이전트를 스트리밍으로 실행 (Streamlit write_stream 호환)."""
    q = queue.Queue()
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

    loop = _get_event_loop()
    asyncio.run_coroutine_threadsafe(_run(), loop)

    while True:
        item = q.get(timeout=120)
        if item is sentinel:
            break
        if isinstance(item, Exception):
            raise item
        yield item
```

### 4-4. Streamlit 캐싱 규칙

| 대상 | `@st.cache_resource` | 이유 |
|------|:---:|------|
| `_get_event_loop()` | ✅ | 프로세스 수명 동안 유지 |
| `get_ai_client()` | ✅ | 싱글턴 |
| `create_rag_agent()` | ✅ | 상태 없음, 재생성 비용 절약 |
| `create_tool_agent()` | ✅ | 상태 없음, 재생성 비용 절약 |
| `create_workflow_agent()` | ❌ | 내부 실행 상태 추적 → 캐시 시 "Concurrent executions are not allowed" 오류 |

---

## 5. MCP 도구 서버 작성 규칙

`demo/mcp_server.py` 에 FastMCP로 정의:

```python
from mcp.server.fastmcp import FastMCP

server = FastMCP("enterprise-tools")

@server.tool()
def my_tool(param: str, count: int = 5) -> str:
    """도구 설명 (docstring이 MCP 도구 설명으로 노출됨).

    Args:
        param: 파라미터 설명
        count: 결과 수 (기본값 5)
    """
    # 입력 검증 (시스템 경계)
    if not param.strip():
        return "⚠️ 검색어를 입력해주세요."

    # 비즈니스 로직
    return "결과 텍스트 (한국어)"

if __name__ == "__main__":
    server.run(transport="stdio")
```

### 체크리스트
- `@server.tool()` 데코레이터 사용
- 파라미터에 타입 힌트 + 기본값 명시
- 시스템 경계 입력(`query`, `keyword` 등)에 빈 문자열·범위 초과 검증
- 반환값은 `str` (한국어)
- Mock 데이터는 `demo/mock_data.json`에서 로드

---

## 6. 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| "Concurrent executions are not allowed" | `WorkflowAgent`를 `@st.cache_resource`로 캐시 | 캐시 제거, 매 요청마다 새 인스턴스 |
| "There is no current event loop in thread" | Streamlit에서 `asyncio.run()` 호출 | `run_coroutine_threadsafe` + 공유 루프 사용 |
| MCP 도구 호출 실패 (timeout) | `mcp_server.py` 경로 오류 또는 Python 경로 | `sys.executable` + `os.path.join(os.path.dirname(__file__), ...)` 사용 |
| RAG 에이전트가 "문서를 찾을 수 없습니다" 반복 | `KNOWLEDGE_BASE_NAME` 미설정 또는 KB 미생성 | `.env`에서 확인, Foundry IQ에서 KB 생성 여부 확인 |
| BOTH 경로에서 Summarizer가 분류 결과만 요약 | 서브 에이전트 instructions에 "분류 결과 무시" 미명시 | instructions에 "이전 메시지의 분류 결과(RAG/TOOL/BOTH)는 무시하세요" 추가 |

---

## 7. Mock 데이터 스키마 (`demo/mock_data.json`)

3월~12월(키 `"3"`~`"12"`) 월별 데이터, 최상위 키 4개:

| 키 | 타입 | 항목 스키마 |
|----|------|------------|
| `calendar` | `dict[월, list]` | `{time: str, title: str}` |
| `emails` | `dict[월, list]` | `{from: str, subject: str, date: str, preview: str}` |
| `tasks` | `dict[월, list]` | `{id: str, title: str, status: "pending"\|"in_progress"\|"done", priority: str, due: str}` |
| `sales` | `dict[월, dict]` | `제품명 → {amount: float(억), change: str, count: int}` |

제품 카테고리: 엔터프라이즈 라이선스, 클라우드 서비스, 기술 컨설팅, 교육/트레이닝
