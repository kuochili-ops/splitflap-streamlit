import streamlit as st
from flip_board import render_flip_board

st.set_page_config(layout="wide")

# 隱藏 Streamlit 預設樣式
st.markdown("<style>header, footer {visibility: hidden;} .block-container {padding:0;}</style>", unsafe_allow_html=True)

# 使用 Session State 鎖定資料
if "msg" not in st.session_state:
    st.session_state.msg = st.query_params.get("text", "KEEP GOING")

# 渲染看板
render_flip_board(text=st.session_state.msg, stay_sec=4.0)

# 控制面板放在底部 Expander
with st.expander("⚙️ 看板控制面板"):
    new_msg = st.text_input("輸入新訊息", value=st.session_state.msg)
    if st.button("更新看板內容"):
        st.session_state.msg = new_msg
        st.query_params["text"] = new_msg
        st.rerun()
