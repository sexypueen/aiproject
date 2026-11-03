import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 페이지 기본 설정
st.set_page_config(
    page_title="국가별 MBTI 비율 시각화",
    page_icon="📊",
    layout="wide"
)

st.title("📊 국가별 MBTI 16가지 유형 비율 분석")
st.write("국가를 선택하면 1위 유형(진한 파란색)부터 순위별로 흐려지는 그라데이션 막대그래프를 확인할 수 있습니다.")

# 데이터 불러오기 함수 (캐싱 적용)
@st.cache_data
def load_data():
    df = pd.read_csv('countriesMBTI_16types.csv')
    return df

try:
    df = load_data()

    # 국가 목록 생성
    country_list = sorted(df['Country'].unique().tolist())
    
    # 한국이 목록에 있다면 기본값으로 설정, 없으면 첫 번째 국가 설정
    default_index = country_list.index("South Korea") if "South Korea" in country_list else 0

    # 1. 국가 선택 드롭다운 (사이드바)
    selected_country = st.sidebar.selectbox("국가를 선택하세요", country_list, index=default_index)

    # 데이터 추출 및 내림차순 정렬
    country_row = df[df['Country'] == selected_country].iloc[0]
    mbti_cols = [c for c in df.columns if c != 'Country']
    
    # 퍼센트(%) 단위로 변환 후 정렬
    mbti_series = (country_row[mbti_cols] * 100).astype(float).sort_values(ascending=False)

    # 2. 색상 그라데이션 설정 (1등은 진한 파란색, 뒤로 갈수록 흐려지는 연파란색)
    n_bars = len(mbti_series)
    # matplotlib의 Blues 컬러맵을 활용하여 1등(0.9)부터 16등(0.25)까지 그라데이션 생성
    colors = [plt.cm.Blues(0.9 - (i / (n_bars - 1)) * 0.65) for i in range(n_bars)]

    # 3. 그래프 시각화
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(mbti_series.index, mbti_series.values, color=colors, edgecolor='none')

    # 막대 상단에 비율 퍼센트 표시
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3pt vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8, fontweight='bold', color='#333333')

    # 축 및 제목 스타일링
    ax.set_title(f"[{selected_country}] MBTI 유형별 비율 (내림차순)", fontsize=14, pad=15, fontweight='bold')
    ax.set_ylabel("비율 (%)", fontsize=11)
    ax.set_ylim(0, max(mbti_series.values) * 1.15)  # 상단 여백 확보
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.xticks(rotation=45, ha='right', fontsize=9.5)

    # Streamlit 화면에 그래프 출력
    st.pyplot(fig)

    # 요약 정보 카드 출력
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🥇 1위 유형", value=f"{mbti_series.index[0]} ({mbti_series.iloc[0]:.2f}%)")
    with col2:
        st.metric(label="🥈 2위 유형", value=f"{mbti_series.index[1]} ({mbti_series.iloc[1]:.2f}%)")
    with col3:
        st.metric(label="🥉 3위 유형", value=f"{mbti_series.index[2]} ({mbti_series.iloc[2]:.2f}%)")

except FileNotFoundError:
    st.error("❌ `countriesMBTI_16types.csv` 파일을 찾을 수 없습니다. 같은 폴더 내에 파일이 있는지 확인해 주세요.")
