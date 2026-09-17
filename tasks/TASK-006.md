# TASK-006 · WIP 데이터 조회 모듈 작성

| 항목 | 내용 |
|------|------|
| 상태 | waiting |
| 우선순위 | high |
| 예상 시간 | 30분 |
| 의존 | TASK-005, TASK-004 |

## 쉬운 설명

Supabase에 저장된 재공 데이터를 앱에서 읽어오는 함수를 만드는 단계입니다. 마치 창고에서 재고 현황을 조회하는 것처럼, 클라우드 데이터베이스에 저장된 모든 WIP 정보(제품명, STEP, Lot, 수량 등)를 한 번에 가져와서 표로 정리하는 역할을 합니다. 캐싱 기능도 적용해서 같은 요청을 5분 이내에 반복할 때는 더 빠르게 응답합니다. 이 함수가 완성되면 대시보드에서 실제 WIP 데이터를 표시할 수 있게 됩니다.

## 관련 파일

| 파일 경로 | 상태 | 이 태스크에서의 역할 |
|-----------|------|---------------------|
| `data/fetch.py` | 생성 예정 | WIP 데이터 조회 함수 구현 — `fetch_wip_data()` 함수가 Supabase에서 데이터를 조회하여 DataFrame으로 변환 |
| `db.py` | 기존 파일 | Supabase 클라이언트 제공 — `get_client()` 함수를 통해 데이터베이스 연결 객체를 전달 |
| `sources/rawdata.csv` | 참조 파일 | 로컬 테스트 데이터 — 개발 중 데이터 스키마와 형식 확인용 |
| `requirements.txt` | 확인 필요 | 의존 라이브러리 — pandas, supabase 패키지 포함 여부 확인 |

## 목표

Supabase에서 `wip_inventory` 전체 데이터를 조회하여 pandas DataFrame으로 반환하는 함수를 작성한다.

## 완료 조건

- [ ] `fetch_wip_data()` 함수 구현 완료
- [ ] 반환 DataFrame의 컬럼 타입이 올바르게 변환됨 (`quantity`: int, `input_time`: datetime 등)
- [ ] `st.cache_data(ttl=300)`으로 5분 캐싱 적용
- [ ] 빈 결과 또는 오류 시 빈 DataFrame 반환 (앱이 크래시되지 않아야 함)

## 작업 내용

```python
# data/fetch.py
import streamlit as st
import pandas as pd
from db import get_client

@st.cache_data(ttl=300)
def fetch_wip_data() -> pd.DataFrame:
    client = get_client()
    response = client.table("wip_inventory").select("*").execute()
    if not response.data:
        return pd.DataFrame()
    df = pd.DataFrame(response.data)
    df["input_time"] = pd.to_datetime(df["input_time"])
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["quantity"] = df["quantity"].astype(int)
    df["step_order"] = df["step_order"].astype(int)
    return df
```

## 주의사항

- Supabase 기본 응답은 최대 1000건 제한이 있다. 데이터가 1000건을 초과하면 페이지네이션 처리 필요
- ttl은 데이터 변경 빈도에 따라 조정 가능
