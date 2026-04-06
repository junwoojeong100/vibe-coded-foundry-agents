---
name: foundry-agent-v2-migration
description: "Foundry Agent Service SDK v2 마이그레이션 가이드. USE FOR: azure-ai-agents SDK v2 마이그레이션, Agent Framework → SDK v2 전환, Foundry Agent v2 코드 변환, SDK 교체 계획. DO NOT USE FOR: 현재 Agent Framework 코드 생성(agent-framework-codegen 사용), Azure 배포(azure-deploy 사용)."
---

# Foundry Agent Service SDK v2 마이그레이션 스킬

이 스킬은 현재 Microsoft Agent Framework(`agent-framework-core`) 기반 코드를
Foundry Agent Service SDK v2(`azure-ai-agents>=2.x`)로 마이그레이션할 때 참조하는 가이드입니다.

> **현재 상태**: Foundry Agent Service SDK(`azure-ai-agents`)는 아래 기능이 아직 지원되지 않아
> 이 프로젝트는 Agent Framework를 사용합니다. SDK v2가 이 기능들을 GA하면 마이그레이션을 진행합니다.

---

## 1. 현재 SDK 간 기능 비교

| 기능 | Agent Framework (`agent-framework-core`) | Foundry Agent Service SDK (`azure-ai-agents`) | 비고 |
|------|:---:|:---:|------|
| **Foundry IQ (Knowledge Base)** | ✅ `knowledge_base_name`으로 직접 연결 | ❌ AI Search 인덱스 수동 지정 필요 | SDK에 KB 추상화 없음 |
| **멀티 에이전트 워크플로우** | ✅ `WorkflowBuilder` (명시적 그래프) | ❌ `ConnectedAgentTool`만 제공 | 명시적 라우팅/체인/분기 불가 |
| **MCP 도구 (로컬)** | ✅ `MCPStdioTool` (로컬 subprocess) | ❌ `McpTool` (원격 URL만 지원) | 로컬 stdio 연결 불가 |
| **스트리밍** | ✅ `agent.run(prompt, stream=True)` | ✅ 지원 | — |
| **기본 에이전트 생성** | ✅ | ✅ | — |
| **코드 인터프리터** | ✅ | ✅ | — |
| **파일 검색** | ✅ | ✅ | — |

---

## 2. 마이그레이션 전제 조건 (SDK v2 GA 시 확인)

마이그레이션을 시작하기 전 다음 3가지가 SDK v2에서 모두 지원되는지 확인:

- [ ] **Knowledge Base 추상화**: `knowledge_base_name`으로 Foundry IQ KB에 직접 연결 가능
- [ ] **멀티 에이전트 워크플로우**: Switch 라우팅 + 순차 파이프라인(체인) 구성 가능
- [ ] **로컬 MCP 도구**: stdio 전송으로 로컬 MCP 서버에 연결 가능

하나라도 미지원이면 해당 시나리오는 Agent Framework를 유지하거나 대체 패턴을 설계해야 합니다.

---

## 3. Import 경로 매핑 (예상)

> ⚠️ 아래 SDK v2 경로는 예상 매핑입니다. GA 시 실제 API 문서를 확인하세요.

### 3-1. 패키지 교체

```diff
# demo/requirements.txt
- agent-framework-core
- agent-framework-azure-ai
- agent-framework-azure-ai-search
+ azure-ai-agents>=2.0
```

### 3-2. Import 경로

```python
# ── Agent Framework (현재) ──
from agent_framework import Agent, AgentExecutor, WorkflowBuilder, WorkflowAgent
from agent_framework import Case, Default, MCPStdioTool
from agent_framework.azure import AzureAISearchContextProvider
from agent_framework_azure_ai import AzureAIAgentClient

# ── SDK v2 (예상) ──
# GA 시 실제 모듈 경로로 교체
from azure.ai.agents import AgentsClient          # 클라이언트
from azure.ai.agents.models import (
    Agent,                                         # 에이전트
    # 멀티 에이전트 관련 클래스 — GA 시 확인
    # KnowledgeBase 관련 클래스 — GA 시 확인
    # MCP 도구 관련 클래스 — GA 시 확인
)
```

---

## 4. 컴포넌트별 마이그레이션 가이드

### 4-1. 클라이언트 생성

```python
# Agent Framework (현재)
from agent_framework_azure_ai import AzureAIAgentClient
client = AzureAIAgentClient(
    project_endpoint=PROJECT_ENDPOINT,
    model_deployment_name=MODEL,
    credential=DefaultAzureCredential(),
)

# SDK v2 (예상)
from azure.ai.agents import AgentsClient
client = AgentsClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)
```

### 4-2. RAG (Foundry IQ Knowledge Base)

```python
# Agent Framework (현재)
from agent_framework.azure import AzureAISearchContextProvider
kb = AzureAISearchContextProvider(
    knowledge_base_name=KNOWLEDGE_BASE_NAME,
    credential=DefaultAzureCredential(),
    mode="agentic",
    top_k=3,
)
agent = Agent(client=client, context_providers=[kb], ...)

# SDK v2 (예상 — GA 시 실제 API 확인)
# Knowledge Base 연결 방식이 달라질 수 있음
# 가능성 1: knowledge_base_name 파라미터 직접 지원
# 가능성 2: AI Search 인덱스를 직접 지정하는 방식 유지
# 가능성 3: Foundry IQ 전용 tool_resources 추가
```

### 4-3. MCP 도구

```python
# Agent Framework (현재)
from agent_framework import MCPStdioTool
mcp = MCPStdioTool(
    name="enterprise-tools",
    command=sys.executable,
    args=["demo/mcp_server.py"],
    description="업무 도구 MCP 서버",
)
agent = Agent(client=client, tools=[mcp], ...)

# SDK v2 (예상 — GA 시 확인)
# 현재 SDK v1의 McpTool은 원격 URL만 지원
# v2에서 로컬 stdio가 추가되는지 확인 필요
```

### 4-4. 멀티 에이전트 워크플로우

```python
# Agent Framework (현재)
from agent_framework import WorkflowBuilder, AgentExecutor, Case, Default, WorkflowAgent

workflow = (
    WorkflowBuilder(start_executor=classifier_exec)
    .add_switch_case_edge_group(source=classifier_exec, cases=[
        Case(condition=is_rag, target=rag_exec),
        Case(condition=is_both, target=rag_both_exec),
        Default(target=tool_exec),
    ])
    .add_chain([rag_both_exec, tool_both_exec, summarizer_exec])
    .build()
)
agent = WorkflowAgent(workflow=workflow, ...)

# SDK v2 (예상 — GA 시 확인)
# 현재 SDK v1은 ConnectedAgentTool만 제공 (에이전트 간 단순 호출)
# v2에서 명시적 워크플로우 그래프(라우팅/체인/분기)가 추가되는지 확인 필요
# 대안: 커스텀 오케스트레이션 레이어를 직접 구현
```

---

## 5. 마이그레이션 단계

SDK v2가 위 기능들을 모두 GA하면 다음 순서로 진행:

### Phase 1: 의존성 교체 + 기본 에이전트

1. `demo/requirements.txt`에서 패키지 교체
2. `demo/app.py`의 import 경로 변경
3. 클라이언트 생성 코드 변경
4. 단일 에이전트(RAG, Tool) 생성 코드 변경
5. 시나리오 1(RAG), 시나리오 2(MCP) 동작 확인

### Phase 2: 멀티 에이전트 워크플로우

1. `WorkflowBuilder` → SDK v2의 워크플로우 API로 교체
2. Switch 라우팅 + 순차 파이프라인 구현
3. 시나리오 3(멀티 에이전트) 동작 확인

### Phase 3: 설정 파일 갱신

1. `.github/copilot-instructions.md` — 핵심 제약 갱신
2. `.github/skills/agent-framework-codegen/SKILL.md` — 전체 갱신
3. `.github/prompts/*.prompt.md` — 코드 템플릿 갱신
4. `.github/agents/debugger.agent.md` — 진단 체크리스트 갱신
5. `README.md` — SDK 지원 현황 표, 설치 명령어 갱신

---

## 6. 마이그레이션 체크리스트

```
[ ] SDK v2 GA 릴리스 확인
[ ] 3대 기능(KB, 멀티 에이전트, MCP stdio) 지원 여부 확인
[ ] Phase 1: 의존성 + 기본 에이전트 교체
[ ] Phase 2: 멀티 에이전트 워크플로우 교체
[ ] Phase 3: .github/ 설정 파일 전체 갱신
[ ] 전 시나리오(1, 2, 3) 정상 동작 확인
[ ] README.md "SDK 지원 현황" 표 갱신
[ ] requirements.txt에서 --pre 플래그 필요 여부 확인
```

---

## 7. 참고 링크

- [Foundry Agent Service SDK 공식 문서](https://learn.microsoft.com/azure/ai-services/agents/)
- [azure-ai-agents PyPI](https://pypi.org/project/azure-ai-agents/)
- [Agent Framework (현재 사용 중)](https://pypi.org/project/agent-framework-core/)
- [AI Foundry 포털](https://ai.azure.com)
