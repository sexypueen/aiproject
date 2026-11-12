import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
import os
from matplotlib.colors import ListedColormap
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.datasets import load_iris

# --- [그래프 한글 및 마이너스 부호 깨짐 방지 핵심 설정] ---
plt.rcParams['font.family'] = 'DejaVu Sans'  # 기본 폰트 초기화
if platform.system() == 'Linux':
    font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
    if os.path.exists(font_path):
        fe = fm.FontEntry(fname=font_path, name='NanumGothic')
        fm.fontManager.ttflist.insert(0, fe)
        plt.rc('font', family='NanumGothic')
elif platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':
    plt.rc('font', family='AppleGothic')

plt.rcParams['axes.unicode_minus'] = False

# 1. 페이지 설정
st.set_page_config(page_title="붓꽃(Iris) 품종 예측 비교기", page_icon="🌸", layout="centered")
st.title("🌸 붓꽃(Iris) 품종 다중 알고리즘 예측 및 시각화")
st.write("다양한 머신러닝 분류 알고리즘을 선택하고, 꽃잎 치수를 입력하여 품종 예측 결과와 결정 경계를 비교해 보세요.")

# 2. 데이터 로드 및 전처리
@st.cache_resource
def load_data():
    try:
        df = pd.read_csv('iris.csv', encoding='cp949')
        X = df[['꽃잎길이', '꽃잎너비']].values
        y_raw = df['품종'].values
        class_names = ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']
        y = np.array([class_names.index(label) for label in y_raw])
    except Exception:
        iris = load_iris()
        X = iris.data[:, [2, 3]]
        y = iris.target
        class_names = ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']
    return X, y, class_names

X, y, class_names = load_data()

# 3. 사이드바: 설정 및 입력
st.sidebar.header("⚙️ 모델 및 입력 설정")

# 3-1. 알고리즘 선택 (총 3개)
model_choice = st.sidebar.selectbox(
    "분류 알고리즘 선택",
    ("랜덤 포레스트 (Random Forest)", "K-최근접 이웃 (KNN)", "결정 트리 (Decision Tree)")
)

st.sidebar.markdown("---")
st.sidebar.header("📏 꽃잎 치수 및 범위 입력 (cm)")

# 3-2. 사용자가 입력할 수 있는 값의 범위 설정 (최소/최대/기본값 커스텀)
min_l = st.sidebar.slider("슬라이더 최소 꽃잎 길이", 0.0, 3.0, 0.5, 0.1)
max_l = st.sidebar.slider("슬라이더 최대 꽃잎 길이", 5.0, 9.0, 7.5, 0.1)
min_w = st.sidebar.slider("슬라이더 최소 꽃잎 너비", 0.0, 1.0, 0.1, 0.1)
max_w = st.sidebar.slider("슬라이더 최대 꽃잎 너비", 2.0, 4.0, 3.0, 0.1)

# 실제 사용자 입력 슬라이더
petal_length = st.sidebar.slider("꽃잎 길이 (Petal Length)", min_value=min_l, max_value=max_l, value=3.8, step=0.1)
petal_width = st.sidebar.slider("꽃잎 너비 (Petal Width)", min_value=min_w, max_value=max_w, value=1.2, step=0.1)

# 4. 선택된 알고리즘 학습
if model_choice == "랜덤 포레스트 (Random Forest)":
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model_desc = "**랜덤 포레스트(Random Forest)**는 여러 개의 결정 트리를 생성하고 그 결과를 다수결로 종합하여 예측하는 앙상블 알고리즘입니다. 과적합이 적고 성능이 매우 뛰어납니다."
elif model_choice == "K-최근접 이웃 (KNN)":
    model = KNeighborsClassifier(n_neighbors=5)
    model_desc = "**K-최근접 이웃(KNN)**은 새로운 데이터 주변의 가장 가까운 $K$개의 데이터 플래그를 찾아 다수결 방식으로 품종을 분류하는 직관적인 거리 기반 알고리즘입니다."
else:
    model = DecisionTreeClassifier(max_depth=4, random_state=42)
    model_desc = "**결정 트리(Decision Tree)**는 데이터의 특징들을 기준으로 스고 고개(Yes/No) 질문 형태의 규칙 나무를 만들어 분류를 수행하는 알고리즘입니다."

model.fit(X, y)

# 5. 예측 수행
user_input = np.array([[petal_length, petal_width]])
prediction = model.predict(user_input)[0]
probabilities = model.predict_proba(user_input)[0]
predicted_species = class_names[prediction]

# 6. 예측 결과 출력
st.subheader("🔍 예측 결과")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.success(f"**예측 품종:**\n### {predicted_species}")
    st.write(f"- 선택 모델: **{model_choice}**")
    st.write(f"- 입력 꽃잎 길이: **{petal_length} cm**")
    st.write(f"- 입력 꽃잎 너비: **{petal_width} cm**")

with col2:
    st.write("**품종별 예측 확률**")
    prob_df = pd.DataFrame({
        "품종": class_names,
        "확률 (%)": np.round(probabilities * 100, 1)
    })
    st.dataframe(prob_df, hide_index=True, use_container_width=True)

# 7. 알고리즘 설명 박스
st.info(f"📌 **알고리즘 설명:**\n\n{model_desc}")

# 8. 결정 경계 및 무지개색 별 시각화
st.subheader("📊 분류 근거 시각화 (결정 경계)")
st.caption("배경 색상은 선택한 모델이 학습한 품종별 영역을 나타내며, 무지개색 별(★)은 사용자가 입력한 값의 위치입니다.")

fig, ax = plt.subplots(figsize=(8, 6))

x_min, x_max = 0.0, 7.8
y_min, y_max = 0.0, 3.2
xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.02),
                     np.arange(y_min, y_max, 0.02))

Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

bg_colors = ['#FFCCCC', '#CCFFCC', '#CCE5FF']
cmap_bg = ListedColormap(bg_colors)
ax.contourf(xx, yy, Z, alpha=0.45, cmap=cmap_bg)
ax.contour(xx, yy, Z, colors='gray', linestyles='--', linewidths=0.8)

point_colors = ['#E63946', '#2A9D8F', '#1D3557']
for idx, species in enumerate(class_names):
    ax.scatter(X[y == idx, 0], X[y == idx, 1],
               c=point_colors[idx], label=species,
               edgecolors='white', s=50, alpha=0.85)

# 무지개색 별(★)로 입력값 표시
rainbow_colors = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#4B0082', '#9400D3']
sizes = [650, 520, 400, 300, 210, 130, 60]

for i, (color, size) in enumerate(zip(rainbow_colors, sizes)):
    ax.scatter(petal_length, petal_width,
               marker='*', s=size, color=color,
               edgecolors='black' if i == 0 else 'none',
               linewidths=1.2 if i == 0 else 0,
               zorder=10 + i,
               label='사용자 입력값 (예측 위치)' if i == 0 else "")

ax.set_xlabel("꽃잎 길이 (cm)", fontsize=12, fontweight='bold')
ax.set_ylabel("꽃잎 너비 (cm)", fontsize=12, fontweight='bold')
ax.set_title(f"[{model_choice}] 결정 영역 및 입력 위치 ({predicted_species})", fontsize=13, fontweight='bold')
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)
ax.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
ax.grid(True, linestyle=':', alpha=0.5)

st.pyplot(fig)

# 9. 분류 이유 상세 설명
st.markdown(
    f"💡 **분류 분석 요약:**\n\n"
    f"현재 선택하신 **{model_choice}** 모델 기준, 입력하신 꽃잎 좌표(`{petal_length}cm`, `{petal_width}cm`)는 "
    f"해당 모델의 학습 규칙에 따라 **{predicted_species}** 영역에 배정되었습니다. "
    f"확률 모델 산출 결과 **{probabilities[prediction]*100:.1f}%**의 신뢰도로 판정되었습니다."
)
