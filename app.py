import streamlit as st
import time
from flip_board import render_flip_board

st.set_page_config(layout="wide", page_title="Industrial Terminal")

# 清理參數
def get_safe_param(key, default):
    val = st.query_params.get(key, default)
    return str(val[0] if isinstance(val, list) else val)

t = get_safe_param("text", "SYSTEM ONLINE")
try:
    s = float(get_safe_param("stay", "4.0"))
except:
    s = 4.0

# 隱藏 UI 雜訊
st.markdown("<style>header, footer {visibility: hidden;} .block-container {padding:0; background:#1a1a1a;}</style>", unsafe_allow_html=True)

# 顯示看板
render_flip_board(text=t, stay_sec=s)

# 控制台 (位於底部)
with st.expander("⚙️ 控制面板", expanded=False):
    c1, c2 = st.columns([3, 1])
    with c1:
        new_t = st.text_input("看板訊息", value=t)
    with c2:
        new_s = st.number_input("停留秒數", 2.0, 10.0, s)
    if st.button("更新看板", use_container_width=True):
        st.query_params["text"] = new_t
        st.query_params["stay"] = str(new_s)
        st.rerun()
