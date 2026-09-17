# TASK-005 · 앱-Supabase 연결 설정 및 연결 테스트

| 항목 | 내용 |
|------|------|
| 상태 | waiting |
| 우선순위 | high |
| 예상 시간 | 30분 |
| 의존 | TASK-002, TASK-003 |

## 쉬운 설명

Streamlit 앱이 클라우드 데이터베이스(Supabase)에 안전하게 접속할 수 있도록 설정하는 단계입니다. 마치 앱이 처음 출근하는 직원처럼, 회사 시스템(Supabase)에 접속할 권한(접속 정보)을 부여하고, 실제로 접속이 되는지 간단한 테스트를 해보는 것입니다. 이 단계가 완료되면 이후로 WIP 데이터를 실제로 조회할 수 있습니다.

## 관련 파일

| 파일 경로 | 상태 | 이 태스크에서의 역할 |
|-----------|------|---------------------|
| `db.py` | 기존 파일 | Supabase 클라이언트 초기화 함수 구현 — 접속 정보를 받아 클라이언트를 생성하는 역할 |
| `.streamlit/secrets.toml` | 기존 파일 | Supabase 접속 정보 저장 — URL과 API Key가 로컬에만 보관됨 |
| `app.py` | 수정 필요 | 연결 테스트 코드 추가 — get_client() 함수를 호출하여 연결 검증 |
| `requirements.txt` | 확인 완료 | Supabase 라이브러리(supabase>=2.0.0) 포함 — 이미 등록됨 |

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
