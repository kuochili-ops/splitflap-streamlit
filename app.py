import streamlit as st
from flip_board import render_flip_board

st.set_page_config(layout="wide", page_title="Split-Flap Terminal")

# 1. 取得參數
if "display_text" not in st.session_state:
    st.session_state.display_text = st.query_params.get("text", "KEEP GOING")

# 2. 顯示看板 (這次包含了動畫功能)
st.markdown("<h2 style='text-align: center; color: #555;'>SPLIT-FLAP TERMINAL</h2>", unsafe_allow_html=True)
render_flip_board(text=st.session_state.display_text, stay_sec=4.0)

# 3. 控制面板
st.write("---")
with st.container():
    new_text = st.text_input("輸入顯示內容 (Enter 更新)", value=st.session_state.display_text)
    if st.button("🚀 更新看板內容", use_container_width=True):
        st.session_state.display_text = new_text
        st.query_params["text"] = new_text
        st.rerun()
