# TASK-015 · UI 정리 및 업무용 Dashboard 스타일 적용

| 항목 | 내용 |
|------|------|
| 상태 | todo |
| 우선순위 | low |
| 예상 시간 | 30분 |
| 의존 | TASK-012, TASK-014 |

## 목표

전체 레이아웃을 정리하고 업무용 Dashboard에 적합한 스타일을 적용한다. 핵심 정보가 화면 상단에 배치되도록 최종 레이아웃을 확정한다.

## 완료 조건

- [ ] 페이지 상단에 주요 지표(전체 WIP, Hold 수, STEP별 현황)를 metric 카드로 표시
- [ ] Matrix 표 제목과 설명이 명확하게 표시됨
- [ ] 사이드바 레이아웃이 정리됨
- [ ] 불필요한 Streamlit 기본 UI 요소(footer 등) 제거 검토

## 작업 내용

### 상단 지표 카드

```python
col1, col2, col3 = st.columns(3)
col1.metric("전체 WIP", f"{filtered_df['quantity'].sum():,}")
col2.metric("Hold Lot", f"{(filtered_df['hold_yn']=='Y').sum()}건")
col3.metric("장시간 대기(24h+)", f"{(filtered_df['waiting_hours']>=24).sum()}건")
```

### 레이아웃 순서

1. 페이지 타이틀 + caption
2. 상단 지표 카드 (metric 3개)
3. `st.divider()`
4. WIP Matrix (사이드바 필터와 연동)
5. Lot 상세 팝업 (선택 시 자동 표시)

### 선택적 스타일 개선

```python
# 기본 Streamlit footer 숨기기 (필요 시)
st.markdown("""
<style>
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)
```

## 주의사항

- 디자인보다 데이터 정확성과 핵심 흐름 동작이 우선이다
- 복잡한 CSS 커스터마이징은 이 단계에서 최소화한다
