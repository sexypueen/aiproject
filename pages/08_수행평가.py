from pathlib import Path
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# 1. 페이지 설정 및 화려한 공룡 테마 스타일 🦕🌋🌈
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="공룡 식성·세대 퀴즈 & 다중 기록 탐험기 🦕✨",
    page_icon="🦕",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Jua&family=Noto+Sans+KR:wght@400;600;800&display=swap');

    /* 전체 배경: 햇살 비치는 정글 그린 + 핑크/라임/스카이 화사한 그라데이션 & 은은한 공룡/발자국 패턴 🌿🦕 */
    .stApp {
        background:
            radial-gradient(circle at 12% 15%, rgba(255, 182, 213, 0.42) 0%, transparent 38%),
            radial-gradient(circle at 88% 18%, rgba(255, 224, 102, 0.42) 0%, transparent 36%),
            radial-gradient(circle at 80% 85%, rgba(125, 211, 252, 0.42) 0%, transparent 40%),
            linear-gradient(160deg, #e8f8ee 0%, #f3fff7 45%, #fff7ed 100%);
        font-family: 'Noto Sans KR', sans-serif;
    }

    /* 사이드바: 열대 정글 & 화산 노을 톤 🌴🔥 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #134e4a 0%, #1e3a5f 55%, #4c1d95 100%);
        border-right: 3px solid #6ee7b7;
    }
    [data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }
    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background-color: #ec4899 !important;
        color: #ffffff !important;
    }

    /* 메인 히어로 배너 🦖✨ */
    .dino-hero {
        background: linear-gradient(120deg, #ff6b9d 0%, #ff9f43 32%, #2ecc71 68%, #00b4d8 100%);
        border: 3px solid #ffffff;
        border-radius: 24px;
        padding: 26px 30px;
        margin-bottom: 18px;
        box-shadow: 0 12px 30px rgba(16, 185, 129, 0.22);
        color: #ffffff;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.22);
    }
    .dino-hero h1 {
        font-family: 'Jua', 'Noto Sans KR', sans-serif;
        font-size: 2.3rem;
        margin: 0 0 8px 0;
        color: #ffffff !important;
    }
    .dino-hero p {
        margin: 0;
        font-size: 1.05rem;
        font-weight: 600;
        color: #fffef7 !important;
    }

    /* 메트릭 카드 화려하게 꾸미기 🏆 */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.88);
        border: 2px solid #a7f3d0;
        border-radius: 18px;
        padding: 14px 18px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.07);
        backdrop-filter: blur(8px);
    }
    [data-testid="stMetricLabel"] {
        color: #047857 !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricValue"] {
        color: #be185d !important;
        font-weight: 800 !important;
    }

    /* 퀴즈 카드: 반짝이는 공룡 탐험 카드 🦕💎 */
    .quiz-card {
        background:
            radial-gradient(circle at top right, rgba(251, 207, 232, 0.65), transparent 45%),
            radial-gradient(circle at bottom left, rgba(167, 243, 208, 0.65), transparent 45%),
            rgba(255, 255, 255, 0.92);
        border: 3px solid #f472b6;
        border-radius: 24px;
        padding: 28px;
        margin-top: 10px;
        margin-bottom: 18px;
        box-shadow: 0 14px 32px rgba(244, 114, 182, 0.18);
    }
    .dino-title {
        font-family: 'Jua', 'Noto Sans KR', sans-serif;
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #065f46, #db2777, #2563eb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .sub-badge {
        display: inline-block;
        background: linear-gradient(90deg, #fef08a, #fbcfe8);
        border: 1.5px solid #f472b6;
        color: #831843;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 0.92rem;
        font-weight: 700;
        margin-right: 8px;
        margin-bottom: 6px;
    }

    /* 버튼 스타일 업그레이드 🎉 */
    .stButton > button {
        border-radius: 14px !important;
        font-weight: 700 !important;
        border: 2px solid #34d399 !important;
        transition: transform 0.12s ease, box-shadow 0.12s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(16, 185, 129, 0.25) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# 2. 데이터 로드 및 클리닝 🧹
# ---------------------------------------------------------------------------
def clean_text(val: object) -> str:
    if pd.isna(val):
        return ""
    s = str(val).replace("\xa0", " ").strip()
    s = "".join(ch for ch in s if ch.isprintable() and ord(ch) != 63867)
    return " ".join(s.split())


def simplify_diet(raw_diet: str) -> str:
    low = raw_diet.lower().strip()
    if not low or "unknown" in low or "?" in low:
        return "불명/미상 ❓"
    if "omnivor" in low or "/" in low:
        if "herbivore" in low and "omnivore" not in low and "carnivore" not in low:
            return "초식 🌿"
        if "carnivore" in low and "omnivore" not in low and "herbivore" not in low:
            return "육식 🥩"
        return "잡식/혼합 🍖🌿"
    if "herbivore" in low:
        return "초식 🌿"
    if "carnivore" in low:
        return "육식 🥩"
    return f"{raw_diet} 🦖"


def simplify_era(raw_era: str) -> str:
    low = raw_era.lower().strip()
    if not low or "unknown" in low or "?" in low:
        return "불명/미상 ❓"
    if "/" in low or " or " in low or "-" in low:
        return "경계/혼합 시대 ⏳"
    if "cretaceous" in low:
        return "백악기 (Cretaceous) 🌋"
    if "jurassic" in low:
        return "쥐라기 (Jurassic) 🌿"
    if "triassic" in low:
        return "트라이아스기 (Triassic) 🌍"
    return f"{raw_era} ⏳"


@st.cache_data
def load_dino_data() -> pd.DataFrame:
    candidate_paths = [Path("dino.csv"), Path("data/dino.csv")]
    csv_path = next((p for p in candidate_paths if p.exists()), None)
    if csv_path is None:
        raise FileNotFoundError(
            "dino.csv 파일을 찾을 수 없어요! 저장소 루트나 data/ 폴더에 넣어주세요. 📂"
        )

    df = pd.read_csv(csv_path, encoding="cp949")
    for col in df.columns:
        df[col] = df[col].apply(clean_text)

    df["식성_분류"] = df["식성"].apply(simplify_diet)
    df["세대_분류"] = df["세대"].apply(simplify_era)
    name_counts = df["이름"].value_counts()
    df["중복_기록_수"] = df["이름"].map(name_counts)
    return df


try:
    df = load_dino_data()
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()


# ---------------------------------------------------------------------------
# 3. 세션 상태 초기화 🎯
# ---------------------------------------------------------------------------
if "score" not in st.session_state:
    st.session_state.score = 0
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "best_streak" not in st.session_state:
    st.session_state.best_streak = 0
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "current_q" not in st.session_state:
    st.session_state.current_q = None
if "answered" not in st.session_state:
    st.session_state.answered = False
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "trigger_balloons" not in st.session_state:
    st.session_state.trigger_balloons = False


def pick_new_question(pool_df: pd.DataFrame, mode: str) -> dict:
    row = pool_df.sample(1).iloc[0]
    if mode == "식성 맞추기 🥩🌿":
        answer = row["식성_분류"]
        candidates = sorted(pool_df["식성_분류"].unique().tolist())
    else:
        answer = row["세대_분류"]
        candidates = sorted(pool_df["세대_분류"].unique().tolist())

    others = [c for c in candidates if c != answer]
    k = min(3, len(others))
    sampled_others = pd.Series(others).sample(k, replace=False).tolist() if k > 0 else []
    options = [answer] + sampled_others
    options = pd.Series(options).sample(len(options), replace=False).tolist()

    return {
        "row": row.to_dict(),
        "mode": mode,
        "answer": answer,
        "options": options,
    }


# ---------------------------------------------------------------------------
# 4. 사이드바 🎛️
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("🌴 공룡 탐험 컨트롤러")
    st.caption("원하는 시대나 식성 조건으로 퀴즈 출제 범위를 좁혀보세요! 🔍✨")

    era_filter = st.multiselect(
        "세대 필터 ⏳",
        options=sorted(df["세대_분류"].unique().tolist()),
        default=[],
        placeholder="전체 세대 출제",
    )
    diet_filter = st.multiselect(
        "식성 필터 🍽️",
        options=sorted(df["식성_분류"].unique().tolist()),
        default=[],
        placeholder="전체 식성 출제",
    )

    filtered_df = df.copy()
    if era_filter:
        filtered_df = filtered_df[filtered_df["세대_분류"].isin(era_filter)]
    if diet_filter:
        filtered_df = filtered_df[filtered_df["식성_분류"].isin(diet_filter)]

    if filtered_df.empty:
        st.warning("선택한 조건에 맞는 공룡 데이터가 없어요! 필터를 넓혀주세요. 😅")
        filtered_df = df

    st.divider()
    st.metric("총 공룡 기록 수 🦖", f"{len(df):,}건")
    st.metric("현재 문제 풀 🦕", f"{len(filtered_df):,}건")

    if st.button("🔄 점수·연속 정답 초기화", use_container_width=True):
        st.session_state.score = 0
        st.session_state.streak = 0
        st.session_state.best_streak = 0
        st.session_state.question_count = 0
        st.session_state.current_q = None
        st.session_state.answered = False
        st.session_state.last_result = None
        st.session_state.trigger_balloons = False
        st.rerun()


# ---------------------------------------------------------------------------
# 5. 메인 화려한 배너 & 스코어보드 🏆
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="dino-hero">
        <h1>🦕 쥬라기 & 백악기 공룡 퀴즈 월드 🌋🌈</h1>
        <p>정답을 맞추면 하늘 위로 풍선이 팡팡! 🎈 공룡 식성·세대 퀴즈와 다중 기록 탐험을 즐겨보세요 ✨</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 정답 맞췄을 때 풍선 띄우기 🎈
if st.session_state.trigger_balloons:
    st.balloons()
    st.session_state.trigger_balloons = False

m1, m2, m3, m4 = st.columns(4)
m1.metric("누적 점수 ⭐", f"{st.session_state.score}점")
m2.metric("현재 연속 정답 🔥", f"{st.session_state.streak}연속")
m3.metric("최고 연속 정답 👑", f"{st.session_state.best_streak}연속")
m4.metric("도전한 문제 수 📝", f"{st.session_state.question_count}문제")

tab1, tab2 = st.tabs(["🎮 공룡 퀴즈 도전", "🗂️ 다중 기록 공룡 탐험기"])


# ---------------------------------------------------------------------------
# 탭 1: 공룡 퀴즈 도전 🎮
# ---------------------------------------------------------------------------
with tab1:
    col_mode, col_btn = st.columns([3, 1])
    with col_mode:
        quiz_mode = st.radio(
            "퀴즈 유형 선택 🎯",
            options=["식성 맞추기 🥩🌿", "세대 맞추기 ⏳🌋"],
            horizontal=True,
        )
    with col_btn:
        st.write("")
        if st.button("🎲 새 문제 뽑기", use_container_width=True):
            st.session_state.current_q = pick_new_question(filtered_df, quiz_mode)
            st.session_state.answered = False
            st.session_state.last_result = None
            st.session_state.trigger_balloons = False
            st.rerun()

    if (
        st.session_state.current_q is None
        or st.session_state.current_q["mode"] != quiz_mode
    ):
        st.session_state.current_q = pick_new_question(filtered_df, quiz_mode)
        st.session_state.answered = False
        st.session_state.last_result = None
        st.session_state.trigger_balloons = False

    q = st.session_state.current_q
    dino = q["row"]

    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="dino-title">🦖 {dino["이름"]}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<span class="sub-badge">📍 발견 지역: {dino["나라"] or "미상"}</span>'
        f'<span class="sub-badge">📚 동일 이름 기록: {dino["중복_기록_수"]}건</span>',
        unsafe_allow_html=True,
    )
    st.write("")

    if quiz_mode == "식성 맞추기 🥩🌿":
        st.markdown(
            f"**{dino['이름']}**의 식성은 무엇일까요? 🍽️ *(원본 세대 힌트: `{dino['세대']}`)*"
        )
    else:
        st.markdown(
            f"**{dino['이름']}**이 살았던 시대는 언제일까요? ⏳ *(원본 식성 힌트: `{dino['식성']}`)*"
        )

    selected_option = st.radio(
        "정답을 골라보세요 👇",
        options=q["options"],
        key=f"opt_{st.session_state.question_count}_{dino['이름']}_{quiz_mode}",
    )

    submit_col, next_col = st.columns([1, 1])
    with submit_col:
        submit_clicked = st.button(
            "✅ 정답 확인하기",
            type="primary",
            disabled=st.session_state.answered,
            use_container_width=True,
        )
    with next_col:
        next_clicked = st.button("➡️ 다음 문제", use_container_width=True)

    if submit_clicked and not st.session_state.answered:
        st.session_state.answered = True
        st.session_state.question_count += 1
        if selected_option == q["answer"]:
            st.session_state.score += 10
            st.session_state.streak += 1
            st.session_state.best_streak = max(
                st.session_state.best_streak, st.session_state.streak
            )
            st.session_state.trigger_balloons = True
            st.session_state.last_result = (
                "correct",
                f"정답이에요! 🎈🎉 (+10점, {st.session_state.streak}연속 정답 🔥)",
            )
        else:
            st.session_state.streak = 0
            st.session_state.trigger_balloons = False
            st.session_state.last_result = (
                "wrong",
                f"아쉬워요! 😅 정답은 **{q['answer']}** 입니다.",
            )
        st.rerun()

    if next_clicked:
        st.session_state.current_q = pick_new_question(filtered_df, quiz_mode)
        st.session_state.answered = False
        st.session_state.last_result = None
        st.session_state.trigger_balloons = False
        st.rerun()

    if st.session_state.last_result is not None:
        kind, msg = st.session_state.last_result
        if kind == "correct":
            st.success(msg)
        else:
            st.error(msg)

        st.info(
            f"🔎 **상세 기록** — 이름: `{dino['이름']}` | "
            f"세대: `{dino['세대']}` ({dino['세대_분류']}) | "
            f"식성: `{dino['식성']}` ({dino['식성_분류']}) | "
            f"나라: `{dino['나라']}`"
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 탭 2: 다중 기록 공룡 탐험기 🗂️
# ---------------------------------------------------------------------------
with tab2:
    st.subheader("같은 이름이지만 여러 기록으로 등장하는 공룡들 📚🦖")
    st.write(
        "데이터셋에서 `이름`이 2번 이상 등장하는 공룡들을 골라 지역·세대·식성 차이를 비교해 보세요! 🔍✨"
    )

    dup_df = df[df["중복_기록_수"] >= 2].sort_values(["이름", "나라"])
    dup_names = sorted(dup_df["이름"].unique().tolist())

    selected_dino = st.selectbox("탐험할 공룡 이름 선택 🦕", options=dup_names)
    one_dino_df = dup_df[dup_df["이름"] == selected_dino][
        ["이름", "세대", "세대_분류", "식성", "식성_분류", "나라"]
    ].reset_index(drop=True)

    st.write(f"**{selected_dino}** 총 기록 수: **{len(one_dino_df)}건** ✨")
    st.dataframe(one_dino_df, use_container_width=True, hide_index=True)

    with st.expander("📋 전체 다중 기록 공룡 목록 보기"):
        st.dataframe(
            dup_df[["이름", "중복_기록_수", "세대", "식성", "나라"]].reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )
