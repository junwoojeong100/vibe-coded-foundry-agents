# 프로젝트 글로벌 인스트럭션

<!-- 🔒 프로젝트 전용: 이 프로젝트(github-copilot-foundry-agent-workflow)에만 해당하는 규칙입니다. 다른 프로젝트에 복사하지 마세요. -->

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

## Agent Framework 코드 생성

에이전트·워크플로우·MCP·RAG 코드 생성 시 **`agent-framework-codegen` 스킬**을 참조한다.
(`.github/skills/agent-framework-codegen/SKILL.md`)

이 스킬에는 다음이 포함되어 있다:
- SDK import 경로, 에이전트 생성, WorkflowBuilder API 상세 예제
- Streamlit 비동기/스트리밍 통합 패턴
- MCP 도구 작성 규칙, Mock 데이터 스키마
- 트러블슈팅 가이드

### 핵심 제약 (항상 적용)

- `asyncio.run()` 사용 금지 — `run_coroutine_threadsafe` + 공유 루프 사용
- `WorkflowAgent`는 `@st.cache_resource` 금지 — 매 요청마다 새 인스턴스
- 단일 에이전트(`create_rag_agent`, `create_tool_agent`)는 `@st.cache_resource` 적용
- MCP 도구 반환값은 `str` (한국어), 시스템 경계 입력 검증 필수

## Foundry Agent Service SDK v2 마이그레이션

Agent Framework → Foundry Agent Service SDK v2(`azure-ai-agents`) 전환 시 **`foundry-agent-v2-migration` 스킬**을 참조한다.
(`.github/skills/foundry-agent-v2-migration/SKILL.md`)

이 스킬에는 다음이 포함되어 있다:
- 현재 SDK 간 기능 비교 (KB, 멀티 에이전트, MCP)
- 컴포넌트별 import 매핑 및 코드 전환 가이드
- 3단계 마이그레이션 계획 및 체크리스트
