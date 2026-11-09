import datetime
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# --- 1. 한글 폰트 설정 및 마이너스 기호 방지 ---
plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

# 페이지 설정
st.set_page_config(
    page_title='서울 기온 분석 대시보드', page_icon='🌡️', layout='wide'
)

st.title('🌡️ 서울 종합 기온 분석 대시보드')
st.write(
    '제공된 기온 데이터를 바탕으로 월별, 연도별 기온 변화를 올바르게'
    ' 시각화합니다.'
)


# --- 2. 데이터 로드 및 전처리 (연도 오인식 방지 보정) ---
@st.cache_data
def load_data():
  df = pd.read_csv('temperature.csv', encoding='cp949')

  # 날짜 파싱 (기본 datetime 변환 후 2자리 연도 세기 조정)
  df['일시_dt'] = pd.to_datetime(
      df['일시'], format='%b-%y', errors='coerce'
  )
  df['연도'] = df['일시_dt'].dt.year

  # pandas가 2자리 연도를 2000년대로 오인하여 미래 연도가 된 경우(예: 2069 ~ 2099년 등) 1900년대로 보정
  # (데이터셋의 실제 연도 범위에 맞게 조정)
  df.loc[df['연도'] > 2026, '연도'] -= 100

  df['월'] = df['일시_dt'].dt.month

  # 실제 정확한 연도-월 기반으로 정렬하기 위해 연도 다시 세팅
  return df


try:
  df = load_data()
except Exception as e:
  st.error(
      f"데이터 파일을 불러오는 중 오류가 발생했습니다. 'temperature.csv' 파일이"
      f' 올바른 위치에 있는지 확인하세요.\n오류 내용: {e}'
  )
  st.stop()

# 유효한 연도 목록 추출 (정렬)
available_years = sorted(df['연도'].dropna().unique().astype(int))

# --- 3. 사이드바 메뉴 구성 ---
st.sidebar.header('🔍 분석 메뉴 선택')
menu = st.sidebar.selectbox(
    '원하는 분석을 선택하세요',
    [
        '1. 월별 평균기온 (1~12월)',
        '2. 특정 연도 최고·최저기온',
        '3. 두 연도 기온 비교',
    ],
)

# -------------------------------------------------------------------------
# 기능 1: 월별 평균기온 (가로축 1~12월)
# -------------------------------------------------------------------------
if menu == '1. 월별 평균기온 (1~12월)':
  st.subheader('📊 서울 월별 평균기온 분석 (1월 ~ 12월)')
  st.write('전체 연도를 통틀어 각 월의 평균기온 추이를 보여줍니다.')

  monthly_avg = df.groupby('월')['평균기온(℃)'].mean().reset_index()

  fig, ax = plt.subplots(figsize=(10, 5))
  ax.plot(
      monthly_avg['월'],
      monthly_avg['평균기온(℃)'],
      marker='o',
      color='orange',
      linewidth=2.5,
      label='월별 평균기온',
  )

  ax.set_title('서울 월별 평균기온', fontsize=14, fontweight='bold')
  ax.set_xlabel('월 (Month)', fontsize=12)
  ax.set_ylabel('평균기온 (℃)', fontsize=12)
  ax.set_xticks(range(1, 13))
  ax.set_xticklabels([f'{i}월' for i in range(1, 13)])
  ax.legend(loc='upper left')
  ax.grid(True, linestyle='--', alpha=0.6)

  st.pyplot(fig)

# -------------------------------------------------------------------------
# 기능 2: 연도 1개 선택 -> 해당 연도의 월별 최고기온/최저기온 그래프
# -------------------------------------------------------------------------
elif menu == '2. 특정 연도 최고·최저기온':
  st.subheader('📈 연도별 월별 최고·최저기온 분석')

  selected_year = st.selectbox(
      '조회할 연도를 선택하세요:',
      options=available_years,
      index=len(available_years) - 1,
  )

  year_df = df[df['연도'] == selected_year].sort_values('월')

  if year_df.empty:
    st.warning(f'{selected_year}년에 해당하는 데이터가 없습니다.')
  else:
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        year_df['월'],
        year_df['최고기온(℃)'],
        color='red',
        marker='o',
        linewidth=2,
        label='최고기온',
    )
    ax.plot(
        year_df['월'],
        year_df['최저기온(℃)'],
        color='blue',
        marker='s',
        linewidth=2,
        label='최저기온',
    )

    ax.set_title(
        f'월별 기온분석 ({selected_year}년)', fontsize=14, fontweight='bold'
    )
    ax.set_xlabel('월 (Month)', fontsize=12)
    ax.set_ylabel('온도 (℃)', fontsize=12)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels([f'{i}월' for i in range(1, 13)])
    ax.legend(loc='upper left')
    ax.grid(True, linestyle='--', alpha=0.6)

    st.pyplot(fig)

    with st.expander('📊 상세 데이터 보기'):
      st.dataframe(
          year_df[['월', '평균기온(℃)', '최고기온(℃)', '최저기온(℃)']].reset_index(
              drop=True
          )
      )

# -------------------------------------------------------------------------
# 기능 3: 연도 2개 선택 -> 두 연도 비교 그래프
# -------------------------------------------------------------------------
elif menu == '3. 두 연도 기온 비교':
  st.subheader('⚖️ 두 연도 간 월별 평균기온 비교')

  col1, col2 = st.columns(2)
  with col1:
    year1 = st.selectbox(
        '첫 번째 연도 선택:', options=available_years, index=0
    )
  with col2:
    year2 = st.selectbox(
        '두 번째 연도 선택:',
        options=available_years,
        index=min(1, len(available_years) - 1),
    )

  df_y1 = df[df['연도'] == year1].sort_values('월')
  df_y2 = df[df['연도'] == year2].sort_values('월')

  fig, ax = plt.subplots(figsize=(10, 5))

  ax.plot(
      df_y1['월'],
      df_y1['평균기온(℃)'],
      color='green',
      marker='o',
      linewidth=2,
      label=f'{year1}년 평균기온',
  )
  ax.plot(
      df_y2['월'],
      df_y2['평균기온(℃)'],
      color='purple',
      marker='x',
      linewidth=2,
      label=f'{year2}년 평균기온',
  )

  ax.set_title(
      f'연도별 기온 비교 ({year1}년 vs {year2}년)',
      fontsize=14,
      fontweight='bold',
  )
  ax.set_xlabel('월 (Month)', fontsize=12)
  ax.set_ylabel('평균기온 (℃)', fontsize=12)
  ax.set_xticks(range(1, 13))
  ax.set_xticklabels([f'{i}월' for i in range(1, 13)])
  ax.legend(loc='upper left')
  ax.grid(True, linestyle='--', alpha=0.6)

  st.pyplot(fig)

  with st.expander('📊 연도별 비교 데이터 보기'):
    comparison_df = pd.DataFrame({
        '월': range(1, 13),
        f'{year1}년 평균기온': df_y1['평균기온(℃)'].values,
        f'{year2}년 평균기온': df_y2['평균기온(℃)'].values,
    })
    st.dataframe(comparison_df.reset_index(drop=True))
