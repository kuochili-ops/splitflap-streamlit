import streamlit as st
import time
from flip_board import render_flip_board

st.set_page_config(layout="wide", page_title="Split-Flap Terminal")

# --- 強化參數清理 ---
def get_clean_param(key, default):
    try:
        val = st.query_params.get(key, default)
        if isinstance(val, list):
            return str(val[0])
        return str(val)
    except:
        return default

raw_text = get_clean_param("text", "STAY HUNGRY")
try:
    raw_stay = float(get_clean_param("stay", "4.0"))
except:
    raw_stay = 4.0

# 樣式隱藏
st.markdown("""
    <style>
    header, [data-testid="stHeader"], footer {visibility: hidden;}
    .block-container {padding: 0 !important; background: #1a1a1a;}
    .floating-console {
        position: fixed; bottom: -280px; left: 50%; transform: translateX(-50%);
        width: 100%; max-width: 800px; background: rgba(30, 30, 30, 0.95);
        backdrop-filter: blur(20px); padding: 25px; border-radius: 20px 20px 0 0;
        transition: 0.5s; border: 1px solid rgba(255,255,255,0.1); z-index: 1000;
    }
    .floating-console:hover, .floating-console:focus-within { bottom: 0px; }
    .trigger-bar { position: fixed; bottom: 0; width: 100%; height: 40px; z-index: 999; }
    </style>
""", unsafe_allow_html=True)

# 渲染看板
render_flip_board(text=raw_text, stay_sec=raw_stay)

# 控制層
st.markdown('<div class="trigger-bar"></div>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="floating-console">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        new_text = st.text_input("看板訊息", value=raw_text)
    with col2:
        new_stay = st.number_input("停留(秒)", 2.0, 20.0, raw_stay)
    
    if st.button("🚀 更新播放", use_container_width=True, type="primary"):
        st.query_params["text"] = new_text
        st.query_params["stay"] = str(new_stay)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
