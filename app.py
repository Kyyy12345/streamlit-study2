import streamlit as st

# 1. State 초기화
if 'c' not in st.session_state:
    st.session_state.c = 0
if 'l' not in st.session_state:
    st.session_state.l = False

# 2. 콜백 함수 정의 
def increase_counter():
    st.session_state.c += 1

def reset_counter():
    st.session_state.c = 0

def toggle_like():
    st.session_state.l = not st.session_state.l

# 3. 레이아웃 및 버튼 배치 (on_click 연결)
col1, col2 = st.columns([3, 1])
with col1:
    st.button("클릭", on_click=increase_counter)
with col2:
    st.button("초기화", on_click=reset_counter)

# 4. 데이터 표시
st.write("클릭 수:", st.session_state.c)

# 5. 좋아요 토글 버튼 및 상태 표시
label = "❤️ 좋아요 취소" if st.session_state.l else "🤍 좋아요"
st.button(label, on_click=toggle_like)

if st.session_state.l:
    st.success("좋아요를 눌렀습니다!")

# 위젯의 매개변수로 key를 지정할 경우
# session_state의 key로 자동 저장
# 초기화 가드 대신 최초 실행시 value값을 초기값으로 사용
# 데이터 변경시 -> rerun -> 마지막 session_state값으로 불러옴
age_range = st.slider("나이 범위", 0, 80, (0, 80), key='age_range')

# 읽기
st.write("현재 선택 값: ", st.session_state["age_range"])