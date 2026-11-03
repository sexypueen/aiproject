import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 페이지 기본 설정
st.set_page_config(
    page_title="국가별 MBTI 비율 시각화",
    page_icon="📊",
    layout="wide"
)

# 데이터 불러오기 함수 (캐싱 처리)
@st.cache_data
def load_data():
    # 동일한 폴더에 countriesMBTI_16types.csv 파일이 있어야 합니다.
    df = pd.read_csv('countriesMBTI_16types.csv')
    return df

try:
    df = load_data()

    # 앱 제목 및 설명
    st.title("🌍 국가별 MBTI 16가지 유형 비율 분석")
    st.markdown("원하는 국가를 선택하면 해당 국가의 MBTI 유형별 비율을 높은 순서대로 시각화합니다.")

    # 국가 선택 드롭다운 (기본값: South Korea 또는 첫 번째 국가)
    country_list = sorted(df['Country'].unique().tolist())
    default_index = country_list.index('South Korea') if 'South Korea' in country_list else 0
    selected_country = st.selectbox("국가를 선택하세요:", country_list, index=default_index)

    # 선택한 국가의 데이터 추출 및 정렬
    country_row = df[df['Country'] == selected_country].drop(columns=['Country']).iloc[0]
    
    # 비율을 백분율(%)로 변환 및 내림차순 정렬
    sorted_series = (country_row * 100).sort_values(ascending=False)
    mbti_types = sorted_series.index.tolist()
    percentages = sorted_series.values.tolist()

    # 🎨 색상 그라데이션 생성 (1등: 진한 파란색, 2~16등: 파란색에서 점차 연해짐)
    colors = []
    num_items = len(percentages)
    for i in range(num_items):
        if i == 0:
            # 1위: 가장 명확하고 진한 메인 파란색
            colors.append('#0D47A1')
        else:
            # 2위부터 16위까지 투명도를 조절하여 부드러운 그라데이션 생성 (0.85 -> 0.20)
            alpha = 0.85 - (i - 1) * (0.65 / (num_items - 2))
            colors.append(f'rgba(25, 118, 210, {alpha:.2f})')

    # Plotly 막대그래프 생성
    fig = go.Figure(
        data=[
            go.Bar(
                x=mbti_types,
                y=percentages,
                text=[f"{val:.2f}%" for val in percentages],
                textposition='auto',
                marker_color=colors,
                hovertemplate="<b>%{x}</b>: %{y:.2f}%<extra></extra>"
            )
        ]
    )

    # 레이아웃 스타일 설정
    fig.update_layout(
        title=dict(
            text=f"<b>{selected_country}의 MBTI 유형 분포</b>",
            font=dict(size=20)
        ),
        xaxis_title="MBTI 유형",
        yaxis_title="비율 (%)",
        xaxis=dict(type='category'),
        yaxis=dict(range=[0, max(percentages) * 1.15]), # 상단 여유 공간 확보
        template="plotly_white",
        height=550,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    # 그래프 출력
    st.plotly_chart(fig, use_container_width=True)

    # 요약 정보 및 데이터 테이블 배치
    st.markdown("---")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("💡 주요 포인트")
        st.success(f"🥇 가장 높은 비율: **{mbti_types[0]}** ({percentages[0]:.2f}%)")
        st.info(f"🥈 두 번째 비율: **{mbti_types[1]}** ({percentages[1]:.2f}%)")
        st.warning(f"🥉 세 번째 비율: **{mbti_types[2]}** ({percentages[2]:.2f}%)")

    with col2:
        st.subheader("📋 상세 데이터 (비율 순)")
        summary_df = pd.DataFrame({
            "MBTI 유형": mbti_types,
            "비율 (%)": [f"{p:.2f}%" for p in percentages]
        })
        st.dataframe(summary_df.T, use_container_width=True)

except FileNotFoundError:
    st.error("⚠️ `countriesMBTI_16types.csv` 파일을 찾을 수 없습니다. 파이썬 파일과 동일한 위치에 놓아주세요.")
