"""
Microsoft Foundry 엔터프라이즈 AI 데모

3가지 핵심 AI 에이전트 패턴을 실제 기술 스택으로 구현합니다:
  1) RAG — Foundry IQ(Knowledge Base) 기반 사내 문서 검색
  2) MCP — MCPStdioTool로 외부 도구 서버 연결
  3) 멀티 에이전트 — WorkflowBuilder로 에이전트 간 라우팅
"""

import asyncio
import os
import queue
import sys
import threading

import streamlit as st
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

from agent_framework import (
    Agent,
    AgentExecutor,
    Case,
    Default,
    MCPStdioTool,
    WorkflowAgent,
    WorkflowBuilder,
)
from agent_framework.azure import AzureAISearchContextProvider
from agent_framework_azure_ai import AzureAIAgentClient

load_dotenv()

PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
MODEL = os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME", "gpt-4.1")
KNOWLEDGE_BASE_NAME = os.getenv("KNOWLEDGE_BASE_NAME")


# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Enterprise AI Demo",
    page_icon="🏢",
    layout="wide",
)

# ─────────────────────────────────────────────
# 필수 환경변수 검증
# ─────────────────────────────────────────────
if not PROJECT_ENDPOINT:
    st.error(
        "⚠️ FOUNDRY_PROJECT_ENDPOINT 환경변수가 설정되지 않았습니다. "
        "`.env` 파일을 확인하세요."
    )
    st.stop()


# ─────────────────────────────────────────────
# 공유 리소스 (캐시)
# ─────────────────────────────────────────────
@st.cache_resource
def _get_event_loop():
    """단일 이벤트 루프를 백그라운드 스레드에서 유지합니다."""
    loop = asyncio.new_event_loop()
    t = threading.Thread(target=loop.run_forever, daemon=True)
    t.start()
    return loop


@st.cache_resource
def _get_credential():
    """DefaultAzureCredential 싱글턴 (인증 객체 재사용)"""
    return DefaultAzureCredential()


@st.cache_resource
def get_ai_client():
    """AzureAIAgentClient 싱글턴"""
    return AzureAIAgentClient(
        project_endpoint=PROJECT_ENDPOINT,
        model_deployment_name=MODEL,
        credential=_get_credential(),
    )


# ─────────────────────────────────────────────
# Foundry IQ — Knowledge Base 연동
# ─────────────────────────────────────────────

def _get_kb_context_provider():
    """Foundry IQ(Knowledge Base) 컨텍스트 프로바이더를 생성합니다.

    KNOWLEDGE_BASE_NAME을 AzureAISearchContextProvider에 직접 전달합니다.
    """
    if not KNOWLEDGE_BASE_NAME:
        return None
    return AzureAISearchContextProvider(
        knowledge_base_name=KNOWLEDGE_BASE_NAME,
        credential=_get_credential(),
        mode="agentic",
        top_k=3,
        retrieval_reasoning_effort="low",
    )


# ─────────────────────────────────────────────
# MCP 도구 — 업무 도구 서버 연결
# ─────────────────────────────────────────────
MCP_SERVER_PATH = os.path.join(os.path.dirname(__file__), "mcp_server.py")


def _create_mcp_tool():
    """MCPStdioTool: mcp_server.py를 subprocess로 실행하여 MCP 프로토콜로 연결"""
    return MCPStdioTool(
        name="enterprise-tools",
        command=sys.executable,
        args=[MCP_SERVER_PATH],
        description="일정/이메일/업무/매출 조회 등 업무 도구 MCP 서버",
    )


# ─────────────────────────────────────────────
# 에이전트 생성
# ─────────────────────────────────────────────
@st.cache_resource
def create_rag_agent():
    """시나리오 1: RAG — Foundry IQ(Knowledge Base) 기반 사내 문서 Q&A"""
    kb_provider = _get_kb_context_provider()
    if not kb_provider:
        raise RuntimeError(
            "KNOWLEDGE_BASE_NAME이 설정되지 않았습니다. "
            "Foundry IQ Knowledge Base를 설정하세요."
        )

    instructions = (
        "당신은 기업의 사내 문서 검색 AI 어시스턴트입니다.\n"
        "- 사용자의 질문에 대해 반드시 문서를 먼저 검색한 뒤 답변합니다\n"
        "- 검색된 문서 내용을 기반으로만 답변합니다 (Grounding)\n"
        "- 관련 문서가 없으면 '해당 문서를 찾을 수 없습니다'라고 답합니다\n"
        "- 출처(문서번호)를 항상 포함합니다\n"
        "- 한국어로 간결하고 명확하게 답변합니다. 불필요한 서론 없이 핵심만 답합니다"
    )

    return Agent(
        client=get_ai_client(),
        name="rag-agent",
        instructions=instructions,
        context_providers=[kb_provider],
    )


@st.cache_resource
def create_tool_agent():
    """시나리오 2: MCP — MCPStdioTool로 외부 도구 서버에 연결"""
    return Agent(
        client=get_ai_client(),
        name="tool-agent",
        instructions=(
            "당신은 MCP 서버를 통해 업무 도구를 호출하는 AI 어시스턴트입니다.\n\n"
            "사용 가능한 도구 (MCP 서버에서 제공):\n"
            "- get_calendar_events: 일정 조회\n"
            "- create_calendar_event: 일정 생성\n"
            "- search_emails: 이메일 검색\n"
            "- get_tasks: 업무 목록 조회\n"
            "- create_task: 업무 생성\n"
            "- query_sales_data: 매출 데이터 조회\n\n"
            "가이드라인:\n"
            "- 사용자의 자연어 요청을 분석하여 적절한 도구를 호출합니다\n"
            "- 여러 도구가 필요하면 순차적으로 호출합니다\n"
            "- 결과를 간결하게 정리하여 한국어로 답변합니다. 불필요한 서론 없이 핵심만 답합니다"
        ),
        tools=[_create_mcp_tool()],
    )


def create_workflow_agent():
    """시나리오 3: 멀티 에이전트 워크플로우

    WorkflowBuilder로 구성:
      분류기(classifier) → Switch 라우팅
        - RAG만 → RAG 에이전트
        - TOOL만 → MCP 도구 에이전트
        - BOTH → RAG → Tool → Summarizer (순차 파이프라인)

    Note: WorkflowAgent는 내부 실행 상태를 추적하므로 캐시하지 않습니다.
    매 요청마다 새 인스턴스를 생성하여 동시 실행 충돌을 방지합니다.
    """
    client = get_ai_client()

    # 분류기 에이전트: 질문을 분석하여 RAG / TOOL / BOTH로 라우팅
    classifier = Agent(
        client=client,
        name="classifier",
        instructions=(
            "사용자의 질문을 분석하여 반드시 다음 중 하나의 단어로만 응답하세요:\n"
            "RAG — 사내 문서, 규정, 정책, 제도, 가이드 등에 대한 질문\n"
            "TOOL — 일정, 이메일, 업무, 매출 등 도구 사용이 필요한 요청\n"
            "BOTH — 문서 검색과 도구 사용이 모두 필요한 복합 요청\n\n"
            "예시:\n"
            "- '연차 규정 알려줘' → RAG\n"
            "- '오늘 일정 보여줘' → TOOL\n"
            "- '온보딩 절차 알려주고 관련 업무도 생성해줘' → BOTH\n\n"
            "응답은 RAG, TOOL, BOTH 중 한 단어만 출력하세요. 다른 말은 하지 마세요."
        ),
    )

    # RAG 서브 에이전트 (Foundry IQ)
    kb_provider = _get_kb_context_provider()
    if not kb_provider:
        raise RuntimeError(
            "KNOWLEDGE_BASE_NAME이 설정되지 않았습니다. "
            "Foundry IQ Knowledge Base를 설정하세요."
        )

    rag_sub = Agent(
        client=client,
        name="rag-sub-agent",
        instructions=(
            "사내 문서 검색 전문 에이전트입니다.\n"
            "- 문서를 검색하고 답변하세요\n"
            "- 이전 메시지의 분류 결과(RAG/TOOL/BOTH)는 무시하세요\n"
            "- 사용자의 원래 질문에 집중하세요\n"
            "- 한국어로 답변합니다"
        ),
        context_providers=[kb_provider],
    )

    # MCP 도구 서브 에이전트
    tool_sub = Agent(
        client=client,
        name="tool-sub-agent",
        instructions=(
            "MCP 업무 도구 전문 에이전트입니다.\n"
            "- MCP 서버의 도구를 사용하여 요청을 처리하세요\n"
            "- 이전 메시지의 분류 결과(RAG/TOOL/BOTH)는 무시하세요\n"
            "- 사용자의 원래 요청에 집중하세요\n"
            "- 한국어로 답변합니다"
        ),
        tools=[_create_mcp_tool()],
    )

    # 종합 에이전트 (BOTH 경로 마지막 단계)
    summarizer = Agent(
        client=client,
        name="summarizer",
        instructions=(
            "당신은 여러 에이전트의 결과를 종합하는 전문가입니다.\n"
            "- 대화 이력에서 '문서 검색 결과'와 '도구 실행 결과'를 각각 찾으세요\n"
            "- 분류기 응답(RAG/TOOL/BOTH 등 한 단어)은 무시하세요\n"
            "- 두 결과를 통합하여 사용자에게 하나의 일관된 답변을 제공하세요\n"
            "- 문서 기반 정보는 '📄 문서 기반 안내' 섹션으로,\n"
            "  도구 실행 결과는 '🔧 실행 결과' 섹션으로 구분하세요\n"
            "- 중복 내용은 제거하고 핵심만 정리하세요\n"
            "- 한국어로 명확하고 구조적으로 답변합니다"
        ),
    )

    # BOTH 경로 전용 에이전트 (체인에서의 역할에 맞는 별도 instructions)
    rag_both = Agent(
        client=client,
        name="rag-both-agent",
        instructions=(
            "사내 문서 검색 전문 에이전트입니다.\n"
            "당신은 멀티 에이전트 파이프라인의 첫 번째 단계입니다.\n"
            "- 이전 메시지에 RAG, TOOL, BOTH 같은 분류 단어가 있으면 무시하세요\n"
            "- 사용자의 원래 질문에서 '문서/규정/정책/절차' 관련 부분만 답변하세요\n"
            "- 도구 호출이 필요한 부분(일정 생성, 업무 생성 등)은 답변하지 마세요\n"
            "- 출처(문서번호)를 포함하세요\n"
            "- 한국어로 답변합니다"
        ),
        context_providers=[kb_provider],
    )

    tool_both = Agent(
        client=client,
        name="tool-both-agent",
        instructions=(
            "MCP 업무 도구 전문 에이전트입니다.\n"
            "당신은 멀티 에이전트 파이프라인의 두 번째 단계입니다.\n"
            "- 이전 대화에 문서 검색 결과가 있지만, 그것은 다른 에이전트가 처리한 것입니다\n"
            "- 당신은 오직 MCP 도구(일정/이메일/업무/매출)만 사용하세요\n"
            "- 사용자의 원래 요청에서 '도구 실행'이 필요한 부분만 처리하세요\n"
            "- 문서 검색이나 규정 안내는 하지 마세요 (이미 처리됨)\n"
            "- 도구를 반드시 호출하여 실제 작업을 수행하세요\n"
            "- 한국어로 답변합니다"
        ),
        tools=[_create_mcp_tool()],
    )

    # 단독 경로용 Executor
    classifier_exec = AgentExecutor(agent=classifier, id="classifier")
    rag_exec = AgentExecutor(agent=rag_sub, id="rag")
    tool_exec = AgentExecutor(agent=tool_sub, id="tool")

    # BOTH 순차 파이프라인용 Executor (전용 에이전트)
    rag_both_exec = AgentExecutor(agent=rag_both, id="rag-both")
    tool_both_exec = AgentExecutor(agent=tool_both, id="tool-both")
    summarizer_exec = AgentExecutor(agent=summarizer, id="summarizer")

    def is_rag(response) -> bool:
        """분류기 응답에서 RAG 키워드 감지"""
        return response.agent_response.text.strip().upper() == "RAG"

    def is_both(response) -> bool:
        """분류기 응답에서 BOTH 키워드 감지"""
        return response.agent_response.text.strip().upper() == "BOTH"

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
        # BOTH 경로: RAG → Tool → Summarizer (순차 파이프라인)
        .add_chain([rag_both_exec, tool_both_exec, summarizer_exec])
        .build()
    )

    return WorkflowAgent(
        workflow=workflow,
        name="multi-agent-workflow",
        description=(
            "분류기가 질문을 분석하여 RAG, MCP 도구, "
            "또는 양쪽 모두 실행하는 순차 파이프라인으로 라우팅합니다"
        ),
    )


# ─────────────────────────────────────────────
# 에이전트 실행
# ─────────────────────────────────────────────
def stream_agent(agent, prompt: str):
    """에이전트를 스트리밍으로 실행합니다 (Streamlit write_stream 호환).

    토큰 단위로 yield하여 실시간으로 응답을 표시합니다.

    Args:
        agent: 실행할 에이전트 (Agent 또는 WorkflowAgent)
        prompt: 사용자 입력 프롬프트

    Yields:
        str: 스트리밍 응답 텍스트 청크
    """
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


# ─────────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/microsoft.png", width=48)
    st.title("Enterprise AI")
    st.caption("Microsoft Foundry 데모")
    st.divider()

    scenario = st.radio(
        "데모 시나리오 선택",
        [
            "📄 사내 문서 Q&A (RAG)",
            "🔧 업무 도구 에이전트 (MCP)",
            "🤖 멀티 에이전트 워크플로우",
        ],
        index=0,
    )

    st.divider()

    if "📄" in scenario:
        st.markdown(
            """**RAG 아키텍처**
```
사용자 → RAG 에이전트
             ↓
    Foundry IQ (Knowledge Base)
             ↓
  AzureAISearchContextProvider
     → AI Search 인덱스 검색
             ↓
    검색 결과 + LLM → 답변
```"""
        )
    elif "🔧" in scenario:
        st.markdown(
            """**MCP 아키텍처**
```
사용자 → Tool 에이전트
             ↓
      MCPStdioTool 연결
             ↓
     mcp_server.py (subprocess)
   ┌─────┼─────┼─────┐
 일정   이메일  업무  매출
   └─────┼─────┼─────┘
             ↓
       결과 종합 → 답변
```"""
        )
    else:
        st.markdown(
            """**멀티 에이전트 워크플로우**
```
사용자 → WorkflowBuilder
             ↓
     ① 분류기(classifier)
             ↓
     ② Switch 라우팅
  ┌──────┬──────┐
"RAG" "TOOL" "BOTH"
  ↓      ↓      ↓
 RAG   Tool   ③ 순차 파이프라인
 Agent Agent  RAG → Tool
  ↓      ↓        ↓
 답변   답변   Summarizer
                   ↓
                종합 답변
```"""
        )

    st.divider()
    st.markdown(
        """
**엔터프라이즈 보안**
- ✅ Azure Entra ID 인증
- ✅ RBAC 기반 권한 관리
- ✅ 대화 로그 감사 추적
- ✅ 데이터 암호화
- ✅ 콘텐츠 필터링 내장
"""
    )


# ─────────────────────────────────────────────
# 메인 영역
# ─────────────────────────────────────────────

if "📄" in scenario:
    st.header("📄 사내 문서 Q&A (RAG)")
    if not KNOWLEDGE_BASE_NAME:
        st.warning(
            "⚠️ KNOWLEDGE_BASE_NAME 환경변수가 설정되지 않았습니다. "
            "RAG 시나리오를 사용하려면 Foundry IQ Knowledge Base를 설정하세요."
        )
    st.info(
        "사내 HR 정책, IT 가이드, 재무 규정 등을 AI가 검색하여 답변합니다. "
        "검색 백엔드: **Foundry IQ (Knowledge Base)**"
    )
    example_qs = [
        "연차 휴가 규정 알려줘",
        "VPN 접속 방법은?",
        "경비 처리 기준이 어떻게 되나요?",
    ]
    agent_key = "rag"
    agent_factory = create_rag_agent

elif "🔧" in scenario:
    st.header("🔧 업무 도구 에이전트 (MCP)")
    st.info(
        "MCPStdioTool을 통해 mcp_server.py에 연결합니다. "
        "에이전트가 MCP 프로토콜(JSON-RPC over stdio)로 도구를 호출합니다."
    )
    example_qs = [
        "오늘 일정 알려줘",
        "진행중인 업무 목록 보여줘",
        "이번달 매출 현황은?",
    ]
    agent_key = "tool"
    agent_factory = create_tool_agent

else:
    st.header("🤖 멀티 에이전트 워크플로우")
    st.info(
        "WorkflowBuilder로 구성된 멀티 에이전트입니다. "
        "분류기가 질문을 분석 → Switch로 RAG 또는 MCP 도구 에이전트에 라우팅합니다."
    )
    example_qs = [
        "연차 규정 알려줘",
        "오늘 일정 보여줘",
        "온보딩 절차 알려주고 관련 업무도 생성해줘",
    ]
    agent_key = "orch"
    agent_factory = create_workflow_agent

# 예시 질문 버튼
st.markdown("**💡 예시 질문:**")
cols = st.columns(len(example_qs))
for i, q in enumerate(example_qs):
    if cols[i].button(q, key=f"ex_{agent_key}_{i}", use_container_width=True):
        st.session_state[f"pending_{agent_key}"] = q

# 채팅 히스토리 초기화
history_key = f"history_{agent_key}"
if history_key not in st.session_state:
    st.session_state[history_key] = []

# 채팅 메시지 표시
for msg in st.session_state[history_key]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 입력 처리
pending_key = f"pending_{agent_key}"
user_input = st.chat_input("질문을 입력하세요...")

if pending_key in st.session_state:
    user_input = st.session_state.pop(pending_key)

if user_input:
    st.session_state[history_key].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            agent = agent_factory()
            placeholder = st.empty()
            placeholder.markdown("🤔 *답변을 준비하고 있습니다...*")
            chunks = []
            for chunk in stream_agent(agent, user_input):
                chunks.append(chunk)
                placeholder.markdown("".join(chunks))
            response = "".join(chunks)
            st.session_state[history_key].append(
                {"role": "assistant", "content": response}
            )
        except Exception as e:
            error_msg = f"⚠️ 에이전트 호출 중 오류가 발생했습니다: {e}"
            st.error(error_msg)
            st.session_state[history_key].append(
                {"role": "assistant", "content": error_msg}
            )
