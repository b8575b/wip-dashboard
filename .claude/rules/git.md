# Git 워크플로우 규칙

## main 브랜치에서 직접 개발하지 않는다

`session_start.py` hook이 세션 시작 시 브랜치를 표시한다.
`main`이면 즉시 `dev` 브랜치로 전환한다:

```bash
git checkout dev       # 기존 dev로 전환
git checkout -b dev    # 없으면 생성
```

## backlog.json 변경은 자동 commit된다

`post_write.py` hook이 `backlog.json` Write/Edit 후 `git commit`을 자동 실행한다.
수동 commit 불필요. `done` 감지 시 `git push`까지 자동 실행.

자동 commit 메시지: `chore: update backlog [auto]`
done 시: `feat: complete - <태스크 제목> [auto]`

## 수동 commit 메시지 형식

```
feat:     새 기능
fix:      버그 수정
chore:    설정·빌드·리소스 변경
docs:     문서 변경
refactor: 코드 구조 변경 (기능 변화 없음)
```

hook 자동 commit은 `[auto]` 접미사가 붙는다.

## secrets는 절대 commit하지 않는다

`git_safety.py` hook이 `git add` 명령을 검사한다:
- `secrets.toml`을 명시적으로 추가하면 → 차단
- `git add -A` + `secrets.toml`이 `.gitignore` 미등록 → 경고

`.streamlit/secrets.toml`은 `.gitignore`에 반드시 포함.

## 적용 방식

| 규칙 | 지침 | Hook |
|------|:----:|:----:|
| main 브랜치 직접 개발 금지 | ✓ | (session_start 안내) |
| secrets.toml commit 금지 | | ✓ git_safety |
| backlog.json 자동 commit | | ✓ post_write |
| commit 메시지 형식 | ✓ | |
