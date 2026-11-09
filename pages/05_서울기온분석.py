import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="월별 기온 분석기", page_icon="🌡️", layout="wide"
)

st.title("🌡️ 월별 기온 분석 대시보드")
st.write(
    "사용자가 선택한 월의 연도별 최고 기온과 최저 기온 변화를 시각화합니다."
)


# 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
  # cp949 인코딩으로 파일 로드
  df = pd.read_csv("temperature.csv", encoding="cp949")
  # '일시' 컬럼을 datetime 형식으로 변환 (예: Oct-07 -> 2007-10-01)
  df["일시"] = pd.to_datetime(df["일시"], format="%b-%y")
  df["연도"] = df["일시"].dt.year
  df["월"] = df["일시"].dt.month
  return df


# 데이터 불러오기
try:
  df = load_data()
except Exception as e:
  st.error(
      f"데이터 파일을 불러오는 중 오류가 발생했습니다. 'temperature.csv' 파일이"
      f" 올바른 위치에 있는지 확인하세요.\n오류 내용: {e}"
  )
  st.stop()

# 월 선택 셀렉트박스 (1월 ~ 12월)
month_dict = {
    1: "1월",
    2: "2월",
    3: "3월",
    4: "4월",
    5: "5월",
    6: "6월",
    7: "7월",
    8: "8월",
    9: "9월",
    10: "10월",
    11: "11월",
    12: "12월",
}

selected_month_num = st.selectbox(
    "분석할 월을 선택하세요:",
    options=list(month_dict.keys()),
    format_func=lambda x: month_dict[x],
)

# 선택한 월에 해당하는 데이터 필터링
filtered_df = df[df["월"] == selected_month_num].sort_values("연도")

if filtered_df.empty:
  st.warning("선택한 월에 해당하는 데이터가 없습니다.")
else:
  # 그래프 그리기
  fig, ax = plt.subplots(figsize=(10, 5))

  # 최고기온 (빨강색), 최저기온 (파란색)
  ax.plot(
      filtered_df["연도"],
      filtered_df["최고기온(℃)"],
      color="red",
      marker="o",
      linewidth=2,
      label="최고기온",
  )
  ax.plot(
      filtered_df["연도"],
      filtered_df["최저기온(℃)"],
      color="blue",
      marker="s",
      linewidth=2,
      label="최저기온",
  )

  # 그래프 제목 및 축 이름 설정
  ax.set_title(
      f"월별 기온분석 ({month_dict[selected_month_num]})",
      fontsize=14,
      fontweight="bold",
  )
  ax.set_xlabel("연도", fontsize=12)
  ax.set_ylabel("온도 (℃)", fontsize=12)

  # 범례 표시 (한글 폰트 깨짐 방지를 위해 기본 폰트 사용 또는 환경 설정 반영)
  ax.legend(loc="upper left")
  ax.grid(True, linestyle="--", alpha=0.6)

  # Streamlit에 그래프 출력
  st.pyplot(fig)

  # 데이터 테이블 표시 (선택 사항)
  with st.expander("📊 상세 데이터 보기"):
    st.dataframe(
        filtered_df[["연도", "평균기온(℃)", "최고기온(℃)", "최저기온(℃)"]]
        .reset_index(drop=True)
        .style.format(
            {"평균기온(℃)": "{:.1f}", "최고기온(℃)": "{:.1f}", "최저기온(℃)": "{:.1f}"}
        )
    )
