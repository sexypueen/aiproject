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
    /* 전체 배경: 은은한 핑크 파스텔 그라데이션 */
    .stApp {
        background: linear-gradient(135deg, #fff0f3 0%, #ffccd5 100%);
        color: #4a1525;
    }
    
    /* 사이드바 배경: 고급스러운 로즈 핑크 그라데이션 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #d81b60 0%, #ad1457 100%);
        color: white;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }

    /* 메인 타이틀 핑크 그라데이션 */
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ad1457, #ff4081);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }

    /* 글래스모피즘 반투명 핑크 카드 UI */
    .custom-card {
        background: rgba(255, 255, 255, 0.85);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(216, 27, 96, 0.15);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 182,
