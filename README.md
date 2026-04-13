# Foundry Agent × GitHub Copilot

> **GitHub Copilot 바이브 코딩(Vibe Coding)**으로 만드는 **Microsoft Foundry** 기반 멀티 에이전트 워크플로우

이 프로젝트는 **두 가지 핵심 주제**를 실전 예제로 보여주기 위해 만들어졌습니다:

1. **바이브 코딩 가이드** — GitHub Copilot을 `.github/` 설정 파일로 "조종"하여, 사람이 직접 코드를 작성하지 않고 AI가 프로젝트의 기술 스택·코드 패턴·SDK 사용법을 이해하고 소스코드를 생성하도록 하는 워크플로우
2. **멀티 에이전트 워크플로우 가이드** — Microsoft Foundry의 Agent Framework SDK를 활용하여 RAG, MCP 도구 호출, 멀티 에이전트 워크플로우를 구성하는 구현 패턴

> **"코드를 직접 작성하지 않았습니다."**
> 이 프로젝트의 모든 소스코드(`demo/app.py`, `demo/mcp_server.py` 등)는
> `.github/` 디렉토리에 배치한 **11개의 커스텀 설정 파일**(인스트럭션·프롬프트·에이전트·스킬)만으로
> GitHub Copilot이 생성한 것입니다.

---

## 이 프로젝트를 만든 이유

엔터프라이즈 AI 도입을 검토할 때 가장 자주 듣는 두 가지 질문이 있습니다:

- **"AI 코딩 어시스턴트로 실제 프로젝트를 만들 수 있나요?"** — 단순 코드 자동완성을 넘어, 프로젝트 전체를 AI가 생성·리뷰·디버깅하는 **바이브 코딩**이 실무에서 가능한지
- **"멀티 에이전트 워크플로우를 어떻게 구성하나요?"** — RAG, 도구 호출, 에이전트 라우팅 같은 패턴을 하나의 워크플로우로 조합하는 방법

이 프로젝트는 **두 질문에 대한 실전 답변**입니다. `.github/` 폴더의 11개 Markdown 파일이 "설계 문서"이자 "AI에 대한 지시서" 역할을 하고, Copilot이 그에 따라 코드를 생성합니다. 동시에 생성된 코드는 Foundry의 Agent Framework SDK로 3가지 엔터프라이즈 AI 패턴(RAG, MCP, 멀티 에이전트)을 완전한 형태로 구현합니다.

---

## 바이브 코딩이란?

**바이브 코딩(Vibe Coding)**은 개발자가 코드를 한 줄씩 직접 작성하는 대신, **AI에게 의도와 맥락을 전달하여 코드를 생성**하게 하는 개발 방식입니다.

이 프로젝트에서 바이브 코딩은 다음과 같이 동작합니다:

```
┌─────────────────────────────┐      ┌────────────────────────────┐
│  개발자가 준비하는 것        │      │  GitHub Copilot이 하는 것    │
│                             │      │                            │
│  .github/                   │      │  ✅ 소스코드 생성           │
│  ├── copilot-instructions   │ ───→ │  ✅ MCP 도구 함수 작성      │
│  ├── instructions/ (3개)    │      │  ✅ 코드 리뷰 수행          │
│  ├── skills/ (2개)          │      │  ✅ 런타임 문제 진단        │
│  ├── prompts/ (3개)         │      │  ✅ 기술 스택 패턴 준수      │
│  └── agents/ (2개)          │      │                            │
│                             │      │                            │
│  = 11개의 Markdown 파일       │      │  = 프로젝트 전체 코드        │
└─────────────────────────────┘      └────────────────────────────┘
```

핵심은 **"무엇을 만들 것인가"와 "어떤 패턴을 따를 것인가"를 정확히 문서화**하면, AI가 일관된 품질의 코드를 생성한다는 것입니다. `.github/` 디렉토리의 11개 파일이 바로 그 문서입니다.

### 두 가지 도구로 바이브 코딩

GitHub Copilot은 **VS Code(IDE)**뿐 아니라 **Copilot CLI(터미널)**에서도 동일한 `.github/` 설정 파일을 인식합니다. 개발 환경에 따라 두 가지 방식을 선택하거나 병행할 수 있습니다.

| 항목 | 🖥️ VS Code (IDE) | 💻 Copilot CLI (터미널) |
|------|:---:|:---:|
| **설정 파일 인식** | `copilot-instructions.md`, `instructions/`, `skills/`, `prompts/`, `agents/` | `copilot-instructions.md`, `instructions/`, `skills/` + `AGENTS.md` 등 |
| **코드 생성** | 에디터 내 인라인 + 채팅 패널 | 터미널에서 직접 파일 생성/수정 |
| **프롬프트 호출** | `/프롬프트명` (채팅) | 자연어로 직접 요청 |
| **에이전트 호출** | `@에이전트명` (채팅) | `/agent`로 선택 |
| **스킬 관리** | 자동 로드 + `/스킬명` | `/skills`로 관리 |
| **MCP 서버** | 설정 기반 자동 연결 | `/mcp`로 관리 |
| **코드 리뷰** | `@reviewer` 에이전트 | `/review` 명령어 |
| **변경사항 확인** | Git 패널 | `/diff` 명령어 |
| **플랜 모드** | `Shift+Tab`으로 Plan 모드 전환 | `/plan` 명령어 또는 `Shift+Tab` |
| **PR 생성 위임** | Copilot Coding Agent에 이슈 할당 | `/delegate`로 Copilot에 위임 |

### Copilot CLI로 바이브 코딩하기

[GitHub Copilot CLI](https://docs.github.com/copilot/concepts/agents/about-copilot-cli)는 터미널에서 직접 AI 코딩 에이전트와 대화하며 코드를 생성·수정·리뷰할 수 있는 도구입니다. 이 프로젝트의 `.github/` 설정 파일을 자동으로 인식하여 동일한 바이브 코딩이 가능합니다.

#### 설치

```bash
# macOS / Linux (Homebrew)
brew install copilot-cli

# macOS / Linux (install script)
curl -fsSL https://gh.io/copilot-install | bash

# Windows (WinGet)
winget install GitHub.Copilot

# npm (모든 플랫폼)
npm install -g @github/copilot
```

> **사전 요구**: 활성화된 [GitHub Copilot 구독](https://github.com/features/copilot/plans)이 필요합니다.

#### 이 프로젝트에서 사용하기

```bash
# 1. 프로젝트 디렉토리로 이동
cd github-copilot-foundry-agent-workflow

# 2. Copilot CLI 실행 — .github/ 설정 파일이 자동으로 인식됩니다
copilot

# 3. (최초 1회) 로그인
/login

# 4. 인식된 인스트럭션 확인
/instructions
```

이후 자연어로 요청하면 `.github/copilot-instructions.md`와 `instructions/*.md`의 규칙을 반영한 코드를 생성합니다:

```
> "RAG 에이전트에 top_k를 5로 변경해줘"
> "새 MCP 도구 get_employee_info를 추가해줘"
> "멀티 에이전트 워크플로우에 새로운 분류 경로를 추가해줘"
```

#### CLI 워크플로우

```
┌─────────────────────────────────────────────────────────────────┐
│  1. 시작: copilot 실행 → .github/ 설정 자동 인식                  │
│     copilot-instructions.md, instructions/*.md → 자동 적용       │
├─────────────────────────────────────────────────────────────────┤
│  2. 계획: /plan 모드로 구현 계획 수립 (선택)                       │
│     "MCP 도구 3개를 추가하려면 어떤 순서로 해야 할까?"              │
├─────────────────────────────────────────────────────────────────┤
│  3. 생성: 자연어로 코드 생성/수정 요청                              │
│     "get_employee_info MCP 도구를 mcp_server.py에 추가해줘"       │
├─────────────────────────────────────────────────────────────────┤
│  4. 검증: /diff로 변경사항 확인 → /review로 코드 리뷰              │
├─────────────────────────────────────────────────────────────────┤
│  5. 완료: 커밋 또는 /delegate로 PR 생성을 Copilot에 위임           │
└─────────────────────────────────────────────────────────────────┘
```

#### CLI에서 `.github/` 설정 파일 동작 방식

이 프로젝트의 `.github/` 설정 파일 11개 중 Copilot CLI가 자동으로 인식하는 범위:

| `.github/` 파일 | CLI 인식 | CLI에서의 활용 |
|------|:---:|------|
| `copilot-instructions.md` | ✅ 자동 | 프로젝트 기술 스택·코드 패턴·캐싱 규칙이 모든 요청에 반영 |
| `instructions/*.instructions.md` | ✅ 자동 | Python 컨벤션, Azure 보안, 한국어 규칙이 자동 적용 |
| `skills/*/SKILL.md` | ✅ `/skills` | SDK 코드 생성·마이그레이션 패턴을 명시적으로 참조 가능 |
| `prompts/*.prompt.md` | ⚠️ 직접 호출 불가 | 프롬프트 내용을 자연어로 풀어서 요청 (예: "새 MCP 도구를 create-tool 프롬프트 패턴으로 만들어줘") |
| `agents/*.agent.md` | ⚠️ 직접 호출 불가 | 에이전트 역할을 자연어로 지시 (예: "코드 리뷰어 관점에서 이 변경사항 검토해줘") |

> **핵심**: `copilot-instructions.md`와 `instructions/` 3개 파일은 **IDE와 CLI 모두에서 자동 적용**됩니다. 이 4개 파일만으로도 프로젝트의 기술 스택·컨벤션·보안 규칙이 일관되게 반영됩니다.

---

## 이런 분들을 위한 프로젝트입니다

| 대상 | 활용 방법 |
|------|----------|
| **AI 코딩에 관심 있는 개발자** | `.github/` 설정 파일 구조를 참고하여 자신의 프로젝트에 바이브 코딩 워크플로우를 적용 |
| **엔터프라이즈 AI 아키텍트** | RAG + MCP + 멀티 에이전트 워크플로우의 실전 구현 패턴을 참고 |
| **Microsoft Foundry 입문자** | Agent Framework SDK 사용법, Foundry IQ 연동, 모델 배포까지 단계별 가이드 |
| **기술 세미나·워크숍 진행자** | 3가지 시나리오를 라이브 데모로 시연하며 엔터프라이즈 AI 패턴 설명 |

---

## 주요 특징

- **100% 바이브 코딩** — 모든 소스코드를 GitHub Copilot이 `.github/` 설정 파일을 참조하여 생성
- **IDE + CLI 지원** — VS Code 에디터뿐 아니라 [GitHub Copilot CLI](https://docs.github.com/copilot/concepts/agents/about-copilot-cli)(터미널)에서도 동일한 `.github/` 설정으로 바이브 코딩 가능
- **11개 커스텀 설정 파일** — 인스트럭션(자동 적용) · 프롬프트(수동 호출) · 에이전트(수동 호출) · 스킬(자동 로드 + 수동 호출)로 분리된 체계적 구성
- **3가지 엔터프라이즈 AI 패턴** — RAG(문서 검색), MCP(도구 호출), 멀티 에이전트 워크플로우를 하나의 앱에서 시연
- **실시간 스트리밍** — 토큰 단위 응답 스트리밍으로 체감 응답 속도 향상
- **재사용 가능한 설정** — 공용 인스트럭션 3개(`python`, `azure`, `korean`)를 다른 프로젝트에 즉시 복사하여 사용 가능
- **업종 교체 용이** — 코드 구조는 유지하고 데이터·프롬프트만 교체하여 제조·금융·의료 등 다른 업종 데모로 전환 가능

---

## GitHub Copilot 커스텀 설정

이 프로젝트의 소스코드(`demo/app.py`, `demo/mcp_server.py` 등)는 **GitHub Copilot이 `.github/` 하위 md 파일을 참조하여 생성**한 것입니다.
`.github/` 디렉토리에 **11개의 md 파일**을 배치하여 Copilot의 코드 생성·리뷰·디버깅 품질을 제어합니다.

### 파일 유형별 동작 방식

| 파일 유형 | 위치 | 호출 방법 | 적용 방식 |
|----------|------|----------|----------|
| **글로벌 인스트럭션** | `.github/copilot-instructions.md` | 없음 | ✅ 자동 — 모든 Copilot 요청에 항상 포함 |
| **파일 패턴 인스트럭션** | `.github/instructions/*.instructions.md` | 없음 | ✅ 자동 — `applyTo` 패턴에 매칭되는 파일 작업 시 포함 |
| **스킬** | `.github/skills/*/SKILL.md` | 채팅에서 `/스킬명` 입력 | ✅ 자동 + 🔘 수동 — 관련 주제 감지 시 자동 로드, `/스킬명`으로 명시적 호출도 가능 |
| **재사용 프롬프트** | `.github/prompts/*.prompt.md` | 채팅에서 `/프롬프트명` 입력 | 🔘 수동 |
| **커스텀 에이전트** | `.github/agents/*.agent.md` | 채팅에서 `@에이전트명` 입력 | 🔘 수동 |

### 언제, 어떤 파일 유형을 사용해야 하나요?

| 파일 유형 | 주요 용도 | 사용 시점 예시 |
|----------|----------|--------------|
| **인스트럭션** | **"항상 이 규칙을 따라라"** — 코드 컨벤션, 보안 정책, 언어 규칙 등 모든 작업에 자동 적용되는 상시 규칙 | Python 코드를 작성할 때마다 Google docstring과 타입 힌트를 사용하게 하고 싶을 때, Azure 코드에서 항상 `DefaultAzureCredential`을 사용하게 하고 싶을 때 |
| **스킬** | **"이 분야의 전문 지식을 참고해라"** — 특정 SDK나 프레임워크의 API 레퍼런스, 코드 패턴, 트러블슈팅 가이드 등 도메인 지식을 제공 | Agent Framework SDK로 에이전트를 만들 때 올바른 import 경로와 API 사용법이 필요할 때, SDK 마이그레이션 시 기능 비교와 코드 변환 가이드가 필요할 때 |
| **재사용 프롬프트** | **"지금 이 작업을 이 방식으로 해라"** — 반복적으로 수행하는 정형화된 작업을 템플릿화하여 일관된 결과를 보장하는 작업 지시서 | 새 MCP 도구를 추가할 때마다 동일한 패턴(`@server.tool()` 데코레이터, mock 데이터 연동)으로 생성하고 싶을 때, 코드 리뷰를 매번 같은 8개 항목 체크리스트로 수행하고 싶을 때 |
| **커스텀 에이전트** | **"이 역할을 맡아서 수행해라"** — 특정 역할(리뷰어, 디버거)에 특화된 페르소나와 도구 권한을 가진 전문 AI 에이전트 | 코드 변경 후 보안·패턴 준수·성능 관점에서 종합 리뷰가 필요할 때, 런타임 에러 발생 시 환경→인증→RAG→MCP 순서로 체계적 진단이 필요할 때 |

> **요약**: 인스트럭션은 "상시 규칙", 스킬은 "참고 자료", 프롬프트는 "작업 템플릿", 에이전트는 "전문가 역할"입니다.

### 재사용 범위: 프로젝트 전용 🔒 vs. 공용 🌐

각 파일의 상단 주석에 `🔒 프로젝트 전용` 또는 `🌐 공용`이 표기되어 있습니다.

#### 🌐 공용 — 다른 프로젝트에 복사하여 즉시 재사용 가능

| 파일 | `applyTo` | 역할 | 재사용 방법 |
|------|-----------|------|------------|
| `instructions/python.instructions.md` | `**/*.py` | Python 3.12 가상환경 설정, 의존성 관리(`requirements.txt`), 코드 컨벤션(Google docstring, 타입 힌트, import 순서) | `.github/instructions/`에 복사 |
| `instructions/azure.instructions.md` | `**/*.py` | `DefaultAzureCredential` 인증, `.env` 관리, `.gitignore` 포함 규칙, 민감정보 보안 | `.github/instructions/`에 복사 |
| `instructions/korean.instructions.md` | `**` | 한국어 응답·주석·docstring 작성, 변수명은 영어, 기술 용어 병기 규칙 | `.github/instructions/`에 복사 |

> **재사용 시나리오**: 새 Python + Azure 프로젝트를 시작할 때, 위 3개 파일을 `.github/instructions/`에 복사하면 Copilot이 자동으로 Python 컨벤션·Azure 보안·한국어 작성 규칙을 적용합니다.

#### 🔒 프로젝트 전용 — 이 프로젝트의 기술 스택(Agent Framework, Streamlit, MCP)에 특화

| 파일 | 역할 | 전용인 이유 |
|------|------|------------|
| `copilot-instructions.md` | **프로젝트 전체 규칙** — 3가지 시나리오 정의, SDK import 경로, WorkflowBuilder API, 스트리밍 패턴, mock 데이터 스키마, Streamlit UI 구조 | Agent Framework 클래스명, 캐싱 규칙, 비동기 패턴이 이 프로젝트의 기술 스택에 종속 |
| `prompts/add-scenario.prompt.md` | **새 시나리오 추가** — `Agent` 생성 코드 템플릿, `tools`/`context_providers` 구성, 사이드바 연동 규칙 | `create_rag_agent`/`create_tool_agent` 패턴이 `demo/app.py`에 종속 |
| `prompts/create-tool.prompt.md` | **새 MCP 도구 생성** — `@server.tool()` 데코레이터, `mock_data.json` 연동, RAG/MCP 구분 기준 | `demo/mcp_server.py`의 FastMCP 서버 구조에 종속 |
| `prompts/review-code.prompt.md` | **코드 리뷰 요청** — 8개 항목 체크리스트(패턴 준수, 보안, 스트리밍, 멀티 에이전트 정합성 등) | Agent Framework + WorkflowBuilder 패턴 기준 |
| `skills/agent-framework-codegen/SKILL.md` | **Agent Framework 코드 생성 스킬** — SDK import 경로, 에이전트/워크플로우/RAG/MCP 생성 패턴, Streamlit 비동기 통합, 트러블슈팅 | Agent Framework SDK API와 이 프로젝트의 코드 패턴에 종속 |
| `skills/foundry-agent-v2-migration/SKILL.md` | **SDK v2 마이그레이션 스킬** — Agent Framework → SDK v2 전환 가이드, 기능 비교, import 매핑, 단계별 마이그레이션 계획 | SDK v2 GA 시점까지 Agent Framework 유지 필요 |
| `agents/reviewer.agent.md` | **코드 리뷰어 에이전트** — 읽기 전용으로 코드 변경사항을 검토하고 개선사항 제안 | 리뷰 기준이 `AzureAIAgentClient`/`WorkflowBuilder` 패턴에 특화 |
| `agents/debugger.agent.md` | **트러블슈터 에이전트** — 5단계 진단 체크리스트(환경→Azure 인증→RAG→MCP→Streamlit) 기반으로 런타임 문제 진단 | 진단 대상이 Foundry IQ, MCPStdioTool, Streamlit 비동기 패턴 등 이 프로젝트 고유 구성 |

### Copilot 커스텀 파일 전체 관계도

```
.github/
├── copilot-instructions.md          ← 🔒 항상 자동 적용 (프로젝트 전체 규칙)
│
├── instructions/                    ← 🌐 파일 패턴별 자동 적용 (재사용 가능)
│   ├── python.instructions.md       ← *.py 편집 시 자동
│   ├── azure.instructions.md        ← *.py 편집 시 자동
│   └── korean.instructions.md       ← 모든 파일 편집 시 자동
│
├── skills/                          ← 🔒 자동 로드 + /이름으로 수동 호출
│   ├── agent-framework-codegen/     ← Agent Framework SDK 코드 생성 시
│   │   └── SKILL.md
│   └── foundry-agent-v2-migration/  ← SDK v2 마이그레이션 시
│       └── SKILL.md
│
├── prompts/                         ← 🔒 /이름으로 수동 호출
│   ├── add-scenario.prompt.md       ← /add-scenario
│   ├── create-tool.prompt.md        ← /create-tool
│   └── review-code.prompt.md        ← /review-code
│
└── agents/                          ← 🔒 @이름으로 수동 호출
    ├── reviewer.agent.md            ← @reviewer (읽기 전용)
    └── debugger.agent.md            ← @debugger (진단 + 터미널)
```

### 다른 프로젝트에서 재사용하려면

```bash
# 1. 공용 인스트럭션 3개를 새 프로젝트에 복사
mkdir -p <새프로젝트>/.github/instructions
cp .github/instructions/python.instructions.md   <새프로젝트>/.github/instructions/
cp .github/instructions/azure.instructions.md    <새프로젝트>/.github/instructions/
cp .github/instructions/korean.instructions.md   <새프로젝트>/.github/instructions/

# 2. 프로젝트 전용 copilot-instructions.md는 새로 작성
# (기술 스택, 코드 패턴, SDK 매핑 등을 해당 프로젝트에 맞게 정의)
```

## 데모 시나리오

이 프로젝트는 일반 기업 환경에서 가장 많이 사용되는 3가지 AI 패턴을 하나의 Streamlit 앱에서 시연합니다.

| # | 시나리오 | AI 패턴 | 기술 스택 | 설명 |
|---|---------|---------|----------|------|
| 1 | **📄 사내 문서 Q&A** | RAG | `AzureAISearchContextProvider` → Foundry IQ | 사내 규정·정책 문서를 벡터+키워드 하이브리드 검색으로 조회 |
| 2 | **🔧 업무 도구 에이전트** | MCP | `MCPStdioTool` → `mcp_server.py` (FastMCP) | 일정·이메일·업무·매출 조회/생성 도구를 MCP 프로토콜로 호출 |
| 3 | **🤖 멀티 에이전트 워크플로우** | Multi-Agent | `WorkflowBuilder` + `AgentExecutor` + `Switch` | 분류기 → Switch 라우팅 → RAG·MCP 서브 에이전트 + BOTH 순차 파이프라인 |

### 시나리오별 예시 질문

```
# 시나리오 1 — 사내 문서 Q&A (RAG)
"연차 휴가 규정 알려줘"
"VPN 접속 방법은?"
"경비 처리 기준이 어떻게 되나요?"

# 시나리오 2 — 업무 도구 에이전트 (MCP)
"오늘 일정 알려줘"
"진행중인 업무 목록 보여줘"
"이번달 매출 현황은?"

# 시나리오 3 — 멀티 에이전트 워크플로우
"내일 회의 준비해야 하는데, 일정 확인하고 관련 이메일도 찾아줘"
"이번 달 매출 현황 보여주고 관련 업무 진행 상태도 알려줘"
"신규 입사자 온보딩에 필요한 정보 종합해줘"
```

### 멀티 에이전트 워크플로우 상세

시나리오 3은 이 프로젝트의 핵심으로, **에이전트 간 협업의 실전 패턴**을 보여줍니다:

```
사용자 질문
    │
    ▼
① 분류기(Classifier Agent)
    │  "RAG" / "TOOL" / "BOTH" 판별
    ▼
② Switch 라우팅
    ├── RAG  ──→ RAG 에이전트 ──→ 답변
    ├── TOOL ──→ MCP 도구 에이전트 ──→ 답변
    └── BOTH ──→ ③ 순차 파이프라인 (add_chain)
                    │
                    ├── RAG 에이전트 (문서 검색)
                    ├── MCP 도구 에이전트 (도구 실행)
                    └── Summarizer (결과 종합)
                            │
                            ▼
                        통합 답변
```

- **분류기**: 사용자 질문을 분석하여 `RAG`, `TOOL`, `BOTH` 중 하나로 라우팅
- **Switch 라우팅**: `Case`/`Default`로 조건 분기, `BOTH`는 순차 파이프라인으로 전달
- **순차 파이프라인**: `add_chain([RAG, Tool, Summarizer])`로 3개 에이전트를 순서대로 실행

## 설정 가이드

### 사전 요구 사항

- **Python 3.12+** — [다운로드](https://www.python.org/downloads/)
- **Git** — [다운로드](https://git-scm.com/downloads)
- **Azure CLI** — [설치 가이드](https://learn.microsoft.com/cli/azure/install-azure-cli)
- **Azure 구독** — [무료 체험 계정 만들기](https://azure.microsoft.com/free/) + Foundry 프로젝트
- **GitHub Copilot CLI** (선택) — 터미널 기반 바이브 코딩 시. `brew install copilot-cli` (macOS/Linux) 또는 `winget install GitHub.Copilot` (Windows). [설치 가이드](https://docs.github.com/copilot/concepts/agents/about-copilot-cli)

### 1단계: 로컬 환경 준비

```bash
# 저장소 클론
git clone https://github.com/junwoojeong100/github-copilot-foundry-agent-workflow.git
cd github-copilot-foundry-agent-workflow

# 가상환경 생성 및 활성화
# macOS / Linux:
python3.12 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell):
# py -3.12 -m venv .venv
# .venv\Scripts\Activate.ps1
# ※ 실행 정책 오류 시: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

# Windows (CMD):
# py -3.12 -m venv .venv
# .venv\Scripts\activate.bat

# 패키지 설치 (RC 버전 포함이므로 --pre 필요)
pip install --pre -r demo/requirements.txt
```

### 2단계: Foundry 프로젝트 및 모델 준비

1. [AI Foundry 포털](https://ai.azure.com) 접속
2. 프로젝트가 없으면 **+ 새 프로젝트** 생성
3. **채팅 모델 배포** (이미 배포되어 있으면 건너뛰기):
   - 프로젝트 → **모델 + 엔드포인트** → **+ 모델 배포** → **기본 모델 배포**
   - `gpt-4o` 등 원하는 채팅 모델 선택 → **배포 이름** 지정 → **배포**
   - ⚠️ 여기서 지정한 **배포 이름**을 `demo/.env`의 `FOUNDRY_MODEL_DEPLOYMENT_NAME`에 입력해야 합니다
   - 예: 배포 이름을 `gpt-5.4-2`로 지정했다면 `.env`에 `FOUNDRY_MODEL_DEPLOYMENT_NAME=gpt-5.4-2`
4. **임베딩 모델 배포** (Knowledge Base에 필요 — 시나리오 2만 사용하면 건너뛰기):
   - 같은 화면에서 **+ 모델 배포** → `text-embedding-large` 선택 → **배포**
   - 이 임베딩 모델은 Knowledge Base가 내부적으로 사용하므로, 별도 환경변수 설정은 불필요합니다

### 3단계: 환경변수 설정 및 Azure 로그인

```bash
# 환경변수 파일 생성
cp demo/.env.example demo/.env   # Windows: copy demo\.env.example demo\.env
```

`demo/.env` 파일을 편집기로 열어 값을 입력합니다:

| 변수 | 필수 | 설명 | 찾는 방법 |
|------|------|------|----------|
| `FOUNDRY_PROJECT_ENDPOINT` | ✅ | Foundry 프로젝트 엔드포인트 URL | AI Foundry 포털 → 프로젝트 → 개요 → "프로젝트 엔드포인트" 복사 |
| `FOUNDRY_MODEL_DEPLOYMENT_NAME` | 선택 | 모델 배포 이름 (기본값: `gpt-4.1`) | 2단계에서 지정한 배포 이름 |
| `KNOWLEDGE_BASE_NAME` | 조건부 | Knowledge Base 이름 (시나리오 1·3 사용 시 필수, 미설정 시 MCP만 동작) | 5단계에서 생성 |

```bash
# Azure 로그인
az login
# 구독이 여러 개인 경우:
# az account set --subscription "<구독 이름 또는 ID>"
```

> **시나리오 2(MCP)만 사용한다면** `FOUNDRY_PROJECT_ENDPOINT`와 `FOUNDRY_MODEL_DEPLOYMENT_NAME`만 설정하고 바로 실행 가능합니다:
> ```bash
> streamlit run demo/app.py
> ```
> 시나리오 1(RAG)·3(멀티 에이전트)을 사용하려면 아래 4~6단계를 계속 진행하세요.

### 4단계: Blob Storage에 문서 업로드 (RAG 시나리오)

> 시나리오 2(MCP)만 사용하면 이 단계부터 건너뛰세요.

이 프로젝트의 `docs/` 폴더에 샘플 사내 문서 6개가 포함되어 있습니다 (연차 규정, VPN 가이드, 경비 처리, 정보보안, 채용/온보딩, 회의실 예약).
실제 사용 시에는 사내 문서(PDF, Word, TXT, HTML, Markdown 등)로 교체하세요.

```bash
# 리소스 그룹 생성 (이미 있으면 건너뛰기)
az group create \
  --name my-rg \
  --location koreacentral

# 스토리지 계정 생성 (이름은 전역 고유해야 합니다 — 변경 필요)
az storage account create \
  --name mystorageaccount \
  --resource-group my-rg \
  --location koreacentral \
  --sku Standard_LRS

# Blob 컨테이너 생성
az storage container create \
  --name company-docs \
  --account-name mystorageaccount \
  --auth-mode login

# 샘플 문서 일괄 업로드
az storage blob upload-batch \
  --account-name mystorageaccount \
  --destination company-docs \
  --source ./docs/ \
  --auth-mode login

# ※ --auth-mode login은 Azure AD(Entra ID) 인증을 사용합니다.
# 권한 오류 발생 시, 스토리지 계정에 "Storage Blob Data Contributor" 역할을 할당하세요:
# az role assignment create \
#   --role "Storage Blob Data Contributor" \
#   --assignee "<내 Azure 로그인 이메일>" \
#   --scope /subscriptions/<구독ID>/resourceGroups/my-rg/providers/Microsoft.Storage/storageAccounts/mystorageaccount
```

### 5단계: Knowledge Base 생성

Foundry IQ는 Azure AI Search를 내부 기반으로 사용하지만, 사용자는 **Foundry IQ의 Knowledge Base 인터페이스**만 사용하면 됩니다.
Azure AI Search 리소스 생성, 인덱스 스키마 정의, 임베딩, 청킹 등은 **Foundry IQ가 자동으로 처리**합니다.

1. AI Foundry 포털 → 프로젝트 선택 → **Knowledge Bases** (지식 베이스)
2. **+ 새 Knowledge Base** 클릭
3. **이름** 입력 (예: `company-docs-kb`)
4. **데이터 소스** 선택:
   - **Azure Blob Storage** 선택
   - 4단계에서 생성한 **스토리지 계정** (`mystorageaccount`) 을 찾아 선택
   - 컨테이너 목록에서 `company-docs` 선택
   - ⚠️ 스토리지 계정이 Foundry 프로젝트와 **같은 구독**에 있어야 목록에 표시됩니다
5. **검색 설정**:
   - 검색 유형: **하이브리드 (벡터 + 키워드)** 권장
   - 임베딩 모델: 2단계에서 배포한 임베딩 모델 선택 (예: `text-embedding-large`)
6. **만들기** 클릭
7. 인덱싱 완료까지 대기 (문서 수에 따라 수 분 ~ 수십 분)

> **Foundry IQ가 자동으로 처리하는 것들**:
> - Azure AI Search 리소스 및 인덱스 생성/관리
> - 문서 형식 감지 (PDF, Word, TXT, HTML, Markdown 등)
> - 문서 청킹 (적절한 크기로 분할)
> - 임베딩 벡터 생성
> - 인덱스 저장 및 업데이트

Knowledge Base 생성 후, `demo/.env`에 다음 환경변수를 추가합니다:

```bash
KNOWLEDGE_BASE_NAME=company-docs-kb
```

### 6단계: AI Search RBAC 권한 설정

로컬 개발 환경에서 `DefaultAzureCredential`(`az login` 사용자)로 AI Search에 접근하려면 **Search Index Data Reader** 역할이 필요합니다.

```bash
# 현재 로그인한 사용자의 Object ID 확인
az ad signed-in-user show --query id -o tsv

# Search Index Data Reader 역할 할당
az role assignment create \
  --assignee "<사용자 Object ID>" \
  --role "Search Index Data Reader" \
  --scope "/subscriptions/<구독ID>/resourceGroups/<리소스그룹>/providers/Microsoft.Search/searchServices/<Search서비스이름>"
```

> ⚠️ RBAC 역할 전파에 1~5분 정도 소요될 수 있습니다. 할당 후 즉시 동작하지 않으면 잠시 대기하세요.

### 7단계: 실행 및 확인

```bash
streamlit run demo/app.py
# 브라우저가 자동으로 열리지 않으면 http://localhost:8501 에 직접 접속하세요
```

### 문서 업데이트 시

Blob에 문서 추가/수정 후 Knowledge Base에서 **동기화** 클릭

## 아키텍처

### 전체 시스템 구성

```
                            ┌─────────────────────────────────────────────┐
                            │            Microsoft Foundry                │
                            │                                             │
                            │   ┌──────────┐   ┌──────────────────────┐  │
                            │   │ GPT-4.1  │   │ Foundry IQ           │  │
                            │   │ (Chat    │   │ (Knowledge Base)     │  │
                            │   │  Model)  │   │                      │  │
                            │   └────┬─────┘   └──────────┬───────────┘  │
                            │        │                     │              │
                            │        └──────┬──────────────┘              │
                            │               │                             │
                            │      Agent Framework SDK                    │
                            │   (agent-framework-core)                    │
                            └───────────────┬─────────────────────────────┘
                                            │
┌──────────────────┐            ┌───────────┴────────────┐
│  .github/        │            │     Streamlit Demo      │
│  (11개 설정 파일) │            │     (demo/app.py)       │
│                  │            │                         │
│  Copilot이       │    생성    │  ┌───────────────────┐  │
│  이 파일들을     │ ────────→  │  │🤖 WorkflowAgent   │  │  ← 시나리오 3
│  참조하여        │            │  │ (WorkflowBuilder) │  │
│  코드 생성       │            │  └──┬──────────┬─────┘  │
│                  │            │     │ Switch   │        │
│                  │            │  ┌──┴───┐  ┌───┴────┐   │
│                  │            │  │📄 RAG│  │🔧 MCP  │   │  ← 시나리오 1, 2
│                  │            │  │Agent │  │ Agent  │   │
│                  │            │  └──┬───┘  └───┬────┘   │
│                  │            │     │          │        │
│                  │            │  ┌──┴────┐ ┌───┴─────┐  │
│                  │            │  │Foundry│ │  MCP    │  │
│                  │            │  │IQ(KB) │ │ Server  │  │
│                  │            │  └───────┘ │ (stdio) │  │
│                  │            │            └─────────┘  │
└──────────────────┘            └─────────────────────────┘
```

### 바이브 코딩 워크플로우

```
┌─────────────────────────────────────────────────────────────────────┐
│  1. 설계: .github/ 디렉토리에 규칙 문서화                             │
│     copilot-instructions.md  → 기술 스택, SDK 패턴, 데이터 스키마      │
│     instructions/*.md        → Python 컨벤션, Azure 보안, 한국어 규칙  │
│     skills/*/SKILL.md         → SDK 코드 생성, v2 마이그레이션 가이드  │
│     prompts/*.md             → 도구 생성, 시나리오 추가 템플릿          │
│     agents/*.md              → 코드 리뷰어, 트러블슈터 에이전트 정의    │
├─────────────────────────────────────────────────────────────────────┤
│  2. 생성: GitHub Copilot에게 자연어로 요청                             │
│     "RAG 에이전트 만들어줘" → Copilot이 패턴에 맞는 코드 생성           │
│     "/create-tool 매출 조회" → 프롬프트 참조하여 MCP 도구 함수 생성     │
├─────────────────────────────────────────────────────────────────────┤
│  3. 검증: 커스텀 에이전트로 품질 보증                                   │
│     @reviewer → 8개 항목 체크리스트로 코드 리뷰                        │
│     @debugger → 5단계 진단으로 런타임 문제 해결                        │
└─────────────────────────────────────────────────────────────────────┘
```

## 기술 스택

| 영역 | 기술 | 역할 |
|------|------|------|
| **UI** | Streamlit | 채팅 인터페이스, 시나리오 선택, 실시간 스트리밍 표시 |
| **AI Framework** | Microsoft Agent Framework (`agent-framework-core`) | 에이전트 생성, 워크플로우 빌더, MCP 도구 연결 |
| **RAG** | `agent-framework-azure-ai-search` | `AzureAISearchContextProvider`로 Foundry IQ(Knowledge Base) 연동 |
| **MCP** | `MCPStdioTool` + FastMCP | stdio 전송으로 로컬 MCP 서버에 연결하여 도구 호출 |
| **멀티 에이전트** | `WorkflowBuilder` + `AgentExecutor` | Switch 라우팅, 순차 파이프라인(`add_chain`) 구성 |
| **인증** | `azure-identity` → `DefaultAzureCredential` | Azure Entra ID 기반 인증 (로컬: `az login`, 배포: Managed Identity) |
| **모델** | Azure AI Foundry 배포 모델 | 기본 `gpt-4.1`, 환경변수로 변경 가능 |

## 프로젝트 구조

```
github-copilot-foundry-agent-workflow/
│
├── README.md
├── .gitignore
│
├── .github/                             # ★ 바이브 코딩의 핵심 — Copilot 설정 파일
│   ├── copilot-instructions.md          #   🔒 프로젝트 전체 규칙 (자동 적용)
│   ├── instructions/                    #   🌐 파일 패턴별 자동 적용 (재사용 가능)
│   │   ├── python.instructions.md       #     *.py → Python 컨벤션
│   │   ├── azure.instructions.md        #     *.py → Azure 인증/보안
│   │   └── korean.instructions.md       #     *    → 한국어 작성 규칙
│   ├── skills/                          #   🔒 자동 로드 + /이름으로 수동 호출
│   │   ├── agent-framework-codegen/     #     Agent Framework SDK 코드 생성
│   │   │   └── SKILL.md
│   │   └── foundry-agent-v2-migration/  #     SDK v2 마이그레이션 가이드
│   │       └── SKILL.md
│   ├── prompts/                         #   🔒 /이름으로 수동 호출
│   │   ├── add-scenario.prompt.md       #     새 시나리오 추가
│   │   ├── create-tool.prompt.md        #     새 MCP 도구 생성
│   │   └── review-code.prompt.md        #     코드 리뷰 요청
│   └── agents/                          #   🔒 @이름으로 수동 호출
│       ├── reviewer.agent.md            #     코드 리뷰어 (읽기 전용)
│       └── debugger.agent.md            #     트러블슈터 (진단 + 터미널)
│
├── demo/                                # 데모 애플리케이션
│   ├── app.py                           #   Streamlit 앱 (3개 시나리오)
│   ├── mcp_server.py                    #   MCP 서버 (FastMCP, 6개 업무 도구)
│   ├── mock_data.json                   #   시뮬레이션 데이터 (3~12월 월별)
│   ├── requirements.txt                 #   Python 의존성
│   └── .env.example                     #   환경변수 템플릿
│
└── docs/                                # 샘플 사내 문서 (RAG용, Blob Storage 업로드)
    ├── HR-001_연차휴가_운영규정.md
    ├── HR-015_채용_온보딩_프로세스.md
    ├── IT-010_원격근무_VPN_접속가이드.md
    ├── FIN-003_경비처리_규정.md
    ├── SEC-001_정보보안_관리규정.md
    └── ADM-005_회의실_예약안내.md
```

## 트러블슈팅

| 증상 | 해결 방법 |
|------|----------|
| `az login` 실패 | Azure CLI가 설치되었는지 확인: `az version`. 브라우저 인증 창이 뜨지 않으면 `az login --use-device-code` 시도 |
| `pip install` 시 RC 패키지 못 찾음 | `pip install --pre -r demo/requirements.txt` — `--pre` 플래그 필수 |
| `python3.12` 명령을 찾을 수 없음 | Python 설치 확인: `python3 --version`. Windows에서는 `py -3.12` 사용 |
| 가상환경이 활성화되었는지 확인 | 터미널에서 `which python` (macOS/Linux) 또는 `where python` (Windows) 실행 → `.venv` 경로가 표시되어야 함 |
| `streamlit run` 후 브라우저가 열리지 않음 | 브라우저에서 직접 http://localhost:8501 접속 |
| `FOUNDRY_PROJECT_ENDPOINT` 관련 에러 | `demo/.env` 파일에 올바른 엔드포인트가 입력되었는지 확인. 형식: `https://<name>.services.ai.azure.com/api/projects/<id>` |
| RAG 시나리오에서 `Unauthorized` 에러 | AI Search 서비스에 "Search Index Data Reader" RBAC 역할이 할당되었는지 확인 (4-1단계 참고) |
| RAG 시나리오에서 `Forbidden` 에러 | AI Search 서비스의 인증 모드를 확인: `az search service show --name <서비스명> --resource-group <RG>`에서 `authOptions`가 `apiKeyOnly`이면 RBAC 불가. `az search service update --name <서비스명> --resource-group <RG> --auth-options aadOrApiKey --aad-auth-failure-mode http403`으로 변경 |
| Blob 업로드 시 권한 오류 | `--auth-mode login` 추가, 또는 스토리지 계정에 "Storage Blob Data Contributor" 역할 할당 |
| Knowledge Base에서 스토리지 계정이 안 보임 | Foundry 프로젝트와 스토리지 계정이 같은 구독에 있는지 확인 |
| 멀티 에이전트에서 `Concurrent executions are not allowed` | `create_workflow_agent()`에 `@st.cache_resource`가 적용되어 있지 않은지 확인. `WorkflowAgent`는 내부 실행 상태를 추적하므로 캐시 금지 — 매 요청마다 새 인스턴스 생성 필요 |
| Windows PowerShell 실행 정책 오류 | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` 실행 후 다시 시도 |

## Foundry Agent Service SDK 지원 현황

> **참고**: 이 데모는 **Microsoft Agent Framework**(`agent-framework-core`)를 사용합니다.
> Foundry Agent Service SDK(`azure-ai-agents`)는 아래 기능이 아직 SDK에서 지원되지 않아 사용하지 않습니다.
> 해당 기능이 GA되면 Foundry Agent Service 기반 시나리오를 추가할 예정입니다.

| 기능 | Agent Framework | Foundry Agent Service SDK | 비고 |
|------|:---:|:---:|------|
| **Foundry IQ (Knowledge Base)** | ✅ `knowledge_base_name`으로 직접 연결 | ❌ AI Search 인덱스 수동 지정 필요 | SDK에 KB 추상화 없음 |
| **멀티 에이전트 워크플로우** | ✅ `WorkflowBuilder` (명시적 그래프) | ❌ `ConnectedAgentTool`만 제공 | 명시적 라우팅/체인/분기 불가 |
| **MCP 도구 (로컬)** | ✅ `MCPStdioTool` (로컬 subprocess) | ❌ `McpTool` (원격 URL만 지원) | 로컬 stdio 연결 불가 |

> ⚠️ 위 기능들은 **Foundry Portal(UI)**에서는 일부 지원되지만, **Python SDK**에는 아직 반영되지 않은 상태입니다. (2026년 3월 기준, `azure-ai-agents==1.2.0b5`)

## 이 프로젝트에서 배울 수 있는 것

### 바이브 코딩 (GitHub Copilot 커스터마이징)

| 주제 | 배울 수 있는 내용 | 참고 파일 |
|------|-------------------|----------|
| **글로벌 인스트럭션** | 프로젝트 전체에 적용되는 기술 스택·코드 패턴·SDK 사용법 정의 | `.github/copilot-instructions.md` |
| **파일 패턴 인스트럭션** | `applyTo`로 특정 파일 유형에만 자동 적용되는 규칙 작성 | `.github/instructions/*.md` |
| **재사용 프롬프트** | 반복 작업(도구 추가, 시나리오 추가)을 템플릿화하여 `/이름`으로 호출 | `.github/prompts/*.md` |
| **커스텀 에이전트** | 코드 리뷰어·트러블슈터 등 역할별 AI 에이전트를 `@이름`으로 호출 | `.github/agents/*.md` |
| **커스텀 스킬** | SDK 코드 생성, 마이그레이션 가이드 등 도메인 지식을 자동 로드 또는 `/스킬명`으로 명시적 호출 | `.github/skills/*/SKILL.md` |
| **Copilot CLI 연동** | 터미널에서 `.github/` 설정을 활용한 바이브 코딩 워크플로우, IDE와 CLI 비교 | README 내 "Copilot CLI로 바이브 코딩하기" 섹션 |
| **공용 vs. 전용 분리** | 재사용 가능한 공통 규칙과 프로젝트 종속 규칙을 분리하는 전략 | README 내 재사용 범위 표 |

### 멀티 에이전트 워크플로우 (Microsoft Foundry)

| 주제 | 배울 수 있는 내용 | 참고 코드 |
|------|-------------------|----------|
| **RAG 패턴** | Foundry IQ(Knowledge Base) + `AzureAISearchContextProvider` 연동 | `demo/app.py` — `create_rag_agent()` |
| **MCP 도구 호출** | `MCPStdioTool`로 FastMCP 서버에 stdio 연결, 도구 정의 방법 | `demo/mcp_server.py` |
| **워크플로우 빌더** | `WorkflowBuilder` + `AgentExecutor` + `Case`/`Default`로 에이전트 그래프 구성 | `demo/app.py` — `create_workflow_agent()` |
| **순차 파이프라인** | `add_chain()`으로 RAG → Tool → Summarizer 순서 실행 | `demo/app.py` — BOTH 경로 |
| **비동기/스트리밍** | Streamlit 동기 환경에서 비동기 에이전트를 스트리밍으로 실행하는 패턴 | `demo/app.py` — `stream_agent()` |
| **Streamlit 캐싱** | `@st.cache_resource` 적용 대상과 `WorkflowAgent` 캐시 금지 사유 | `demo/app.py` |

---

## 커스터마이징 가이드

### Foundry Agent Service SDK v2 마이그레이션

Foundry Agent Service SDK(`azure-ai-agents`)가 멀티 에이전트 워크플로우와 Foundry IQ를 정식 지원하게 되면, 다음 파일들을 수정합니다:

| 수정 대상 | 변경 내용 |
|----------|----------|
| `demo/requirements.txt` | `agent-framework-*` 패키지를 `azure-ai-agents>=2.x`로 교체 |
| `demo/app.py` | import 경로 변경: `agent_framework` → `azure.ai.agents` SDK v2 클래스. `Agent`, `WorkflowBuilder`, `AzureAISearchContextProvider` 등을 SDK v2 API로 교체 |
| `demo/app.py` | 클라이언트 생성: `AzureAIAgentClient` → SDK v2의 클라이언트 클래스로 변경 |
| `demo/app.py` | RAG: `AzureAISearchContextProvider(knowledge_base_name=...)` → SDK v2의 Knowledge Base 연결 API로 변경 |
| `demo/app.py` | MCP: `MCPStdioTool` → SDK v2의 MCP 도구 클래스로 변경 (로컬 stdio 지원 여부 확인) |
| `demo/app.py` | 멀티 에이전트: `WorkflowBuilder` + `AgentExecutor` + `Case`/`Default` → SDK v2의 워크플로우 API로 변경 |
| `.github/copilot-instructions.md` | SDK import 경로 매핑, WorkflowBuilder API 사용법, 코드 패턴을 SDK v2 기준으로 갱신 |
| `.github/prompts/*.prompt.md` | 코드 템플릿의 import 경로와 클래스명을 SDK v2 기준으로 갱신 |
| `.github/agents/debugger.agent.md` | 진단 체크리스트의 SDK 관련 항목을 SDK v2 기준으로 갱신 |
| README.md | "Foundry Agent Service SDK 지원 현황" 표 갱신, 설치 명령어에서 `--pre` 플래그 제거 검토 |

### 다른 업종 데모로 변경 (예: 제조)

이 데모를 제조업 등 다른 업종에 맞게 변경하려면, 다음 파일들을 수정합니다:

| 수정 대상 | 변경 내용 | 예시 (제조) |
|----------|----------|------------|
| `docs/*.md` | 사내 문서를 해당 업종 문서로 교체 | `MFG-001_생산라인_운영매뉴얼.md`, `QC-002_품질검사_기준서.md`, `SAF-003_안전관리_규정.md` |
| `demo/mock_data.json` | 업무 도구의 mock 데이터를 업종에 맞게 변경. 최상위 4개 키(`calendar`, `emails`, `tasks`, `sales`)의 항목 내용 교체 | `calendar`: 생산 회의·설비 점검 일정, `tasks`: 생산 오더·품질 검사 작업, `sales` → `production`: 라인별 생산량·불량률·가동률 |
| `demo/mcp_server.py` | MCP 도구 함수를 업종 업무에 맞게 추가/변경 | `get_production_status()`, `get_defect_rate()`, `get_equipment_schedule()` |
| `demo/app.py` | 시나리오 이름·설명·예시 질문을 업종에 맞게 변경 | "오늘 A라인 생산 현황은?", "이번 달 불량률 추이 알려줘", "설비 점검 일정 확인해줘" |
| `demo/app.py` | 에이전트 시스템 프롬프트를 업종 맥락에 맞게 수정 | "당신은 제조 현장 업무를 지원하는 AI 어시스턴트입니다" |
| `.github/copilot-instructions.md` | mock 데이터 스키마, 시나리오 설명, 예시 질문을 업종 기준으로 갱신 | `sales` 키를 `production`으로 변경, 제품 카테고리를 생산 라인명으로 변경 |
| Blob Storage | 4단계에서 업로드하는 문서를 업종 문서로 교체 | 생산 매뉴얼, 품질 기준서, 안전 규정 등 |
| Knowledge Base | 5단계에서 KB 이름을 업종에 맞게 변경 (예: `manufacturing-docs-kb`) | `.env`의 `KNOWLEDGE_BASE_NAME` 값도 함께 변경 |

> **핵심 포인트**: 코드 구조(`Agent`, `WorkflowBuilder`, `MCPStdioTool`)는 그대로 유지하고, **데이터와 프롬프트만 교체**하면 됩니다. `.github/` 하위 Copilot 설정 파일도 함께 갱신하면 Copilot이 새로운 업종 맥락에 맞는 코드를 생성합니다.

## 참고 자료

### GitHub Copilot CLI

- [GitHub Copilot CLI 공식 문서](https://docs.github.com/copilot/concepts/agents/about-copilot-cli)
- [GitHub Copilot CLI 저장소](https://github.com/github/copilot-cli)

### Microsoft Foundry & Agent Framework

- [Microsoft Foundry 공식 문서](https://learn.microsoft.com/azure/ai-foundry/)
- [Microsoft Agent Framework (GitHub)](https://github.com/microsoft/agent-framework)
- [Azure AI Search — RAG 패턴](https://learn.microsoft.com/azure/search/retrieval-augmented-generation-overview)

### GitHub Copilot 커스텀 설정

- [Copilot Instructions 공식 문서](https://docs.github.com/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)
- [Copilot Prompt Files 공식 문서](https://docs.github.com/copilot/customizing-copilot/adding-repository-prompt-files-for-github-copilot)
- [Copilot Agent Mode 공식 문서](https://docs.github.com/copilot/using-github-copilot/using-copilot-coding-agent)

### MCP (Model Context Protocol)

- [MCP 사양](https://modelcontextprotocol.io/)
- [FastMCP (Python)](https://github.com/jlowin/fastmcp)

## 라이선스

MIT License — 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.
