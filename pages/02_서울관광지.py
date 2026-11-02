import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. 페이지 설정
st.set_page_config(
    page_title="서울 관광지 TOP 10",
    page_icon="🏙️",
    layout="wide"
)

# 2. 타이틀 & 헤더
st.title("🏙️ 외국인이 선호하는 서울 주요 관광지 TOP 10")
st.caption("서울의 대표 명소 10곳을 지도 위 마커와 카드형 설명으로 확인하세요.")
st.markdown("---")

# 3. 데이터 정의
spots = [
    {"rank": 1, "name": "경복궁", "category": "역사 / 문화", "lat": 37.5796, "lng": 126.9770, "desc": "조선 왕조의 대표적인 법궁으로, 한복을 입고 관람하는 외국인 관광객들에게 필수 코스입니다."},
    {"rank": 2, "name": "N서울타워 (남산타워)", "category": "랜드마크 / 야경", "lat": 37.5512, "lng": 126.9882, "desc": "서울 시내를 360도로 조망할 수 있는 랜드마크로, 사랑의 자물쇠와 아름다운 야경으로 유명합니다."},
    {"rank": 3, "name": "북촌한옥마을", "category": "전통 / 거리", "lat": 37.5826, "lng": 126.9837, "desc": "고즈넉한 기와지붕 아래 한옥 감성과 현대적 분위기가 공존하는 전통 주거지입니다."},
    {"rank": 4, "name": "명동 쇼핑거리", "category": "쇼핑 / 길거리 음식", "lat": 37.5636, "lng": 126.9822, "desc": "K-뷰티 쇼핑과 다양한 길거리 음식을 한곳에서 즐길 수 있는 글로벌 대표 핫플레이스입니다."},
    {"rank": 5, "name": "동대문 디자인 플라자 (DDP)", "category": "건축 / 쇼핑", "lat": 37.5665, "lng": 127.0090, "desc": "곡선미가 돋보이는 곡면 디자인 건축물로 패션, 디자인 전시 및 화려한 야경을 선사합니다."},
    {"rank": 6, "name": "인사동 쌈지길", "category": "전통 / 공예", "lat": 37.5743, "lng": 126.9849, "desc": "한국의 전통 공예품, 찻집, 갤러리가 밀집해 있어 한국 문화의 맛과 멋을 느끼기 좋습니다."},
    {"rank": 7, "name": "홍대 거리", "category": "젊음 / K-POP / 버스킹", "lat": 37.5563, "lng": 126.9226, "desc": "스트리트 패션, 인디 음악 버스킹, 이색 카페 등 한국 청년 문화의 중심지입니다."},
    {"rank": 8, "name": "롯데월드타워 & 석촌호수", "category": "쇼핑 / 전망대", "lat": 37.5126, "lng": 127.1025, "desc": "123층 높이의 전망대 서울스카이와 대형 쇼핑몰, 석촌호수의 산책로가 어우러진 종합 랜드마크입니다."},
    {"rank": 9, "name": "국립중앙박물관", "category": "역사 / 박물관", "lat": 37.5240, "lng": 126.9804, "desc": "대한민국의 방대한 역사 유물과 문화를 한눈에 감상할 수 있는 세계적인 규모의 박물관입니다."},
    {"rank": 10, "name": "반포 한강공원 (무지개분수)", "category": "자연 / 휴식", "lat": 37.5102, "lng": 126.9960, "desc": "달빛무지개분수 쇼와 한강 라면 경험 등 서울 도심 속 강변 휴식을 즐기기 좋은 곳입니다."}
]

# 4. 지도 렌더링
m = folium.Map(location=[37.5550, 126.9800], zoom_start=11)

for spot in spots:
    popup_html = f"<b>#{spot['rank']} {spot['name']}</b><br>{spot['category']}"
    folium.Marker(
        location=[spot["lat"], spot["lng"]],
        popup=folium.Popup(popup_html, max_width=200),
        tooltip=f"#{spot['rank']} {spot['name']}",
        icon=folium.Icon(color="red" if spot["rank"] <= 3 else "blue", icon="info-sign")
    ).add_to(m)

# 지도 출력
st_folium(m, width="100%", height=500)

st.markdown("---")

# 5. 하단 관광지 안내 카드
st.subheader("📌 상세 관광지 정보")

col1, col2 = st.columns(2)

for spot in spots:
    target_col = col1 if spot["rank"] % 2 != 0 else col2
    with target_col:
        with st.container(border=True):
            st.markdown(f"### #{spot['rank']}. {spot['name']}")
            st.caption(f"🏷️ 카테고리: {spot['category']}")
            st.write(spot['desc'])
