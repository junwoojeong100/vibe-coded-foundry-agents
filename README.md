# Microsoft Foundry 엔터프라이즈 AI 데모

> **GitHub Copilot**으로 생성한 **Microsoft Foundry** 기반 엔터프라이즈 AI 에이전트 데모
>
> `.github/` 디렉토리에 배치한 **9개의 커스텀 설정 파일**(인스트럭션·프롬프트·에이전트)만으로
> GitHub Copilot이 프로젝트의 기술 스택·코드 패턴·SDK 사용법을 이해하고,
> 소스코드·설정파일·MCP 도구를 직접 생성합니다.

## GitHub Copilot 커스텀 설정

이 프로젝트의 소스코드(`demo/app.py`, `demo/mcp_server.py` 등)는 **GitHub Copilot이 `.github/` 하위 md 파일을 참조하여 생성**한 것입니다.
`.github/` 디렉토리에 **9개의 md 파일**을 배치하여 Copilot의 코드 생성·리뷰·디버깅 품질을 제어합니다.

### 파일 유형별 동작 방식

| 파일 유형 | 위치 | 호출 방법 | 적용 방식 |
|----------|------|----------|----------|
| **글로벌 인스트럭션** | `.github/copilot-instructions.md` | 없음 | ✅ 자동 — 모든 Copilot 요청에 항상 포함 |
| **파일 패턴 인스트럭션** | `.github/instructions/*.instructions.md` | 없음 | ✅ 자동 — `applyTo` 패턴에 매칭되는 파일 작업 시 포함 |
| **재사용 프롬프트** | `.github/prompts/*.prompt.md` | 채팅에서 `#파일명` 입력 | 🔘 수동 |
| **커스텀 에이전트** | `.github/agents/*.agent.md` | 채팅에서 `@에이전트명` 입력 | 🔘 수동 |

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
├── prompts/                         ← 🔒 #이름으로 수동 호출
│   ├── add-scenario.prompt.md       ← #add-scenario
│   ├── create-tool.prompt.md        ← #create-tool
│   └── review-code.prompt.md        ← #review-code
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

| # | 시나리오 | 패턴 | 설명 |
|---|---------|------|------|
| 1 | **📄 사내 문서 Q&A** | RAG | Foundry IQ(Knowledge Base) 기반 문서 검색 |
| 2 | **🔧 업무 도구 에이전트** | MCP | MCPStdioTool → mcp_server.py 연결, MCP 프로토콜로 도구 호출 |
| 3 | **🤖 멀티 에이전트 워크플로우** | WorkflowBuilder | 분류기 → Switch 라우팅 → RAG/MCP 서브 에이전트 |

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

## 설정 가이드

### 사전 요구 사항

- **Python 3.12+** — [다운로드](https://www.python.org/downloads/)
- **Git** — [다운로드](https://git-scm.com/downloads)
- **Azure CLI** — [설치 가이드](https://learn.microsoft.com/cli/azure/install-azure-cli)
- **Azure 구독** — [무료 체험 계정 만들기](https://azure.microsoft.com/free/) + Foundry 프로젝트

### 1단계: 로컬 환경 준비

```bash
# 저장소 클론
git clone https://github.com/nicewook/vibe-coding.git
cd vibe-coding

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
| `FOUNDRY_MODEL_DEPLOYMENT_NAME` | ✅ | 모델 배포 이름 | 2단계에서 지정한 배포 이름 |
| `KNOWLEDGE_BASE_NAME` | ✅ | Knowledge Base 이름 | 5단계에서 생성 |

```bash
# Azure 로그인
az login
# 구독이 여러 개인 경우:
# az account set --subscription "<구독 이름 또는 ID>"
```

> **시나리오 2(MCP)만 사용한다면** `FOUNDRY_PROJECT_ENDPOINT`만 설정하고 바로 실행 가능합니다:
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

```
┌───────────────────────────────────────────────────────┐
│                  Microsoft Foundry                     │
│   ┌──────────┐   ┌──────────────┐   ┌──────────────┐ │
│   │ GPT-5.4-2│   │ Foundry IQ   │   │ App Insights │ │
│   │          │   │ (Knowledge   │   │              │ │
│   │          │   │   Base)      │   │              │ │
│   └────┬─────┘   └──────┬───────┘   └──────────────┘ │
│        └───────┬─────────┘                            │
│       Agent Framework SDK                             │
└───────────────┬───────────────────────────────────────┘
                │
    ┌───────────┴───────────┐
    │     Streamlit Demo     │
    │                        │
    │  ┌──────────────────┐  │
    │  │🤖 WorkflowAgent  │  │  ← 시나리오 3
    │  │ (WorkflowBuilder)│  │
    │  └──┬──────────┬────┘  │
    │     │ Switch   │       │
    │  ┌──┴───┐  ┌───┴────┐  │
    │  │📄 RAG│  │🔧 MCP  │  │  ← 시나리오 1, 2
    │  │Agent │  │ Agent  │  │
    │  └──┬───┘  └───┬────┘  │
    │     │          │       │
    │  ┌──┴────┐ ┌───┴────┐  │
    │  │Foundry│ │ MCP    │  │
    │  │IQ     │ │ Server │  │
    │  │(KB)   │ │(stdio) │  │
    │  └───────┘ └────────┘  │
    └────────────────────────┘
```

## 프로젝트 구조

```
vibe-coding/
├── README.md
├── .gitignore
├── docs/                            # 샘플 사내 문서 (Blob Storage 업로드용)
│   ├── HR-001_연차휴가_운영규정.md
│   ├── IT-010_원격근무_VPN_접속가이드.md
│   ├── FIN-003_경비처리_규정.md
│   ├── SEC-001_정보보안_관리규정.md
│   ├── HR-015_채용_온보딩_프로세스.md
│   └── ADM-005_회의실_예약안내.md
├── .github/
│   ├── copilot-instructions.md      # 프로젝트 전용 인스트럭션 (자동 적용)
│   ├── instructions/                # ★ 공통 인스트럭션 (다른 프로젝트에도 재사용 가능)
│   │   ├── python.instructions.md   #   Python 가상환경/코딩 컨벤션
│   │   ├── azure.instructions.md    #   Azure 인증/환경변수/보안
│   │   └── korean.instructions.md   #   한국어 작성 컨벤션
│   ├── prompts/
│   │   ├── create-tool.prompt.md    # 새 도구 함수 생성 프롬프트
│   │   ├── add-scenario.prompt.md   # 새 시나리오 추가 프롬프트
│   │   └── review-code.prompt.md    # 코드 리뷰 프롬프트
│   └── agents/
│       ├── reviewer.agent.md        # 코드 리뷰어 에이전트 (읽기 전용)
│       └── debugger.agent.md        # 트러블슈터 에이전트 (환경/런타임 진단)
└── demo/
    ├── app.py              # Streamlit 데모 앱 (3개 시나리오)
    ├── mcp_server.py       # MCP 서버 (FastMCP, 6개 업무 도구)
    ├── requirements.txt    # 의존성
    └── .env.example        # 환경변수 템플릿
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

- [Microsoft Foundry 공식 문서](https://learn.microsoft.com/azure/ai-foundry/)
- [Microsoft Agent Framework (GitHub)](https://github.com/microsoft/agent-framework)
- [Azure AI Search — RAG 패턴](https://learn.microsoft.com/azure/search/retrieval-augmented-generation-overview)
- [MCP (Model Context Protocol) 사양](https://modelcontextprotocol.io/)
