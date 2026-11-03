import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 페이지 기본 설정
st.set_page_config(
    page_title="국가별 MBTI 비율 분석",
    page_icon="📊",
    layout="wide"
)

# 데이터 불러오기 함수 (캐싱 처리)
@st.cache_data
def load_data():
    df = pd.read_csv('countriesMBTI_16types.csv')
    return df

try:
    df = load_data()

    # 앱 제목
    st.title("🌍 국가별 MBTI 16가지 유형 비율 분석 시스템")
    st.markdown("원하는 방식을 선택하여 전 세계 국가들의 MBTI 분포를 탐색해보세요.")

    # 탭 메뉴 구성 (1. 국가별 보기 / 2. MBTI 유형별 순위 보기)
    tab1, tab2 = st.tabs(["📊 국가별 MBTI 분포", "🏆 MBTI 유형별 국가 순위"])

    # ==========================================
    # 탭 1: 국가별 MBTI 분포 그래프
    # ==========================================
    with tab1:
        st.subheader("국가별 MBTI 유형 비율 시각화")
        
        country_list = sorted(df['Country'].unique().tolist())
        default_index = country_list.index('South Korea') if 'South Korea' in country_list else 0
        selected_country = st.selectbox("국가를 선택하세요:", country_list, index=default_index, key="country_select")

        # 데이터 추출 및 정렬
        country_row = df[df['Country'] == selected_country].drop(columns=['Country']).iloc[0]
        sorted_series = (country_row * 100).sort_values(ascending=False)
        mbti_types = sorted_series.index.tolist()
        percentages = sorted_series.values.tolist()

        # 색상 그라데이션 생성 (1등: 진한 파란색, 나머지: 점차 연해짐)
        colors = []
        num_items = len(percentages)
        for i in range(num_items):
            if i == 0:
                colors.append('#0D47A1')
            else:
                alpha = 0.85 - (i - 1) * (0.65 / (num_items - 2))
                colors.append(f'rgba(25, 118, 210, {alpha:.2f})')

        # Plotly 막대그래프
        fig1 = go.Figure(
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

        fig1.update_layout(
            title=dict(text=f"<b>{selected_country}의 MBTI 유형 분포</b>", font=dict(size=20)),
            xaxis_title="MBTI 유형",
            yaxis_title="비율 (%)",
            xaxis=dict(type='category'),
            yaxis=dict(range=[0, max(percentages) * 1.15]),
            template="plotly_white",
            height=500,
            margin=dict(l=40, r=40, t=60, b=40)
        )

        st.plotly_chart(fig1, use_container_width=True)

        # 요약 정보 및 데이터 테이블
        col1, col2 = st.columns([1, 2])
        with col1:
            st.success(f"🥇 가장 높은 비율: **{mbti_types[0]}** ({percentages[0]:.2f}%)")
            st.info(f"🥈 두 번째 비율: **{mbti_types[1]}** ({percentages[1]:.2f}%)")
            st.warning(f"🥉 세 번째 비율: **{mbti_types[2]}** ({percentages[2]:.2f}%)")
        with col2:
            summary_df = pd.DataFrame({
                "MBTI 유형": mbti_types,
                "비율 (%)": [f"{p:.2f}%" for p in percentages]
            })
            st.dataframe(summary_df.T, use_container_width=True)

    # ==========================================
    # 탭 2: MBTI 유형별 국가 순위 보기 (신규 추가)
    # ==========================================
    with tab2:
        st.subheader("특정 MBTI 유형 비율이 높은 국가 순위")
        
        mbti_columns = [col for col in df.columns if col != 'Country']
        selected_mbti = st.selectbox("확인할 MBTI 유형을 선택하세요:", mbti_columns, key="mbti_select")
        
        # 선택한 MBTI 기준으로 내림차순 정렬 (상위 20개 국가)
        ranking_df = df[['Country', selected_mbti]].copy()
        ranking_df[selected_mbti] = ranking_df[selected_mbti] * 100  # 백분율 변환
        ranking_df = ranking_df.sort_values(by=selected_mbti, ascending=False).reset_index(drop=True)
        
        top_n = st.slider("표시할 국가 수:", min_value=5, max_value=50, value=15, step=5)
        plot_df = ranking_df.head(top_n)

        # 유형별 순위 그래프 색상 (1위만 진한 파랑, 나머지는 그라데이션)
        rank_colors = []
        n_bars = len(plot_df)
        for i in range(n_bars):
            if i == 0:
                rank_colors.append('#0D47A1')
            else:
                alpha = 0.85 - (i - 1) * (0.65 / max(1, n_bars - 2))
                rank_colors.append(f'rgba(25, 118, 210, {alpha:.2f})')

        fig2 = go.Figure(
            data=[
                go.Bar(
                    x=plot_df['Country'],
                    y=plot_df[selected_mbti],
                    text=[f"{val:.2f}%" for val in plot_df[selected_mbti]],
                    textposition='auto',
                    marker_color=rank_colors,
                    hovertemplate="<b>%{x}</b>: %{y:.2f}%<extra></extra>"
                )
            ]
        )

        fig2.update_layout(
            title=dict(text=f"<b>[{selected_mbti}] 비율이 가장 높은 국가 순위 (Top {top_n})</b>", font=dict(size=20)),
            xaxis_title="국가",
            yaxis_title="비율 (%)",
            xaxis=dict(type='category'),
            yaxis=dict(range=[0, plot_df[selected_mbti].max() * 1.15]),
            template="plotly_white",
            height=500,
            margin=dict(l=40, r=40, t=60, b=40)
        )

        st.plotly_chart(fig2, use_container_width=True)

        # 전체 순위 테이블 제공
        with st.expander("📋 전체 국가 순위 데이터 테이블 보기"):
            display_table = ranking_df.copy()
            display_table.columns = ['국가', '비율 (%)']
            display_table['비율 (%)'] = display_table['비율 (%)'].apply(lambda x: f"{x:.2f}%")
            display_table.index = display_table.index + 1
            st.dataframe(display_table, use_container_width=True)

except FileNotFoundError:
    st.error("⚠️ `countriesMBTI_16types.csv` 파일을 찾을 수 없습니다. 파이썬 파일과 동일한 폴더에 파일을 위치시켜주세요.")
