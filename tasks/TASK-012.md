# TASK-012 · Lot 상세 팝업(Dialog) 표시 구현

| 항목 | 내용 |
|------|------|
| 상태 | waiting |
| 우선순위 | high |
| 예상 시간 | 30분 |
| 의존 | TASK-011 |

## 쉬운 설명

사용자가 현황판의 WIP Matrix에서 특정 제품과 공정 STEP이 교차하는 셀을 클릭하면, 그 조건에 해당하는 모든 Lot의 상세 정보(수량, 설비, 투입 시간, 대기 시간, 상태 등)를 팝업 창으로 보여주는 기능입니다. 대기 중인 재공(대기 시간이 긴 것)이 노란색으로 강조되어, 품질 담당자가 어떤 Lot이 오래 기다리고 있고 Hold(보류) 상태인지 한눈에 파악할 수 있습니다.

## 관련 파일

| 파일 경로 | 상태 | 이 태스크에서의 역할 |
|-----------|------|---------------------|
| `app.py` | 기존 파일 | 이 태스크의 주요 산출 위치 — `_show_lot_dialog()` 함수 구현, Matrix 클릭 이벤트 처리 |
| `data/fetch.py` | 기존 파일 | 팝업의 데이터 소스 — `fetch_lot_detail()` 함수 호출 |
| `db.py` | 기존 파일 | Supabase 클라이언트 초기화 — `fetch_lot_detail()` 내부에서 호출 |
| `requirements.txt` | 기존 파일 | Streamlit ≥ 1.35 버전 확인 — `st.dialog` 사용 가능 여부 |
| `sources/rawdata.csv` | 데이터 파일 | 테스트 데이터 기준 — Lot 필드(lot_id, hold_yn, status 등) 구조 |

## 목표

TASK-011에서 조회한 Lot 목록을 `st.dialog`로 표시한다. Hold Lot은 시각적으로 강조하고, 결과가 없을 때 안내 메시지를 표시한다.

## 완료 조건

- [ ] Matrix에서 셀 선택 시 Lot 상세 팝업이 열림
- [ ] 팝업 내 테이블에 9개 필수 컬럼 표시
- [ ] `hold_yn == 'Y'`인 행이 강조 표시됨
- [ ] 결과가 없을 때 "해당 조건의 재공이 없습니다" 메시지 표시
- [ ] 팝업 닫기 후 Matrix 화면으로 복귀

## 작업 내용

```python
# app.py 내 Dialog 섹션

@st.dialog("Lot 상세정보")
def show_lot_detail(product: str, step: str):
    st.caption(f"Product: **{product}** | STEP: **{step}**")
    df = fetch_lot_detail(product, step)
    if df.empty:
        st.info("해당 조건의 재공이 없습니다.")
        return

    # Hold Lot 강조
    def highlight_hold(row):
        color = "background-color: #fff3cd;" if row["hold_yn"] == "Y" else ""
        return [color] * len(row)

    styled = df.style.apply(highlight_hold, axis=1)
    st.dataframe(styled, use_container_width=True, hide_index=True)
    st.caption(f"총 {len(df)}건 · Hold {(df['hold_yn']=='Y').sum()}건")

# 선택 시 팝업 호출
if st.session_state.get("selected_product") and st.session_state.get("selected_step"):
    show_lot_detail(
        st.session_state["selected_product"],
        st.session_state["selected_step"]
    )
```

## 주의사항

- `st.dialog`는 Streamlit 1.35+ 기능. 버전 확인 후 구버전이면 `st.expander` 또는 `st.sidebar`로 대체
- 대체 방식에서도 "Matrix → 선택 → Lot 상세 확인" 3단계 흐름은 반드시 유지
