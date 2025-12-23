import streamlit as st
import time
from flip_board import render_flip_board

st.set_page_config(layout="wide", page_title="Industrial Terminal")

# 安全讀取參數
def get_safe_param(key, default):
    try:
        val = st.query_params.get(key, default)
        return str(val[0] if isinstance(val, list) else val)
    except:
        return str(default)

text_p = get_safe_param("text", "STAY HUNGRY")
try:
    stay_p = float(get_safe_param("stay", "4.0"))
except:
    stay_p = 4.0

# 隱藏原生組件邊距
st.markdown("<style>header, footer {visibility: hidden;} .block-container {padding:0 !important; background:#1a1a1a;}</style>", unsafe_allow_html=True)

# 渲染看板
render_flip_board(text=text_p, stay_sec=stay_p)

# 控制台
with st.container():
    st.markdown('<div style="position:fixed; bottom:20px; left:50%; transform:translateX(-50%); width:80%; max-width:600px; background:rgba(50,50,50,0.8); padding:20px; border-radius:15px; backdrop-filter:blur(10px); border:1px solid #444; z-index:999;">', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1:
        new_t = st.text_input("訊息", value=text_p, label_visibility="collapsed")
    with c2:
        new_s = st.number_input("停留", 2.0, 10.0, stay_p, label_visibility="collapsed")
    
    if st.button("🚀 更新", use_container_width=True):
        st.query_params["text"] = new_t
        st.query_params["stay"] = str(new_s)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
