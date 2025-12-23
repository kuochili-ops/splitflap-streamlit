import streamlit as st
import time
from flip_board import render_flip_board

st.set_page_config(layout="wide", page_title="Industrial Flip Board")

def get_p(key, d):
    try:
        res = st.query_params.get(key, d)
        # 確保回傳單一字串
        if isinstance(res, list):
            return str(res[0])
        return str(res)
    except:
        return str(d)

t = get_p("text", "KEEP PUSHING")
try:
    s = float(get_p("stay", 4.0))
except:
    s = 4.0

# 面板控制 UI 樣式
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .block-container {padding: 0 !important; background: #121212;}
    .console {
        position: fixed; bottom: -280px; left: 50%; transform: translateX(-50%);
        width: 100%; max-width: 800px; background: rgba(30,30,30,0.9);
        backdrop-filter: blur(20px); padding: 25px; border-radius: 20px 20px 0 0; 
        transition: 0.5s cubic-bezier(0.19, 1, 0.22, 1);
        border: 1px solid rgba(255,255,255,0.1); z-index: 100;
        box-shadow: 0 -10px 30px rgba(0,0,0,0.5);
    }
    .console:hover, .console:focus-within { bottom: 0; }
</style>
""", unsafe_allow_html=True)

render_flip_board(text=t, stay_sec=s)

with st.container():
    st.markdown('<div class="console">', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1:
        nt = st.text_input("輸入顯示訊息", value=t)
    with c2:
        ns = st.number_input("切換秒數", 2.0, 10.0, s, step=0.5)
    
    if st.button("🚀 立即更新", use_container_width=True):
        st.query_params["text"] = nt
        st.query_params["stay"] = str(ns)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
