import streamlit as st
import pandas as pd

_REQUIRED = {"product_name", "step_name", "step_order", "quantity"}


@st.cache_data
def build_wip_matrix(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(index=pd.Index([], name="Product"))

    missing = _REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")

    # step_name별 최솟값 step_order 기준 정렬 — 동일 step_name의 order 불일치 방지
    step_cols = (
        df.groupby("step_name")["step_order"].min()
        .sort_values().index.tolist()
    )

    matrix = df.pivot_table(
        index="product_name",
        columns="step_name",
        values="quantity",
        aggfunc="sum",
        fill_value=0,
    )
    matrix = matrix.reindex(columns=step_cols, fill_value=0)
    matrix.index.name = "Product"
    matrix.columns.name = None
    return matrix


if __name__ == "__main__":
    sample = pd.DataFrame({
        "product_name": ["A", "A", "B"],
        "step_name": ["STEP_010", "STEP_020", "STEP_010"],
        "step_order": pd.array([10, 20, 10], dtype="Int64"),
        "quantity": pd.array([20, 30, 40], dtype="Int64"),
    })
    m = build_wip_matrix(sample)
    assert not m.isna().any().any(), "NaN found"
    assert list(m.columns) == ["STEP_010", "STEP_020"], f"bad columns: {list(m.columns)}"
    assert m.index.name == "Product"
    assert int(m.loc["A", "STEP_010"]) == 20
    assert int(m.loc["B", "STEP_020"]) == 0
    print("검증 OK\n", m)
