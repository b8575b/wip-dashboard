import streamlit as st
import pandas as pd
from db import get_client
from data.fetch import fetch_wip_data
from data.aggregate import build_wip_matrix

_ALL_STATUSES = ["RUN", "WAIT", "HOLD"]
_DISPLAY_COLS = [
    "lot_id", "product_name", "step_name", "quantity",
    "equipment", "input_time", "waiting_hours", "status", "hold_yn",
]


def _reset_selection():
    st.session_state["selected_product"] = None
    st.session_state["selected_step"] = None


def _close_dialog():
    _reset_selection()
    st.session_state["df_version"] = st.session_state.get("df_version", 0) + 1


@st.dialog("Lot 상세정보", width="large")
def _show_lot_dialog(product: str, step: str, lot_df: pd.DataFrame):
    st.caption(f"Product: **{product}** | STEP: **{step}**")
    display = lot_df[[c for c in _DISPLAY_COLS if c in lot_df.columns]].copy()
    display = display.sort_values("waiting_hours", ascending=False, na_position="last")
    display = display.reset_index(drop=True)
    if display.empty:
        st.info("해당 조건의 재공이 없습니다.")
        return
    if "hold_yn" not in display.columns:
        display["hold_yn"] = "N"

    def _highlight_hold(row):
        color = "background-color: #fff3cd;" if row["hold_yn"] == "Y" else ""
        return [color] * len(row)

    lot_styled = display.style.apply(_highlight_hold, axis=1)
    st.dataframe(lot_styled, use_container_width=True, hide_index=True)
    st.caption(f"총 {len(display)}건 · Hold {(display['hold_yn'] == 'Y').sum()}건")
    if st.button("닫기"):
        _close_dialog()
        st.rerun()


st.set_page_config(
    page_title="WIP 재공 현황판",
    page_icon=":material/factory:",
    layout="wide",
)

st.title(":material/factory: WIP 재공 현황판")
st.caption("제품별·공정 STEP별 재공(WIP) 현황을 확인하고 Lot 상세정보를 조회합니다.")

if "db_checked" not in st.session_state:
    try:
        client = get_client()
        client.table("wip_inventory").select("id").limit(1).execute()
        st.session_state.db_checked = True
    except KeyError:
        st.error("Supabase 접속 정보(secrets.toml)가 설정되지 않았습니다.")
        st.stop()
    except Exception:
        st.error("Supabase 연결에 실패했습니다. 관리자에게 문의하세요.")
        st.stop()

if "selected_product" not in st.session_state:
    st.session_state["selected_product"] = None
if "selected_step" not in st.session_state:
    st.session_state["selected_step"] = None
if "df_version" not in st.session_state:
    st.session_state["df_version"] = 0

raw_df = fetch_wip_data()

with st.sidebar:
    st.header(":material/tune: 필터")
    if not raw_df.empty:
        all_products = sorted(raw_df["product_name"].dropna().unique().tolist())
        step_order_map = raw_df.groupby("step_name")["step_order"].min()
        all_steps = step_order_map.sort_values().index.tolist()
    else:
        all_products, all_steps = [], []
    sel_products = st.multiselect(
        "Product", all_products, default=all_products, on_change=_reset_selection
    )
    sel_steps = st.multiselect(
        "STEP", all_steps, default=all_steps, on_change=_reset_selection
    )
    st.space("small")
    hold_only = st.checkbox("Hold Lot만 보기", value=False, on_change=_reset_selection)
    sel_statuses = st.multiselect(
        "Status", _ALL_STATUSES, default=_ALL_STATUSES,
        disabled=hold_only, on_change=_reset_selection,
    )
    st.space("small")
    lot_input = st.text_area(
        ":material/search: Lot ID 검색",
        placeholder="엑셀에서 복사 후 붙여넣기\n(여러 행 동시 입력 가능)",
        height=120,
    )
    search_lot_ids = {
        token.strip()
        for line in lot_input.splitlines()
        for token in line.split("\t")
        if token.strip()
    }

if raw_df.empty:
    filtered_df = pd.DataFrame()
else:
    mask = pd.Series(True, index=raw_df.index)
    if sel_products:
        mask &= raw_df["product_name"].isin(sel_products)
    if sel_steps:
        mask &= raw_df["step_name"].isin(sel_steps)
    if hold_only:
        mask &= raw_df["hold_yn"] == "Y"
    elif sel_statuses:
        mask &= raw_df["status"].isin(sel_statuses)
    filtered_df = raw_df[mask]

hit_pairs: set = set()
if search_lot_ids and not filtered_df.empty and "lot_id" in filtered_df.columns:
    hit_df = filtered_df[filtered_df["lot_id"].isin(search_lot_ids)]
    hit_pairs = set(zip(hit_df["product_name"], hit_df["step_name"]))

if not filtered_df.empty:
    cols = set(filtered_df.columns)
    qty_total = int(filtered_df["quantity"].fillna(0).sum()) if "quantity" in cols else 0
    hold_count = int((filtered_df["hold_yn"] == "Y").sum()) if "hold_yn" in cols else 0
    long_wait = (
        int((filtered_df["waiting_hours"] >= 24).sum()) if "waiting_hours" in cols else 0
    )
else:
    qty_total = hold_count = long_wait = 0

col1, col2, col3 = st.columns(3)
col1.metric(":material/inventory_2: 전체 WIP", f"{qty_total:,}")
col2.metric(":material/warning: Hold Lot", f"{hold_count}건")
col3.metric(":material/schedule: 장시간 대기(24h+)", f"{long_wait}건")

st.subheader(":material/grid_on: WIP Matrix")
st.caption("셀을 클릭하여 Product와 STEP을 선택하면 Lot 상세정보를 조회합니다.")

matrix = build_wip_matrix(filtered_df)

if search_lot_ids and not hit_pairs:
    st.caption(":material/info: 검색한 Lot ID가 현재 필터 조건에 해당하는 데이터에 없습니다.")

if matrix.empty:
    st.warning("표시할 WIP 데이터가 없습니다.", icon=":material/info:")
else:
    def _style_matrix(df):
        styles = pd.DataFrame("", index=df.index, columns=df.columns)
        styles[df.map(lambda v: pd.notna(v) and v == 0)] = "color: #cccccc;"
        for prod, step in hit_pairs:
            if prod in df.index and step in df.columns:
                styles.loc[prod, step] = (
                    "background-color: #DBEAFE; color: #1E40AF; font-weight: 600;"
                )
        return styles

    matrix_styled = matrix.style.apply(_style_matrix, axis=None)
    df_key = str((sorted(sel_products), sorted(sel_steps), sorted(sel_statuses), hold_only,
                  st.session_state.get("df_version", 0)))
    event = st.dataframe(
        matrix_styled,
        on_select="rerun",
        selection_mode="single-cell",
        use_container_width=True,
        key=df_key,
    )
    selection = event.selection
    cells = selection.cells if hasattr(selection, "cells") else []
    if cells:
        row_pos, col_label = cells[0]
        if 0 <= row_pos < len(matrix.index) and col_label in matrix.columns:
            st.session_state["selected_product"] = matrix.index[row_pos]
            st.session_state["selected_step"] = col_label
        else:
            _reset_selection()
    else:
        _reset_selection()

sel_prod = st.session_state.get("selected_product")
sel_step = st.session_state.get("selected_step")
if (sel_prod is not None and sel_step is not None
        and not filtered_df.empty
        and sel_prod in matrix.index
        and sel_step in matrix.columns):
    lot_df = filtered_df[
        (filtered_df["product_name"] == sel_prod)
        & (filtered_df["step_name"] == sel_step)
    ]
    _show_lot_dialog(sel_prod, sel_step, lot_df)
