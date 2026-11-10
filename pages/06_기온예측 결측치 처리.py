import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures
import streamlit as st

# --- 1. 한글 폰트 및 마이너스 기호 설정 (리눅스 서버 대응) ---
plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

# 페이지 설정
st.set_page_config(
    page_title='서울 월별 기온 AI 예측 대시보드', page_icon='🌡️', layout='wide'
)

st.title('🌡️ 서울 월별 기온 장기 분석 및 Scikit-learn AI 예측')
st.write(
    '제공된 데이터를 정제하여 1907년부터 2025년까지 선택한 개월의 기온 트렌드를'
    ' 조회하고, Scikit-learn 모델을 통해 미래 기온을 예측·비교합니다.'
)


# --- 2. 데이터 로드 및 정제 함수 ---
@st.cache_data
def load_and_clean_data():
  df = pd.read_csv('temperature.csv', encoding='cp949')

  # 날짜 파싱
  df['일시_dt'] = pd.to_datetime(
      df['일시'], format='%b-%y', errors='coerce'
  )
  df['연도'] = df['일시_dt'].dt.year
  df['월'] = df['일시_dt'].dt.month

  # 2자리 연도 파싱 오인식 보정 (데이터 범위에 맞게 조정)
  df.loc[(df['연도'] >= 2050) & (df['연도'] <= 2068), '연도'] -= 100

  return df


try:
  df = load_and_clean_data()
except Exception as e:
  st.error(f'데이터 로드 중 오류 발생: {e}')
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
    '분석할 개월을 선택하세요:',
    options=list(month_dict.keys()),
    format_func=lambda x: month_dict[x],
)

# 최대 데이터 연도 (2025년 기준)
max_data_year = 2025

target_year = st.sidebar.number_input(
    '미래 예측 연도 입력:',
    min_value=max_data_year + 1,
    max_value=2100,
    value=max_data_year + 15,
    step=1,
)

# --- 4. 선택한 개월 데이터 필터링 및 연도별 평균 집계 (그래프 꼬임 방지) ---
m_df = (
    df[(df['월'] == selected_month) & (df['연도'] <= max_data_year)]
    .dropna(subset=['평균기온(℃)'])
    .groupby('연도')['평균기온(℃)']
    .mean()
    .reset_index()
    .sort_values('연도')
)

X_past = m_df['연도'].values.reshape(-1, 1)
y_past = m_df['평균기온(℃)'].values

min_year = int(X_past.min())
future_years = np.arange(min_year, target_year + 1).reshape(-1, 1)

# --- 5. Scikit-learn 머신러닝 모델 학습 및 예측 ---
# ① 선형 회귀 (Linear Regression)
model_lr = LinearRegression()
model_lr.fit(X_past, y_past)
pred_lr = model_lr.predict(future_years)

# ② 다항 회귀 (Polynomial Regression, 2차 곡선)
model_poly = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
model_poly.fit(X_past, y_past)
pred_poly = model_poly.predict(future_years)

# ③ 릿지 회귀 (Ridge Regression - 규제 적용 모델)
model_ridge = Ridge(alpha=10.0)
model_ridge.fit(X_past, y_past)
pred_ridge = model_ridge.predict(future_years)


# --- 6. 그래프 시각화 ---
st.subheader(
    f'📈 서울 {month_dict[selected_month]} 기온 트렌드 및 AI 예측'
    f' ({min_year}년 ~ {target_year}년)'
)

fig, ax = plt.subplots(figsize=(12, 6))

# 실제 과거 데이터 라인 (1907 ~ 2025)
ax.plot(
    X_past.flatten(),
    y_past,
    marker='o',
    color='black',
    linewidth=1.5,
    markersize=3,
    label=f'실제 평균기온 ({min_year}~{max_data_year})',
)

# 미래 예측선 (2025년 이후 구간)
future_mask = future_years.flatten() >= max_data_year
x_fut = future_years.flatten()

# 과거와 미래를 자연스럽게 잇기 위해 2025년 데이터 지점부터 미래 예측선 시작
bridge_idx = np.where(x_fut >= max_data_year)[0][0] - 1
if bridge_idx < 0:
  bridge_idx = 0

x_plot = x_fut[bridge_idx:]

ax.plot(
    x_plot,
    pred_lr[bridge_idx:],
    color='red',
    linestyle='--',
    linewidth=2,
    label='① 선형 회귀 (Linear Regression)',
)
ax.plot(
    x_plot,
    pred_poly[bridge_idx:],
    color='blue',
    linestyle='-.',
    linewidth=2,
    label='② 다항 회귀 (Polynomial Regression, 2차)',
)
ax.plot(
    x_plot,
    pred_ridge[bridge_idx:],
    color='green',
    linestyle=':',
    linewidth=2.5,
    label='③ 릿지 회귀 (Ridge Regression, 규제 적용)',
)

ax.set_title(
    f'서울 {month_dict[selected_month]} 기온 머신러닝 예측 비교',
    fontsize=14,
    fontweight='bold',
)
ax.set_xlabel('연도 (Year)', fontsize=12)
ax.set_ylabel('평균기온 (℃)', fontsize=12)
ax.legend(loc='upper left', fontsize=10)
ax.grid(True, linestyle='--', alpha=0.6)

st.pyplot(fig)


# --- 7. 알고리즘 작동 원리 및 특징 설명 ---
st.markdown('---')
st.subheader('🧠 Scikit-learn 예측 알고리즘별 작동 원리 및 차이점')

col1, col2, col3 = st.columns(3)

with col1:
  st.markdown('### ① 선형 회귀')
  st.markdown(
      '**작동 원리 (`LinearRegression`):**\n'
      '- 과거 연도와 기온 데이터 간의 **최소제곱오차(MSE)를 최소화하는 단일 직선**($y = wx + b$)을 도출합니다.\n\n'
      '**특징 및 차이점:**\n'
      '- 거시적인 장기 기온 상승 추세를 가장 단순하고 명확하게 보여줍니다.'
  )

with col2:
  st.markdown('### ② 다항 회귀')
  st.markdown(
      '**작동 원리 (`PolynomialFeatures + LinearRegression`):**\n'
      '- 연도 데이터를 2차 다항식 특성으로 확장하여 **포물선 형태의 곡선**으로 데이터에 피팅합니다.\n\n'
      '**특징 및 차이점:**\n'
      '- 최근 기온 상승 속도가 가속화되는 비선형적 패턴을 유연하게 반영합니다.'
  )

with col3:
  st.markdown('### ③ 릿지 회귀')
  st.markdown(
      '**작동 원리 (`Ridge`):**\n'
      '- 선형 회귀에 **L2 규제(Penalty)**를 더해 가중치가 너무 급격하게 튀는 것을 방지합니다.\n\n'
      '**특징 및 차이점:**\n'
      '- 데이터 내 노이즈나 급격한 변동에 덜 민감하며, 먼 미래 예측 시 과적합(Overfitting)을 안정적으로 억제합니다.'
  )

# --- 8. 상세 데이터 테이블 ---
with st.expander('📊 연도별 머신러닝 예측 데이터 확인'):
  pred_df = pd.DataFrame({
      '연도': x_fut,
      '선형회귀(℃)': np.round(pred_lr, 2),
      '다항회귀(℃)': np.round(pred_poly, 2),
      '릿지회귀(℃)': np.round(pred_ridge, 2),
  })
  st.dataframe(pred_df[pred_df['연도'] >= max_data_year].set_index('연도'))
