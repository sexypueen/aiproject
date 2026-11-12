import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import platform

# 운영체제별 한글 폰트 설정
if platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':
    plt.rc('font', family='AppleGothic')
else:
    # 스트림릿 클라우드 (Linux) 환경
    plt.rc('font', family='NanumGothic')

plt.rcParams['axes.unicode_minus'] = False
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris

# 1. 페이지 설정
st.set_page_config(page_title="붓꽃(Iris) 품종 예측기", page_icon="🌸", layout="centered")
st.title("🌸 붓꽃(Iris) 품종 예측 및 분류 시각화")
st.write("꽃잎의 길이와 너비를 입력하면 **랜덤 포레스트(Random Forest)** 알고리즘이 품종을 예측하고, 분류 근거를 시각화합니다.")

# 2. 데이터 로드 및 모델 학습 (캐싱 처리로 속도 최적화)
@st.cache_resource
def load_and_train():
    try:
        # 업로드된 iris.csv가 있는 경우 우선 로드 (cp949 인코딩 대응)
        df = pd.read_csv('iris.csv', encoding='cp949')
        X = df[['꽃잎길이', '꽃잎너비']].values
        y_raw = df['품종'].values
        class_names = ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']
        y = np.array([class_names.index(label) for label in y_raw])
    except Exception:
        # 파일이 없을 경우 사이킷런 기본 데이터로 자동 대체
        iris = load_iris()
        X = iris.data[:, [2, 3]]  # 꽃잎길이(Petal length), 꽃잎너비(Petal width)
        y = iris.target
        class_names = ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']

    # 가장 널리 쓰이는 분류 알고리즘 중 하나인 랜덤 포레스트 학습
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    return X, y, model, class_names

X, y, model, class_names = load_and_train()

# 3. 사이드바: 사용자 입력 받기
st.sidebar.header("📏 꽃잎 치수 입력 (cm)")
petal_length = st.sidebar.slider("꽃잎 길이 (Petal Length)", min_value=0.5, max_value=7.5, value=3.8, step=0.1)
petal_width = st.sidebar.slider("꽃잎 너비 (Petal Width)", min_value=0.1, max_value=3.0, value=1.2, step=0.1)

# 4. 예측 수행
user_input = np.array([[petal_length, petal_width]])
prediction = model.predict(user_input)[0]
probabilities = model.predict_proba(user_input)[0]
predicted_species = class_names[prediction]

# 5. 예측 결과 출력
st.subheader("🔍 예측 결과")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.success(f"**예측 품종:**\n### {predicted_species}")
    st.write(f"- 입력 꽃잎 길이: **{petal_length} cm**")
    st.write(f"- 입력 꽃잎 너비: **{petal_width} cm**")

with col2:
    st.write("**품종별 예측 확률**")
    prob_df = pd.DataFrame({
        "품종": class_names,
        "확률 (%)": np.round(probabilities * 100, 1)
    })
    st.dataframe(prob_df, hide_index=True, use_container_width=True)

# 6. 결정 경계 및 무지개색 별 시각화
st.subheader("📊 분류 근거 시각화 (결정 경계)")
st.caption("배경 색상은 모델이 학습한 각 품종의 영역(결정 경계)을 의미하며, 입력한 값이 어느 영역에 속하는지 보여줍니다.")

fig, ax = plt.subplots(figsize=(8, 6))

# 결정 경계(Decision Boundary) 계산을 위한 그리드 생성
x_min, x_max = 0.0, 7.8
y_min, y_max = 0.0, 3.2
xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.02),
                     np.arange(y_min, y_max, 0.02))

Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

# 배경 영역 색칠 (파스텔 톤)
bg_colors = ['#FFCCCC', '#CCFFCC', '#CCE5FF']
from matplotlib.colors import ListedColormap
cmap_bg = ListedColormap(bg_colors)
ax.contourf(xx, yy, Z, alpha=0.45, cmap=cmap_bg)
ax.contour(xx, yy, Z, colors='gray', linestyles='--', linewidths=0.8)

# 기존 150개 데이터 산점도 표시
point_colors = ['#E63946', '#2A9D8F', '#1D3557']
for idx, species in enumerate(class_names):
    ax.scatter(X[y == idx, 0], X[y == idx, 1],
               c=point_colors[idx], label=species,
               edgecolors='white', s=50, alpha=0.85)

# 사용자 입력값을 무지개색 별(★)로 겹쳐서 표시
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
ax.set_title(f"랜덤 포레스트 분류 영역 및 입력 위치 ({predicted_species})", fontsize=13, fontweight='bold')
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)
ax.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
ax.grid(True, linestyle=':', alpha=0.5)

st.pyplot(fig)

# 7. 분류 이유 자동 설명
st.info(
    f"💡 **왜 '{predicted_species}'로 분류되었나요?**\n\n"
    f"랜덤 포레스트 모델은 기존 150개의 붓꽃 데이터를 학습해 각 품종이 분포하는 영역(배경색)을 나누었습니다. "
    f"입력하신 **꽃잎 길이 {petal_length}cm, 너비 {petal_width}cm** 좌표(무지개 별 ★)는 "
    f"**{predicted_species}**의 결정 영역 내부에 위치하며, 결정 트리들의 투표 결과 **{probabilities[prediction]*100:.1f}%**의 확률로 해당 품종으로 판정되었습니다."
)
