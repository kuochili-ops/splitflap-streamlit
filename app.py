import streamlit as st
import time
from flip_board import render_flip_board

st.set_page_config(layout="wide", page_title="Flip Board")

# 確保從 URL 拿到的參數是乾淨的字串
def get_p(key, d):
    try:
        res = st.query_params.get(key, d)
        return str(res[0]) if isinstance(res, list) else str(res)
    except:
        return str(d)

t = get_p("text", "WELCOME 2025")
try:
    s = float(get_p("stay", 4.0))
except:
    s = 4.0

# 樣式定義
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .block-container {padding: 0 !important; background: #1a1a1a;}
    .console {
        position: fixed; bottom: -280px; left: 50%; transform: translateX(-50%);
        width: 100%; max-width: 800px; background: rgba(30,30,30,0.95);
        padding: 25px; border-radius: 20px 20px 0 0; transition: 0.4s;
        border: 1px solid rgba(255,255,255,0.1); z-index: 100;
    }
    .console:hover, .console:focus-within { bottom: 0; }
</style>
""", unsafe_allow_html=True)

# 執行看板
render_flip_board(text=t, stay_sec=s)

# UI 控制
with st.container():
    st.markdown('<div class="console">', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1:
        nt = st.text_input("訊息", value=t)
    with c2:
        ns = st.number_input("停留", 2.0, 10.0, s)
    
    if st.button("更新", use_container_width=True):
        st.query_params["text"] = nt
        st.query_params["stay"] = str(ns)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
