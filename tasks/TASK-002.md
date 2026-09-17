# TASK-002 · Streamlit 기본 앱 구성 및 로컬 실행 확인

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
