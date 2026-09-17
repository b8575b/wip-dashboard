# TASK-001 · GitHub 리포지토리 및 프로젝트 기본 구조 생성

| 항목 | 내용 |
|------|------|
| 상태 | todo |
| 우선순위 | high |
| 예상 시간 | 30분 |
| 의존 | 없음 |

## 목표

GitHub에 리포지토리를 생성하고, 이후 개발에 필요한 기본 파일 구조를 준비한다.

## 완료 조건

- [ ] GitHub 리포지토리 생성 (Public 또는 Private)
- [ ] `.gitignore` — `.streamlit/secrets.toml`, `__pycache__/`, `.env` 포함
- [ ] `requirements.txt` 초안 작성 (streamlit, supabase, pandas, plotly)
- [ ] `README.md` — 프로젝트 한 줄 설명 및 로컬 실행 방법 기재
- [ ] 초기 커밋 및 push 완료

## 작업 내용

```
프로젝트 루트/
├── app.py                  # (다음 task에서 생성)
├── requirements.txt
├── README.md
├── CLAUDE.md
├── .gitignore
└── .streamlit/
    └── secrets.toml        # 로컬 전용, git 제외
```

### .gitignore 핵심 항목

```
.streamlit/secrets.toml
__pycache__/
*.pyc
.env
.DS_Store
```

### requirements.txt 초안

```
streamlit>=1.35.0
supabase>=2.0.0
pandas>=2.0.0
plotly>=5.0.0
```

## 주의사항

- secrets.toml이 절대 커밋되지 않는지 `.gitignore` 설정 후 반드시 확인
- Streamlit 1.35+ 이상이어야 `st.dialog`, `st.dataframe on_select` 사용 가능
