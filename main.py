import streamlit as st
st.title('나의 첫 웹사이트 만들기')
a=st.text_input('이름을 입력해주세요')
b=st.selectbox('좋아하는 음식을 선택하세요',['돈까스','짜장면','햄버거'])
if st.button('인사말 생성'):
  st.write('반갑습니다!')
  st.info(a+'님 안녕하세뇨')
  st.warning(b+'같은걸 먹고다니니까 살이 찌지')
  st.error('잘 부탁드립니다')
  st.balloons()
