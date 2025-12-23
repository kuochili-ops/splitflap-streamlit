import streamlit as st
from flip_board import render_flip_board

st.set_page_config(layout="wide", page_title="Split-Flap System")

# 隱藏 Streamlit 多餘的邊距
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .block-container {padding: 0 !important;}
</style>
""", unsafe_allow_html=True)

# 管理訊息狀態
if "msg" not in st.session_state:
    st.session_state.msg = st.query_params.get("text", "STAY HUNGRY")

# 渲染妳完美的看板
render_flip_board(text=st.session_state.msg, stay_sec=4.0)

# 控制區
with st.container():
    st.write("---")
    col1, col2 = st.columns([4, 1])
    with col1:
        new_msg = st.text_input("輸入顯示訊息", value=st.session_state.msg, label_visibility="collapsed")
    with col2:
        if st.button("更新看板", use_container_width=True):
            st.session_state.msg = new_msg
            st.query_params["text"] = new_msg
            st.rerun()
