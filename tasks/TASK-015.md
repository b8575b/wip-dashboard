# TASK-015 · UI 정리 및 업무용 Dashboard 스타일 적용

| 항목 | 내용 |
|------|------|
| 상태 | todo |
| 우선순위 | low |
| 예상 시간 | 30분 |
| 의존 | TASK-012, TASK-014 |

## 쉬운 설명

WIP 현황판의 화면을 업무 환경에 맞게 정리하는 작업입니다. 화면 상단에 전체 재공수량, 보류 중인 lot 개수, 장시간 대기 lot 개수를 숫자 카드로 표시하고, 그 아래에 Matrix 표와 필터 영역이 명확하게 배치되도록 합니다. 이를 통해 사용자가 중요한 정보를 빠르게 파악할 수 있는 직관적인 대시보드를 만들게 됩니다.

## 관련 파일

| 파일 경로 | 상태 | 이 태스크에서의 역할 |
|-----------|------|---------------------|
| `app.py` | 기존 파일 | Streamlit 진입점 — 지표 카드 위치 정렬, 레이아웃 순서 조정 |
| `data/aggregate.py` | 기존 파일 | WIP Matrix 생성 — 표시되는 데이터 구조 유지 |
| `data/fetch.py` | 기존 파일 | WIP 데이터 조회 — 지표 계산 대상 데이터 제공 |
| `db.py` | 기존 파일 | Supabase 클라이언트 초기화 — 데이터 연결 유지 |
| `requirements.txt` | 참조 | Streamlit 1.35+ 버전 확인 — st.dialog 호환성 |

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
