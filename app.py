# 진입점 entry point
import streamlit as st

# Page
# home = st.Page('home.py', title='홈', icon="❤")
# dashboard = st.Page('dashboard.py', title='대시보드')

# #Navigation
# page = st.navigation([home, dashboard])
# page.run()

overview = st.Page("home.py", title="요약",     icon="📊")
detail   = st.Page("session1,2.py",   title="상세 분석", icon="🔍")
setting = st.Page("session3.py", title="⚙")

pg = st.navigation({"분석": [overview, detail], "설정": [setting]})
pg.run()