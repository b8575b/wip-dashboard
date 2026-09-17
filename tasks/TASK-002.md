# TASK-002 · Streamlit 기본 앱 구성 및 로컬 실행 확인

## 쉬운 설명

Streamlit이라는 웹 앱 프레임워크를 사용해 시작 페이지를 만들고, 그것이 제대로 작동하는지 확인하는 작업입니다. 페이지 제목, 설명 텍스트를 추가한 기본 골격을 작성한 뒤 `streamlit run` 명령으로 로컬 컴퓨터에서 실행해 오류 없이 브라우저에 표시되는지 검증합니다.

## 관련 파일

| 파일 경로 | 상태 | 이 태스크에서의 역할 |
|-----------|------|---------------------|
| `app.py` | 생성됨 | Streamlit 진입점 — 페이지 제목, 레이아웃, 기본 콘텐츠 포함 |
| `db.py` | 기존 파일 | Supabase 클라이언트 초기화 — 현 단계에서는 미사용, TASK-005에서 활성화 |
| `requirements.txt` | 기존 파일 | 패키지 의존성 — `streamlit` 포함 확인 필수 |
| `.gitignore` | 기존 파일 | 버전 관리 설정 — `.streamlit/secrets.toml` 제외 확인 |
| `README.md` | 기존 파일 | 프로젝트 개요 — 사용자가 로컬 실행 방법 참고 |

| 항목 | 내용 |
|------|------|
| 상태 | todo |
| 우선순위 | high |
| 예상 시간 | 30분 |
| 의존 | TASK-001 |

## 목표

`app.py`를 생성하고 페이지 기본 골격을 구성한 뒤 로컬에서 정상 실행되는지 확인한다.

## 완료 조건

- [ ] `app.py` 생성
- [ ] `st.set_page_config`으로 페이지 제목, 레이아웃 설정 (`layout="wide"`)
- [ ] 페이지 상단에 타이틀과 설명 표시
- [ ] `streamlit run app.py` 실행 시 브라우저에서 오류 없이 렌더링

## 작업 내용

```python
import streamlit as st

st.set_page_config(
    page_title="WIP 재공 현황판",
    page_icon="🏭",
    layout="wide"
)

st.title("WIP 재공 현황판")
st.caption("제품별·공정 STEP별 재공(WIP) 현황을 확인하고 Lot 상세정보를 조회합니다.")

# 이후 섹션: WIP Matrix (TASK-008에서 구현)
st.info("데이터를 불러오는 중입니다...")
```

## 로컬 실행 방법

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 주의사항

- 이 단계에서는 실제 데이터 연결 없이 UI 골격만 확인한다
- Supabase 연결 코드는 TASK-005에서 추가
- `db.py`는 TASK-005 범위로 이 태스크보다 먼저 생성됐으나 app.py에서 import하지 않으며
  TASK-002 done_when 근거에서 제외한다
