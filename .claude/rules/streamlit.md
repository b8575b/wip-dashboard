# Streamlit 개발 규칙

## 단일 파일 앱 구조를 유지한다

진입점은 `app.py` 하나다. React/Vue 같은 별도 프론트엔드를 추가하지 않는다.
UI 컴포넌트가 커지면 `ui/` 하위 모듈로 분리하되, `app.py`에서 import하는 구조를 유지한다.

## Supabase 접속 정보는 st.secrets로만 읽는다

```python
# 올바른 방법
from db import get_client
client = get_client()

# db.py
import streamlit as st
from supabase import create_client

@st.cache_resource
def get_client():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
```

URL과 Key를 코드에 직접 쓰거나 환경변수 `.env`에서 읽지 않는다.

## 캐싱을 적절히 사용한다

| 대상 | 캐시 유형 |
|------|-----------|
| Supabase 클라이언트 | `@st.cache_resource` |
| WIP 데이터 조회 함수 | `@st.cache_data` (TTL 설정 권장) |
| Pandas 집계 함수 | `@st.cache_data` |

매 렌더링마다 Supabase에 쿼리를 날리지 않는다.

## 선택 상태는 st.session_state로 관리한다

Matrix 셀 선택 → Lot 상세 팝업 흐름에서 선택된 product_name, step_name을
`st.session_state`에 저장하고 dialog 표시 여부를 결정한다.

```python
if "selected" not in st.session_state:
    st.session_state.selected = None
```

## Lot 상세 팝업은 st.dialog로 구현한다

```python
@st.dialog("Lot 상세", width="large")
def lot_dialog(product, step):
    ...
```

`st.dialog`는 Streamlit 1.35+에서 사용 가능하다.
버전 제약이 있으면 `st.expander`로 대체하되, 반드시 TASK-012 노트에 기록한다.

## Matrix 셀 선택 방식

TASK-009가 `pending_decision` 상태다. 결정 전까지:
- `st.dataframe(on_select=...)` 방식과 selectbox 방식 모두 허용
- 어느 방식이든 **Product → STEP → Lot 팝업 3단계 흐름**은 유지한다
- 방식을 결정하면 TASK-009를 `done`으로 업데이트한다

## 데모 데이터만 사용한다

`sources/rawdata.csv`의 가상 데이터(PRODUCT_A, PRODUCT_B 등)만 사용한다.
실제 제조 현장 데이터, 실제 Lot ID, 실제 설비 ID를 코드에 포함하지 않는다.

## 필터 구현 시 집계와 동기화한다

Product/STEP/Status/Hold 필터를 적용할 때 Matrix 집계와 Lot 상세 조회 모두
동일한 필터 조건이 적용되어야 한다.
필터는 원본 DataFrame에 적용한 뒤 집계 함수에 넘긴다.
