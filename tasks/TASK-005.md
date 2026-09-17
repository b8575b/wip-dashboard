# TASK-005 · 앱-Supabase 연결 설정 및 연결 테스트

| 항목 | 내용 |
|------|------|
| 상태 | waiting |
| 우선순위 | high |
| 예상 시간 | 30분 |
| 의존 | TASK-002, TASK-003 |

## 목표

`app.py`에서 Supabase 클라이언트를 초기화하는 모듈을 작성하고, 간단한 SELECT로 연결을 검증한다.

## 완료 조건

- [ ] `db.py` (또는 `data/client.py`) 에 Supabase 클라이언트 초기화 함수 작성
- [ ] `app.py`에서 import하여 연결 테스트 성공
- [ ] 연결 실패 시 사용자에게 명확한 오류 메시지 표시

## 작업 내용

```python
# db.py
import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)
```

`app.py`에서 연결 확인:

```python
from db import get_client

client = get_client()
# 연결 테스트: 1건만 조회
test = client.table("wip_inventory").select("id").limit(1).execute()
if test.data:
    st.success("Supabase 연결 성공")
else:
    st.error("데이터를 불러올 수 없습니다.")
```

## 주의사항

- `st.cache_resource`를 사용해 Supabase 클라이언트를 앱 세션 전반에 걸쳐 재사용
- Streamlit Community Cloud 배포 시 `st.secrets`는 서비스 내 Secrets 설정에서 자동 주입
