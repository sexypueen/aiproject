import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# --- 1. 한글 폰트 및 마이너스 기호 설정 (리눅스 서버 대응) ---
plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

# 페이지 설정
st.set_page_config(
    page_title='서울 기온 예측 및 분석 대시보드', page_icon='🌡️', layout='wide'
)

st.title('🌡️ 서울 월별 기온 분석 및 AI 예측 대시보드')
st.write(
    '제공된 기온 데이터(2007년~2026년)를 바탕으로 특정 월의 장기 트렌드를'
    ' 조회하고, 머신러닝/통계 모델을 통해 미래 기온을 예측합니다.'
)


# --- 2. 데이터 로드 및 전처리 ---
@st.cache_data
def load_data():
  df = pd.read_csv('temperature.csv', encoding='cp949')
  df['일시_dt'] = pd.to_datetime(
      df['일시'], format='%b-%y', errors='coerce'
  )
  df['연도'] = df['일시_dt'].dt.year
  df['월'] = df['일시_dt'].dt.month
  return df


try:
  df = load_data()
except Exception as e:
  st.error(
      f"데이터 파일을 불러오는 중 오류가 발생했습니다. 'temperature.csv' 파일이"
      f' 올바른 위치에 있는지 확인하세요.\n오류 내용: {e}'
  )
  st.stop()

# --- 3. 사이드바 설정 ---
st.sidebar.header('⚙️ 분석 및 예측 설정')

month_dict = {
    1: '1월',
    2: '2월',
    3: '3월',
    4: '4월',
    5: '5월',
    6: '6월',
    7: '7월',
    8: '8월',
    9: '9월',
    10: '10월',
    11: '11월',
    12: '12월',
}
selected_month = st.sidebar.selectbox(
    '분석할 월을 선택하세요:',
    options=list(month_dict.keys()),
    format_func=lambda x: month_dict[x],
)

max_data_year = int(df['연도'].max())
target_year = st.sidebar.number_input(
    '미래 예측 연도 입력:',
    min_value=max_data_year + 1,
    max_value=2100,
    value=max_data_year + 5,
    step=1,
)

# --- 4. 데이터 필터링 및 예측 모델링 ---
m_df = (
    df[df['월'] == selected_month]
    .dropna(subset=['평균기온(℃)'])
    .sort_values('연도')
)
X_past = m_df['연도'].values
y_past = m_df['평균기온(℃)'].values

min_year = int(X_past.min())
future_years = np.arange(min_year, target_year + 1)


# 알고리즘 1: 선형 회귀
def linear_regression(x, y, x_pred):
  coef = np.polyfit(x, y, 1)
  return np.poly1d(coef)(x_pred)


# 알고리즘 2: 다항 회귀 (2차)
def poly_regression(x, y, x_pred, deg=2):
  coef = np.polyfit(x, y, deg)
  return np.poly1d(coef)(x_pred)


# 알고리즘 3: 지수 평활 트렌드
def exponential_smoothing_trend(x, y, x_pred, alpha=0.3):
  n = len(y)
  smoothed = [y[0]]
  for i in range(1, n):
    smoothed.append(alpha * y[i] + (1 - alpha) * smoothed[i - 1])
  recent_trend = (y[-1] - y[-5]) / 5 if n >= 5 else (y[-1] - y[0]) / n
  base_val = smoothed[-1]
  preds = []
  for yr in x_pred:
    diff = yr - x[-1]
    if diff <= 0:
      idx = np.where(x == yr)[0]
      preds.append(y[idx[0]] if len(idx) > 0 else base_val)
    else:
      preds.append(base_val + recent_trend * diff)
  return np.array(preds)


pred_lr = linear_regression(X_past, y_past, future_years)
pred_poly = poly_regression(X_past, y_past, future_years, deg=2)
pred_es = exponential_smoothing_trend(X_past, y_past, future_years, alpha=0.4)

# --- 5. 시각화 ---
st.subheader(
    f'📈 서울 {month_dict[selected_month]} 장기 기온 분석 및 미래 예측'
    f' ({min_year}년 ~ {target_year}년)'
)

fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(
    X_past,
    y_past,
    marker='o',
    color='black',
    linewidth=2,
    label=f'실제 평균기온 ({min_year}~{max_data_year})',
)
ax.plot(
    future_years[future_years >= max_data_year],
    pred_lr[future_years >= max_data_year],
    color='red',
    linestyle='--',
    linewidth=2,
    label='① 선형 회귀 (Linear Regression)',
)
ax.plot(
    future_years[future_years >= max_data_year],
    pred_poly[future_years >= max_data_year],
    color='blue',
    linestyle='-.',
    linewidth=2,
    label='② 다항 회귀 (Polynomial, 2차)',
)
ax.plot(
    future_years[future_years >= max_data_year],
    pred_es[future_years >= max_data_year],
    color='green',
    linestyle=':',
    linewidth=2.5,
    label='③ 지수 평활 트렌드 (Exponential Smoothing)',
)

ax.set_title(
    f'서울 {month_dict[selected_month]} 기온 트렌드 및 AI 예측 비교',
    fontsize=14,
    fontweight='bold',
)
ax.set_xlabel('연도 (Year)', fontsize=12)
ax.set_ylabel('평균기온 (℃)', fontsize=12)
ax.legend(loc='upper left', fontsize=10)
ax.grid(True, linestyle='--', alpha=0.6)

st.pyplot(fig)

# --- 6. 알고리즘 원리 설명 ---
st.markdown('---')
st.subheader('🧠 예측 알고리즘별 작동 원리 및 차이점 설명')

col1, col2, col3 = st.columns(3)

with col1:
  st.markdown('### ① 선형 회귀')
  st.markdown(
      '**작동 원리:**\n'
      '- 전체 데이터의 **최소제곱법(OLS)**을 이용해 오차가 가장 적은 **하나의 직선($y = ax + b$)**을 긋습니다.\n\n'
      '**특징:** 장기적인 거시적 상승 추세를 파악하는 데 가장 직관적입니다.'
  )

with col2:
  st.markdown('### ② 다항 회귀 (2차)')
  st.markdown(
      '**작동 원리:**\n'
      '- 직선이 아닌 **포물선 형태의 곡선함수($y = ax^2 + bx + c$)**를 적용합니다.\n\n'
      '**특징:** 최근 온난화 가속화 등 비선형적인 변화 곡선을 유연하게 반영합니다.'
  )

with col3:
  st.markdown('### ③ 지수 평활 트렌드')
  st.markdown(
      '**작동 원리:**\n'
      '- **가장 최근 연도 데이터에 높은 가중치**를 두고 멀어질수록 낮추어 단기 모멘텀을 반영합니다.\n\n'
      '**특징:** 최근의 변화 속도를 민감하게 따라가는 예측에 강합니다.'
  )

with st.expander('📊 연도별 예측 데이터 테이블 확인'):
  pred_df = pd.DataFrame({
      '연도': future_years,
      '선형회귀_예측온도(℃)': np.round(pred_lr, 2),
      '다항회귀_예측온도(℃)': np.round(pred_poly, 2),
      '지수평활_예측온도(℃)': np.round(pred_es, 2),
  })
  st.dataframe(pred_df.set_index('연도'))
