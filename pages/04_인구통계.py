import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# 1. 페이지 기본 설정
st.set_page_config(page_title="행정구역별 인구 분석", layout="wide")

st.title("🩷 행정구역별 연령대 인구 분석 대시보드")

# 2. 데이터 로드 (pages 폴더 기준 상위 폴더 '../population.csv' 탐색)
@st.cache_data
def load_data():
    file_path = '../population.csv'
    # 상위 폴더에 없거나 루트에서 직접 실행될 경우 예외 처리
    if not os.path.exists(file_path):
        file_path = 'population.csv'
        
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

# 3. 사이드바 - 행정구역, 성별, 연도 선택 필터
st.sidebar.header("⚙️ 분석 조건 선택")

# 행정구역 선택
regions = df['행정구역'].unique().tolist()
selected_region = st.sidebar.selectbox("행정구역 선택", regions)

# 성별 선택
gender_options = {"전체(계)": "계", "남성": "남", "여성": "여"}
selected_gender_label = st.sidebar.radio("성별 선택", list(gender_options.keys()))
selected_gender = gender_options[selected_gender_label]

# 연도 선택
years = ["2020년", "2021년", "2022년", "2023년", "2024년", "2025년"]
selected_year = st.sidebar.selectbox("연도 선택", years, index=2)

# 4. 선택된 데이터 추출
row_data = df[df['행정구역'] == selected_region].iloc[0]

# 10살 단위 연령대
age_bins = ['0~9세', '10~19세', '20~29세', '30~39세', '40~49세', 
            '50~59세', '60~69세', '70~79세', '80~89세', '90~99세', '100세 이상']

# 해당되는 연도/성별/연령대 인구수 매핑
pop_values = []
for age in age_bins:
    col_name = f"{selected_year}_{selected_gender}_{age}"
    pop_values.append(row_data.get(col_name, 0))

# 5. Plotly 꺾은선 그래프 생성 (한글 깨짐 방지 + 핫핑크 색상 + 구분선 설정)
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=age_bins,
    y=pop_values,
    mode='lines+markers',
    name=f'{selected_gender_label} 인구수',
    line=dict(color='#FF1493', width=4),  # 핫핑크 (HotPink) 라인
    marker=dict(size=8, color='#FF1493')
))

# 그래프 레이아웃 및 격자선(구분선) 설정
fig.update_layout(
    title=dict(
        text=f"<b>[{selected_region}] {selected_year} {selected_gender_label} 연령별 인구수</b>",
        font=dict(size=20)
    ),
    xaxis=dict(
        title="나이 (10살 단위 연령대)",
        showgrid=True,
        gridcolor='lightgray',
        gridwidth=1
    ),
    yaxis=dict(
        title="인구수 (명)",
        dtick=10000000,  # 세로축 1,000만 단위 구분선 설정
        showgrid=True,
        gridcolor='lightgray',
        gridwidth=1,
        tickformat=","
    ),
    hovermode="x unified",
    template="plotly_white",
    height=550
)

# 6. 웹 화면에 그래프 출력
st.plotly_chart(fig, use_container_width=True)

# 총인구수 요약 정보
total_col = f"{selected_year}_{selected_gender}_총인구수"
total_pop = int(row_data.get(total_col, 0))
st.info(f"📌 **{selected_region}**의 **{selected_year} {selected_gender_label} 총인구수**: **{total_pop:,}명**")
