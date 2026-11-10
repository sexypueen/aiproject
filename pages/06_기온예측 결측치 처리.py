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
    page_title='서울 기온 AI 예측 및 결측치 비교 대시보드',
    page_icon='🌡️',
    layout='wide',
)

st.title('🌡️ 서울 월별 기온 AI 예측 & 결측치 처리/알고리즘 비교 대시보드')
st.write(
    '결측치 처리 방식과 Scikit-learn 머신러닝 알고리즘 선택에 따른 미래 기온'
    ' 예측값의 변화를 실시간으로 비교합니다.'
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

# --- 3. 사이드바 설정 (조건 입력) ---
st.sidebar.header('⚙️ 대시보드 설정')

# 개월 선택
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
    '분석할 개월 선택:',
    options=list(month_dict.keys()),
    format_func=lambda x: month_dict[x],
)

# 결측치 처리 방법 선택
impute_method = st.sidebar.selectbox(
    '결측치 처리 방식 선택:',
    options=['1. 제거 (Drop)', '2. 중앙값 대체 (Median)', '3. 선형보간 (Interpolation)'],
)

# 알고리즘 선택
st.sidebar.markdown('---')
st.sidebar.subheader('🤖 머신러닝 알고리즘 선택')
use_lr = st.sidebar.checkbox('① 선형 회귀 (Linear Regression)', value=True)
use_poly = st.sidebar.checkbox(
    '② 다항 회귀 (Polynomial Regression, 2차)', value=True
)
use_ridge = st.sidebar.checkbox(
    '③ 릿지 회귀 (Ridge Regression, 규제)', value=True
)

# 미래 예측 연도 입력
max_data_year = 2025
target_year = st.sidebar.number_input(
    '미래 예측 연도 입력:',
    min_value=max_data_year + 1,
    max_value=2100,
    value=max_data_year + 15,
    step=1,
)

# --- 4. 데이터 전처리 및 결측치 핸들링 ---
all_years = np.arange(df['연도'].min(), max_data_year + 1)
base_df = pd.DataFrame({'연도': all_years})

m_df = (
    df[(df['월'] == selected_month) & (df['연도'] <= max_data_year)]
    .groupby('연도')['평균기온(℃)']
    .mean()
    .reset_index()
)

merged_df = pd.merge(base_df, m_df, on='연도', how='left').sort_values('연도')

raw_missing_count = int(merged_df['평균기온(℃)'].isna().sum())

if '1. 제거' in impute_method:
  clean_df = merged_df.dropna(subset=['평균기온(℃)'])
  method_name = '결측치 제거'
elif '2. 중앙값' in impute_method:
  clean_df = merged_df.copy()
  med_val = clean_df['평균기온(℃)'].median()
  clean_df['평균기온(℃)'] = clean_df['평균기온(℃)'].fillna(med_val)
  method_name = f'중앙값 대체 ({med_val:.1f}℃)'
else:  # 선형보간
  clean_df = merged_df.copy()
  clean_df['평균기온(℃)'] = clean_df['평균기온(℃)'].interpolate(
      method='linear'
  )
  clean_df['평균기온(℃)'] = clean_df['평균기온(℃)'].bfill().ffill()
  method_name = '선형보간 (Interpolation)'

X_past = clean_df['연도'].values.reshape(-1, 1)
y_past = clean_df['평균기온(℃)'].values
future_years = np.arange(int(X_past.min()), target_year + 1).reshape(-1, 1)
x_fut = future_years.flatten()

# --- 5. 선택한 알고리즘에 따른 모델 학습 및 예측 ---
predictions = {}

if use_lr:
  model_lr = LinearRegression()
  model_lr.fit(X_past, y_past)
  predictions['선형 회귀'] = model_lr.predict(future_years)

if use_poly:
  model_poly = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
  model_poly.fit(X_past, y_past)
  predictions['다항 회귀 (2차)'] = model_poly.predict(future_years)

if use_ridge:
  model_ridge = Ridge(alpha=10.0)
  model_ridge.fit(X_past, y_past)
  predictions['릿지 회귀'] = model_ridge.predict(future_years)

# --- 6. 화면 출력 및 시각화 ---
st.subheader(
    f'📈 서울 {month_dict[selected_month]} 기온 분석 및 AI 예측 (적용 방식:'
    f' {method_name})'
)
# 수정된 오타 부위 ({raw_missing_count}개)
st.info(
    f'💡 선택하신 개월의 전체 기간 중 발견된 결측치 개수:'
    f' **{raw_missing_count}개** | 선택된 결측치 처리법: **{impute_method}**'
)

fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(
    X_past.flatten(),
    y_past,
    marker='o',
    color='black',
    linewidth=1.5,
    markersize=3,
    label=f'실제 평균기온 ({method_name})',
)

colors = {'선형 회귀': 'red', '다항 회귀 (2차)': 'blue', '릿지 회귀': 'green'}
styles = {'선형 회귀': '--', '다항 회귀 (2차)': '-.', '릿지 회귀': ':'}

future_mask = x_fut >= max_data_year
bridge_idx = np.where(x_fut >= max_data_year)[0][0] - 1
if bridge_idx < 0:
  bridge_idx = 0
x_plot = x_fut[bridge_idx:]

for algo_name, pred_vals in predictions.items():
  ax.plot(
      x_plot,
      pred_vals[bridge_idx:],
      color=colors.get(algo_name, 'purple'),
      linestyle=styles.get(algo_name, '-'),
      linewidth=2.5,
      label=f'AI 예측: {algo_name}',
  )

ax.set_title(
    f'서울 {month_dict[selected_month]} 기온 예측 비교 ({method_name})',
    fontsize=14,
    fontweight='bold',
)
ax.set_xlabel('연도 (Year)', fontsize=12)
ax.set_ylabel('평균기온 (℃)', fontsize=12)
ax.legend(loc='upper left', fontsize=10)
ax.grid(True, linestyle='--', alpha=0.6)

st.pyplot(fig)

# --- 7. 결측치 처리 방식별 특징 및 알고리즘 설명 ---
st.markdown('---')
col_desc1, col_desc2 = st.columns(2)

with col_desc1:
  st.subheader('🔍 결측치 처리 방식별 특징')
  st.markdown(
      '- **1. 제거 (Drop):** 결측치가 있는 연도를 아예 분석에서 제외하므로 왜곡은 없으나 데이터 손실이 발생합니다.\n'
      '- **2. 중앙값 대체:** 데이터의 전체적인 중심 경향을 유지하며 빈자리를 메우지만, 트렌드 반영이 다소 뭉개질 수 있습니다.\n'
      '- **3. 선형보간:** 앞뒤 데이터의 흐름을 이어 부드럽게 채워주어 시계열 데이터의 연속성을 가장 잘 유지합니다.'
  )

with col_desc2:
  st.subheader('🤖 선택한 알고리즘 작동 원리')
  st.markdown(
      '- **선형 회귀:** 데이터 전반의 거시적 상승/하강 추세를 단순 직선($y=wx+b$)으로 피팅합니다.\n'
      '- **다항 회귀:** 2차 포물선 형태로 최근의 가속화되는 변화를 유연하게 반영합니다.\n'
      '- **릿지 회귀:** L2 규제를 더해 과적합(Overfitting)을 방지하고 안정적인 예측선을 만듭니다.'
  )

# --- 8. 상세 데이터 테이블 ---
with st.expander('📊 연도별 예측 결과 데이터 테이블 확인'):
  if predictions:
    pred_table_dict = {'연도': x_fut}
    for algo_name, pred_vals in predictions.items():
      pred_table_dict[f'{algo_name} 예측(℃)'] = np.round(pred_vals, 2)
    pred_df = pd.DataFrame(pred_table_dict)
    st.dataframe(pred_df[pred_df['연도'] >= max_data_year].set_index('연도'))
  else:
    st.warning('사이드바에서 최소 하나 이상의 알고리즘을 선택해 주세요.')
