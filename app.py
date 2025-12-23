import streamlit as st
from flip_board import render_flip_board

st.set_page_config(layout="wide", page_title="Split-Flap Stable")

# 簡單的參數管理
if "display_text" not in st.session_state:
    st.session_state.display_text = st.query_params.get("text", "STABLE VERSION")

st.markdown("<h2 style='text-align: center; color: #666;'>SPLIT-FLAP SYSTEM</h2>", unsafe_allow_html=True)

# 渲染看板
render_flip_board(st.session_state.display_text)

# 分隔線與輸入
st.write("---")
with st.container():
    new_text = st.text_input("輸入顯示內容", value=st.session_state.display_text)
    if st.button("更新看板", use_container_width=True):
        st.session_state.display_text = new_text
        st.query_params["text"] = new_text
        st.rerun()
