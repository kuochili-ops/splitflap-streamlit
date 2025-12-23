import streamlit as st
import time
from flip_board import render_flip_board

st.set_page_config(layout="wide", page_title="Split Flap")

def get_clean_param(key, default):
    try:
        val = st.query_params.get(key, default)
        return str(val[0]) if isinstance(val, list) else str(val)
    except:
        return str(default)

text_param = get_clean_param("text", "STAY HUNGRY")
try:
    stay_param = float(get_clean_param("stay", "4.0"))
except:
    stay_param = 4.0

st.markdown("""<style>
    header, footer {visibility: hidden;}
    .block-container {padding: 0 !important; background: #1a1a1a;}
    .console {
        position: fixed; bottom: -280px; left: 50%; transform: translateX(-50%);
        width: 100%; max-width: 800px; background: rgba(30,30,30,0.9);
        padding: 25px; border-radius: 20px 20px 0 0; transition: 0.5s;
        border: 1px solid rgba(255,255,255,0.1); z-index: 100;
    }
    .console:hover, .console:focus-within { bottom: 0; }
</style>""", unsafe_allow_html=True)

render_flip_board(text=text_param, stay_sec=stay_param)

with st.container():
    st.markdown('<div class="console">', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1:
        nt = st.text_input("看板訊息", value=text_param)
    with c2:
        ns = st.number_input("停留秒數", 2.0, 10.0, stay_param)
    if st.button("🚀 更新"):
        st.query_params["text"] = nt
        st.query_params["stay"] = str(ns)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
