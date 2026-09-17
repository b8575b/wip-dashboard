# TASK-014 · Status / Hold 필터 구현

| 항목 | 내용 |
|------|------|
| 상태 | todo |
| 우선순위 | medium |
| 예상 시간 | 30분 |
| 의존 | TASK-013 |

## 쉬운 설명

사용자가 WIP 현황판에서 재공의 상태(진행중, 대기중, 보류중)를 선택하고, "보류 중인 Lot만 보기" 옵션을 켤 수 있도록 합니다. 이 필터들은 제품/공정 필터와 함께 작동하여, 사용자가 보고 싶은 재공 데이터만 정확히 찾아볼 수 있게 합니다.

## 관련 파일

| 파일 경로 | 상태 | 이 태스크에서의 역할 |
|-----------|------|---------------------|
| `app.py` | 기존 파일 | Status/Hold 필터 UI 추가 위치 — 사이드바에 multiselect와 checkbox 구현 |
| `data/fetch.py` | 기존 파일 | 필터 조건에 따른 Lot 상세 데이터 조회 — fetch_lot_detail 함수 사용 |
| `data/aggregate.py` | 기존 파일 | 필터된 데이터로 WIP Matrix 생성 — build_wip_matrix 함수 호출 |

## 목표

Status(RUN/WAIT/HOLD) 선택 필터와 Hold Lot만 보기 토글을 추가한다. TASK-013의 Product/STEP 필터와 함께 복합 조건으로 동작해야 한다.

## 완료 조건

- [ ] 사이드바에 Status 다중 선택 필터 추가 (RUN / WAIT / HOLD)
- [ ] Hold Lot만 보기 토글(`st.checkbox`) 추가
- [ ] 모든 필터가 조합되어 WIP Matrix와 Lot 상세 팝업에 동일하게 적용됨
- [ ] 필터 초기화 버튼 또는 기본값으로 전체 선택

## 작업 내용

```python
# app.py 사이드바 섹션 (TASK-013 필터 이후에 추가)
with st.sidebar:
    st.divider()
    selected_statuses = st.multiselect(
        "Status", ["RUN", "WAIT", "HOLD"],
        default=["RUN", "WAIT", "HOLD"]
    )
    hold_only = st.checkbox("Hold Lot만 보기", value=False)

# 복합 필터 적용
filtered_df = df[
    df["product_name"].isin(selected_products) &
    df["step_name"].isin(selected_steps) &
    df["status"].isin(selected_statuses)
]
if hold_only:
    filtered_df = filtered_df[filtered_df["hold_yn"] == "Y"]
```

## 주의사항

- Hold Lot만 보기가 활성화된 상태에서 Status 필터도 함께 적용되므로, 두 조건의 AND 관계를 명확히 유지한다
- 필터 적용 결과로 Matrix가 비어 있을 수 있으므로 빈 Matrix 안내 메시지 처리 필요 (TASK-008에서 이미 처리됨)
