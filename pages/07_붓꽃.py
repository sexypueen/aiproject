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

# --- [그래프 한글 및 마이너스 부호 깨짐 방지 설정] ---
plt.rcParams['font.family'] = 'DejaVu Sans'
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
st.set_page_config(page_title="핑크 붓꽃 품종 예측기", page_icon="🌸", layout="centered")

# --- [화사한 핑크 테마 CSS 스타일링] ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #fff0f3 0%, #ffccd5 100%);
        color: #4a1525;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #d81b60 0%, #ad1457 100%);
        color: white;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ad1457, #ff4081);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .custom-card {
        background: rgba(255, 255, 255, 0.85);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(216, 27, 96, 0.15);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 182, 193, 0.4);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 메인 타이틀
st.markdown('<p class="main-title">🌸 핑크빛 붓꽃(Iris) AI 스마트 품종 예측기</p>', unsafe_allow_html=True)
st.markdown("**다양한 머신러닝 알고리즘**을 통해 꽃잎 치수에 따른 품종을 예측하고 화사하게 시각화합니다.")
st.write("")

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

model_choice = st.sidebar.selectbox(
    "분류 알고리즘 선택",
    ("랜덤 포레스트 (Random Forest)", "K-최근접 이웃 (KNN)", "결정 트리 (Decision Tree)")
)

st.sidebar.markdown("---")
st.sidebar.header("📏 꽃잎 치수 범위 설정")

min_l = st.sidebar.slider("최소 꽃잎 길이", 0.0, 3.0, 0.5, 0.1)
max_l = st.sidebar.slider("최대 꽃잎 길이", 5.0, 9.0, 7.5, 0.1)
min_w = st.sidebar.slider("최소 꽃잎 너비", 0.0, 1.0, 0.1, 0.1)
max_w = st.sidebar.slider("최대 꽃잎 너비", 2.0, 4.0, 3.0, 0.1)

st.sidebar.markdown("---")
st.sidebar.header("🎯 입력 값 조정")
petal_length = st.sidebar.slider("꽃잎 길이 (Petal Length)", min_value=min_l, max_value=max_l, value=3.8, step=0.1)
petal_width = st.sidebar.slider("꽃잎 너비 (Petal Width)", min_value=min_w, max_value=max_w, value=1.2, step=0.1)

# 4. 모델 학습
if model_choice == "랜덤 포레스트 (Random Forest)":
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model_desc = "**랜덤 포레스트**는 여러 개의 결정 트리를 결합하여 과적합을 방지하고 높은 정확도를 자랑하는 앙상블 알고리즘입니다."
elif model_choice == "K-최근접 이웃 (KNN)":
    model = KNeighborsClassifier(n_neighbors=5)
    model_desc = "**K-최근접 이웃(KNN)**은 새로운 데이터와 가장 가까운 $K$개의 이웃 데이터 성향을 참고해 다수결로 품종을 결정하는 직관적인 거리 기반 알고리즘입니다."
else:
    model = DecisionTreeClassifier(max_depth=4, random_state=42)
    model_desc = "**결정 트리**는 예/아니오의 질문 규칙들을 나무 구조로 만들어 직관적으로 분류 기준을 학습하는 알고리즘입니다."

model.fit(X, y)

# 5. 예측 수행
user_input = np.array([[petal_length, petal_width]])
prediction = model.predict(user_input)[0]
probabilities = model.predict_proba(user_input)[0]
predicted_species = class_names[prediction]

# 6. 예측 결과 카드 출력
st.markdown('<div class="custom-card">', unsafe_allow_html=True)
st.subheader("🔍 예측 결과 및 분석")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.success(f"**예측 품종:**\n### {predicted_species}")
    st.write(f"- 선택 모델: **{model_choice}**")
    st.write(f"- 입력 길이: **{petal_length} cm**")
    st.write(f"- 입력 너비: **{petal_width} cm**")

with col2:
    st.write("**품종별 예측 확률**")
    prob_df = pd.DataFrame({
        "품종": class_names,
        "확률 (%)": np.round(probabilities * 100, 1)
    })
    st.dataframe(prob_df, hide_index=True, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# 7. 알고리즘 설명 박스
st.info(f"📌 **알고리즘 가이드:**\n\n{model_desc}")

# 8. 결정 경계 및 무지개색 별 시각화 카드
st.markdown('<div class="custom-card">', unsafe_allow_html=True)
st.subheader("📊 분류 경계 및 무지개 위치 시각화")
st.caption("배경 색상은 모델의 학습 영역이며, 무지개색 별(★) 마커는 사용자가 입력한 좌표의 위치입니다.")

fig, ax = plt.subplots(figsize=(8, 6))

x_min, x_max = 0.0, 7.8
y_min, y_max = 0.0, 3.2
xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.02),
                     np.arange(y_min, y_max, 0.02))

Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

bg_colors = ['#ffccd5', '#d8f3dc', '#bde0fe']
cmap_bg = ListedColormap(bg_colors)
ax.contourf(xx, yy, Z, alpha=0.45, cmap=cmap_bg)
ax.contour(xx, yy, Z, colors='gray', linestyles='--', linewidths=0.8)

point_colors = ['#c71585', '#2a9d8f', '#1d3557']
for idx, species in enumerate(class_names):
    ax.scatter(X[y == idx, 0], X[y == idx, 1],
               c=point_colors[idx], label=species,
               edgecolors='white', s=60, alpha=0.85)

rainbow_colors = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#4B0082', '#9400D3']
sizes = [700, 560, 420, 300, 200, 120, 50]

for i, (color, size) in enumerate(zip(rainbow_colors, sizes)):
    ax.scatter(petal_length, petal_width,
               marker='*', s=size, color=color,
               edgecolors='black' if i == 0 else 'none',
               linewidths=1.2 if i == 0 else 0,
               zorder=10 + i,
               label='사용자 입력값 (★)' if i == 0 else "")

ax.set_xlabel("꽃잎 길이 (cm)", fontsize=12, fontweight='bold')
ax.set_ylabel("꽃잎 너비 (cm)", fontsize=12, fontweight='bold')
ax.set_title(f"[{model_choice}] 결정 영역 분석", fontsize=13, fontweight='bold')
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)
ax.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
ax.grid(True, linestyle=':', alpha=0.5)

st.pyplot(fig)
st.markdown('</div>', unsafe_allow_html=True)

# 9. 분류 요약
st.markdown(
    f"💡 **분류 분석 요약:** 선택하신 **{model_choice}** 모델은 입력하신 치수(`{petal_length}cm`, `{petal_width}cm`)를 기반으로 "
    f"영역 판정을 내려 **{predicted_species}**(확률: **{probabilities[prediction]*100:.1f}%**)로 최종 분류하였습니다."
)
