import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# 1. 페이지 설정
st.set_page_config(page_title="행정구역별 인구 분석", layout="wide")

st.title("🩷💚 행정구역별 연령대 및 성별 인구 분석 대시보드")

# 2. 데이터 로드 (pages 폴더 기준 상위 폴더인 '../population.csv' 탐색)
@st.cache_data
def load_data():
    file_path = '../population.csv'
    if not os.path.exists(file_path):
        file_path = 'population.csv'  # 로컬 테스트용 폴더 대응
        
    try:
        df = pd.read_csv(file_path, encoding='cp949')
    except Exception:
        df = pd.read_csv(file_path, encoding='euc-kr')
    
    # 숫자 데이터 쉼표(,) 제거 및 정수 형변환
    for col in df.columns:
        if col != '행정구역':
            df[col] = df[col].astype(str).str.replace(',', '').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

df = load_data()

# 3. 사이드바 - 분석 모드 선택 (기능 1 vs 기능 2)
st.sidebar.header("⚙️ 분석 메뉴 선택")
analysis_mode = st.sidebar.radio(
    "분석 방식을 선택하세요", 
    ["1️⃣ 특정 행정구의 연령별 꺾은선 그래프", "2️⃣ 특정 연령대가 가장 많은 행정구 TOP 10"]
)

years = ["2020년", "2021년", "2022년", "2023년", "2024년", "2025년"]
age_bins = ['0~9세', '10~19세', '20~29세', '30~39세', '40~49세', 
            '50~59세', '60~69세', '70~79세', '80~89세', '90~99세', '100세 이상']

# ==========================================
# [모드 1] 기존: 행정구, 성별, 연도별 꺾은선 그래프 (남: 핑크, 여: 초록)
# ==========================================
if analysis_mode == "1️⃣ 특정 행정구의 연령별 꺾은선 그래프":
    st.sidebar.subheader("🔍 꺾은선 그래프 조건")
    regions = df['행정구역'].unique().tolist()
    selected_region = st.sidebar.selectbox("행정구역 선택", regions)
    selected_year = st.sidebar.selectbox("연도 선택", years, index=2)
    
    row_data = df[df['행정구역'] == selected_region].iloc[0]
    
    # 남녀 데이터 각각 추출
    male_values, female_values = [], []
    for age in age_bins:
        male_values.append(row_data.get(f"{selected_year}_남_{age}", 0))
        female_values.append(row_data.get(f"{selected_year}_여_{age}", 0))
        
    # Plotly 꺾은선 그래프 생성 (남성: 핑크 #FF1493, 여성: 초록 #2E8B57)
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=age_bins, y=male_values,
        mode='lines+markers',
        name='남성',
        line=dict(color='#FF1493', width=4),  # 핑크색
        marker=dict(size=8, color='#FF1493')
    ))
    
    fig.add_trace(go.Scatter(
        x=age_bins, y=female_values,
        mode='lines+markers',
        name='여성',
        line=dict(color='#2E8B57', width=4),  # 초록색 (SeaGreen)
        marker=dict(size=8, color='#2E8B57')
    ))
    
    fig.update_layout(
        title=dict(text=f"<b>[{selected_region}] {selected_year} 성별 연령별 인구수</b>", font=dict(size=20)),
        xaxis=dict(title="나이 (10살 단위 연령대)", showgrid=True, gridcolor='lightgray'),
        yaxis=dict(title="인구수 (명)", showgrid=True, gridcolor='lightgray', tickformat=","),
        hovermode="x unified",
        template="plotly_white",
        height=550
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    total_pop = int(row_data.get(f"{selected_year}_계_총인구수", 0))
    st.info(f"📌 **{selected_region}**의 **{selected_year} 총인구수**: **{total_pop:,}명**")

# ==========================================
# [모드 2] 신규: 연령대별 가장 인구가 많은 행정구 막대그래프
# ==========================================
else:
    st.sidebar.subheader("📊 연령대별 순위 조건")
    selected_age = st.sidebar.selectbox("10살 단위 연령대 선택", age_bins)
    selected_year = st.sidebar.selectbox("연도 선택", years, index=2)
    
    # 성별 선택 (전체, 남성, 여성)
    gender_choice = st.sidebar.radio("성별 구분", ["전체(계)", "남성", "여성"])
    gender_code = "계" if gender_choice == "전체(계)" else ("남" if gender_choice == "남성" else "여")
    
    target_col = f"{selected_year}_{gender_code}_{selected_age}"
    
    # 데이터 상위 10개 추출
    top_df = df[['행정구역', target_col]].sort_values(by=target_col, ascending=False).head(10)
    top_df = top_df.sort_values(by=target_col, ascending=True) # 가로 막대 정렬용
    
    # 색상 지정 (남성이면 핑크, 여성이면 초록, 전체면 기본 핫핑크 계열)
    bar_color = '#FF1493' if gender_code == '남' else ('#2E8B57' if gender_code == '여' else '#FF69B4')
    
    fig = go.Figure(go.Bar(
        x=top_df[target_col],
        y=top_df['행정구역'],
        orientation='h',
        marker_color=bar_color,
        text=[f"{val:,}명" for val in top_df[target_col]],
        textposition='auto'
    ))
    
    fig.update_layout(
        title=dict(text=f"<b>{selected_year} [{selected_age}] 인구가 가장 많은 행정구 TOP 10 ({gender_choice})</b>", font=dict(size=18)),
        xaxis=dict(title="인구수 (명)", showgrid=True, gridcolor='lightgray', tickformat=","),
        yaxis=dict(title="행정구역"),
        template="plotly_white",
        height=550
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.success(f"💡 선택하신 **{selected_age}** 구간에서 **{selected_year년}년 기준 {gender_choice}** 인구가 가장 밀집된 지역 순위입니다.")
