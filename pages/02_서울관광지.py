import streamlit as st
import folium
from streamlit_folium import st_folium

# 페이지 기본 설정 (와이드 레이아웃 적용)
st.set_page_config(
    page_title="서울 주요 관광지 TOP 10",
    page_icon="✨",
    layout="wide"
)

# [커스텀 CSS] 화려하고 세련된 UI 스타일링
st.markdown("""
    <style>
    /* 전체 배경 및 폰트 감성 업그레이드 */
    .main {
        background-color: #f8f9fa;
    }
    /* 메인 타이틀 그라데이션 효과 */
    .gradient-title {
        background: linear-gradient(90deg, #FF4B4B, #FF8E53);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0px;
    }
    /* 서브 타이틀 */
    .sub-title {
        color: #555555;
        font-size: 1.1rem;
        margin-bottom: 20px;
    }
    /* 카드 디자인 */
    .spot-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-left: 5px solid #FF4B4B;
        transition: transform 0.2s ease;
    }
    .spot-card:hover {
        transform: translateY(-3px);
    }
    </style>
""", unsafe_allow_html=True)

# 데이터 정의 (서울 주요 관광지 TOP 10)
spots = [
    {
        "name": "경복궁",
        "category": "역사 / 문화",
        "lat": 37.5796,
        "lng": 126.9770,
        "desc": "조선 왕조의 대표적인 법궁으로, 한복을 입고 관람하는 외국인 관광객들에게 필수 코스입니다."
    },
    {
        "name": "N서울타워 (남산타워)",
        "category": "랜드마크 / 야경",
        "lat": 37.5512,
        "lng": 126.9882,
        "desc": "서울 시내를 360도로 조망할 수 있는 랜드마크로, 사랑의 자물쇠와 아름다운 야경으로 유명합니다."
    },
    {
        "name": "북촌한옥마을",
        "category": "전통 / 거리",
        "lat": 37.5826,
        "lng": 126.9837,
        "desc": "고즈넉한 기와지붕 아래 한옥 감성과 현대적 분위기가 공존하는 전통 주거지입니다."
    },
    {
        "name": "명동 쇼핑거리",
        "category": "쇼핑 / 길거리 음식",
        "lat": 37.5636,
        "lng": 126.9822,
        "desc": "K-뷰티 쇼핑과 다양한 길거리 음식을 한곳에서 즐길 수 있는 글로벌 대표 핫플레이스입니다."
    },
    {
        "name": "동대문 디자인 플라자 (DDP)",
        "category": "건축 / 쇼핑",
        "lat": 37.5665,
        "lng": 127.0090,
        "desc": "곡선미가 돋보이는 곡면 디자인 건축물로 패션, 디자인 전시 및 화려한 야경을 선사합니다."
    },
    {
        "name": "인사동 쌈지길",
        "category": "전통 / 공예",
        "lat": 37.5743,
        "lng": 126.9849,
        "desc": "한국의 전통 공예품, 찻집, 갤러리가 밀집해 있어 한국 문화의 맛과 멋을 느끼기 좋습니다."
    },
    {
        "name": "홍대 거리",
        "category": "젊음 / K-POP / 버스킹",
        "lat": 37.5563,
        "lng": 126.9226,
        "desc": "스트리트 패션, 인디 음악 버스킹, 이색 카페 등 한국 청년 문화의 중심지입니다."
    },
    {
        "name": "롯데월드타워 & 석촌호수",
        "category": "쇼핑 / 전망대",
        "lat": 37.5126,
        "lng": 127.1025,
        "desc": "123층 높이의 전망대 서울스카이와 대형 쇼핑몰, 석촌호수의 산책로가 어우러진 종합 랜드마크입니다."
    },
    {
        "name": "국립중앙박물관",
        "category": "역사 / 박물관",
        "lat": 37.5240,
        "lng": 126.9804,
        "desc": "대한민국의 방대한 역사 유물과 문화를 한눈에 감상할 수 있는 세계적인 규모의 박물관입니다."
    },
    {
        "name": "반포 한강공원 (무지개분수)",
        "category": "자연 / 휴식",
        "lat": 37.5102,
        "lng": 126.9960,
        "desc": "달빛무지개분수 쇼와 한강 라면 경험 등 서울 도심 속 강변 휴식을 즐기기 좋은 곳입니다."
    }
]

# 상단 헤더 영역
st.markdown('<p class="gradient-title">✨ 외국인이 가장 사랑하는 서울 관광지 TOP 10</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">지도를 통해 위치를 확인하고, 마법 같은 서울의 매력을 만나보세요!</p>', unsafe_allow_html=True)

# 사이드바 설정 (필터 기능 추가로 화려함과 실용성 동시 확보)
st.sidebar.header("🔍 탐색 필터")
categories = ["전체"] + list(set(spot["category"] for spot in spots))
selected_category = st.sidebar.selectbox("관광지 카테고리 선택", categories)

# 필터링 로직
if selected_category == "전체":
    filtered_spots = spots
else:
    filtered_spots = [spot for spot in spots if selected_category in spot["category"]]

# 레이아웃 구성 (지도 + 핵심 통계 위젯)
col_map, col_stat = st.col([3, 1])

with col_stat:
    st.markdown("### 📊 정보 요약")
    st.metric(label="총 추천 명소", value=f"{len(spots)}개소")
    st.metric(label="선택된 카테고리", value=selected_category)
    st.info("💡 팁: 지도 위의 마커를 클릭하면 상세 이름과 유형이 팝업으로 나타납니다.")

with col_map:
    # 1. 포커스된 지도 생성
    m = folium.Map(location=[37.5550, 126.9800], zoom_start=12, tiles="CartoDB positron") # 세련된 모던 지도 테마 적용

    # 마커 동적 추가
    for i, spot in enumerate(spots, start=1):
        # 사이드바 필터에 맞는 마커 강조 또는 전체 표시
        is_highlighted = (selected_category == "전체" or selected_category in spot["category"])
        
        popup_text = f"<b>#{i} {spot['name']}</b><br>유형: {spot['category']}"
        folium.Marker(
            location=[spot["lat"], spot["lng"]],
            popup=folium.Popup(popup_text, max_width=250),
            tooltip=f"#{i} {spot['name']}",
            icon=folium.Icon(
                color="orange" if is_highlighted else "lightgray", 
                icon="star" if i <= 3 else "info-sign",
                prefix="fa"
            )
        ).add_to(m)

    # 지도를 화면에 출력
    st_folium(m, width="100%", height=480, use_container_width=True)

st.markdown("---")

# 2. 하단 관광지 카드형 상세 설명 렌더링
st.markdown("### 🌟 주요 관광지 10선 상세 가이드")
st.write("")

# 2열 그리드로 화사한 카드 나열
col1, col2 = st.columns(2)

for i, spot in enumerate(spots, start=1):
    target_col = col1 if i % 2 != 0 else col2
    with target_col:
        st.markdown(f"""
            <div class="spot-card">
                <h4>#{i}. {spot['name']}</h4>
                <p><b>🏷️ 카테고리:</b> <span style="color: #FF4B4B;">{spot['category']}</span></p>
                <p style="color: #666666; font-size: 0.95rem;">{spot['desc']}</p>
            </div>
        """, unsafe_allow_html=True)
