import streamlit as st
import pandas as pd
from db import get_client

TABLE = "wip_inventory"
_PAGE = 1000


def _fetch_all(client) -> list:
    rows, start = [], 0
    while True:
        resp = client.table(TABLE).select("*").range(start, start + _PAGE - 1).execute()
        batch = resp.data or []
        rows.extend(batch)
        if len(batch) < _PAGE:
            break
        start += _PAGE
    return rows


@st.cache_data(ttl=300)
def fetch_wip_data() -> pd.DataFrame:
    try:
        client = get_client()
        rows = _fetch_all(client)
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        df["input_time"] = pd.to_datetime(df["input_time"], utc=True, errors="coerce")
        df["created_at"] = pd.to_datetime(df["created_at"], utc=True, errors="coerce")
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").astype("Int64")
        df["step_order"] = pd.to_numeric(df["step_order"], errors="coerce").astype("Int64")
        df["waiting_hours"] = pd.to_numeric(df["waiting_hours"], errors="coerce")
        return df
    except Exception:
        return pd.DataFrame()
