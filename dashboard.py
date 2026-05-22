import streamlit as st

name = st.session_state.get('user_name', '방문자')
st.subheader(f"{name}님의 대시보드")