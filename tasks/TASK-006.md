# TASK-006 · WIP 데이터 조회 모듈 작성

| 항목 | 내용 |
|------|------|
| 상태 | waiting |
| 우선순위 | high |
| 예상 시간 | 30분 |
| 의존 | TASK-005, TASK-004 |

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
