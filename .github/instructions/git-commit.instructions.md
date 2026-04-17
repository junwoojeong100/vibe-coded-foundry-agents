---
applyTo: "**"
---

<!-- 🌐 공용: 다른 프로젝트에서도 .github/instructions/에 복사하여 재사용할 수 있습니다. -->

# Git 커밋 메시지 컨벤션

> 이 규칙은 한국어 작성 컨벤션(`korean.instructions.md`)보다 **우선 적용**됩니다.
> 커밋 메시지는 오픈소스 관례·CI 도구·외부 기여자와의 호환성을 위해 영어로 통일합니다.

## 언어

- 모든 커밋 메시지(제목·본문)는 **영어**로 작성한다.
- 코드 주석·docstring·README 등 나머지 문서는 기존대로 한국어를 유지한다.

## 형식 (Conventional Commits)

- 형식: `type(scope): subject`
  - `scope`는 선택 사항이며, 영향 범위를 나타낸다 (예: `readme`, `mcp`, `rag`).
- 사용 가능한 `type`:
  - `feat` — 새 기능
  - `fix` — 버그 수정
  - `docs` — 문서만 변경
  - `refactor` — 기능 변화 없는 리팩터링
  - `test` — 테스트 추가/수정
  - `chore` — 빌드·설정·의존성 등 부수 작업
  - `perf` — 성능 개선
  - `style` — 포매팅·세미콜론 등 (코드 동작 변화 없음)

## 작성 규칙

- 제목은 **50자 이내**, **명령형 현재 시제**(imperative mood)로 작성한다.
  - 좋은 예: `docs: clarify README title`
  - 나쁜 예: `docs: clarified README title` / `docs: README 제목 명확화`
- 제목 끝에 마침표를 붙이지 않는다.
- 본문이 필요한 경우 제목과 한 줄 띄우고, **72자 단위로 줄바꿈**하며 "무엇을/왜"를 설명한다 ("어떻게"는 diff로 충분).
- 본문 불릿은 `-`를 사용한다.

## 트레일러

- `Co-authored-by:` 등 트레일러는 본문과 한 줄 띄우고 맨 아래에 둔다.
- 이 프로젝트에서는 다음 트레일러를 항상 포함한다:

  ```
  Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
  ```

## 예시

```
docs: clarify README title and explain Agent Framework choice

- Rename title to highlight vibe coding with GitHub Copilot
- Note that Microsoft Foundry multi-agent workflow is in Public
  Preview while Agent Framework is GA, which is why the demo is
  built on Agent Framework

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## PR 생성 워크플로우

- 기능/수정 브랜치(`fix/*`, `feat/*`, `docs/*` 등)에 커밋을 **푸시한 직후에는 항상 PR을 자동으로 생성**한다.
  - 이미 해당 브랜치로 열린 PR이 있으면 새로 만들지 않고 그대로 두고, 사용자에게 PR URL만 안내한다.
  - `main` 브랜치에 직접 푸시하는 경우에는 PR을 만들지 않는다.
- PR 생성은 `gh pr create --base main --head <branch>`를 사용한다.
- PR 제목과 본문도 커밋 메시지와 동일하게 **영어**로 작성한다.
  - 제목: Conventional Commits 스타일 (`type: subject`)
  - 본문: `## Summary`, `## Commits`, 필요 시 `## Notes` 섹션으로 구성
- PR 생성 후에는 PR URL을 사용자에게 안내한다.
