import streamlit as st
from flip_board import render_flip_board

st.set_page_config(layout="wide", page_title="Industrial Terminal")

# 初始化參數
if "display_text" not in st.session_state:
    st.session_state.display_text = st.query_params.get("text", "WELCOME")

# 頁面標題
st.markdown("<h1 style='text-align: center; color: #666;'>SPLIT-FLAP TERMINAL</h1>", unsafe_allow_html=True)

# 渲染看板 (放在上方)
render_flip_board(text=st.session_state.display_text)

st.write("---")

# 控制面板 (放在下方)
with st.container():
    st.write("### ⚙️ 控制中心")
    c1, c2 = st.columns([3, 1])
    
    with c1:
        new_text = st.text_input("輸入顯示訊息", value=st.session_state.display_text)
    
    with c2:
        if st.button("🚀 更新看板", use_container_width=True):
            st.session_state.display_text = new_text
            st.query_params["text"] = new_text
            st.rerun()

st.info("💡 提示：輸入文字後點擊更新，看板將會同步。")
