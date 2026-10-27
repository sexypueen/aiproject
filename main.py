import streamlit as st
st.title('나의 첫 웹사이트 만들기')
st.text_input('이름을 입력해 주세요')
st.selectbox('좋아하는 음식을 선택하세요',['돈까스','짜장면','햄버거'])
st.button('인사말 생성')
