import streamlit as st
import time
from flip_board import render_flip_board

st.set_page_config(layout="wide", page_title="Split-Flap Terminal")

# --- 參數清理函式 ---
def get_clean_param(key, default):
    val = st.query_params.get(key, default)
    # 如果是 list (Streamlit 偶爾會回傳 list)，取第一個值
    if isinstance(val, list):
        val = val[0] if val else default
    return str(val)

# 1. 讀取並清洗參數
raw_text = get_clean_param("text", "STAY HUNGRY")
try:
    raw_stay = float(get_clean_param("stay", "4.0"))
except:
    raw_stay = 4.0

# 2. 隱藏原生組件
st.markdown("""
    <style>
    header, [data-testid="stHeader"], footer {visibility: hidden;}
    .block-container {padding: 0 !important;}
    div[data-testid="stVerticalBlock"] > div:has(div.floating-console) {z-index: 999;}
    
    .floating-console {
        position: fixed; bottom: -280px; left: 50%; transform: translateX(-50%);
        width: 100%; max-width: 800px; background: rgba(30, 30, 30, 0.9);
        backdrop-filter: blur(20px); padding: 25px; border-radius: 20px 20px 0 0;
        transition: 0.5s; border: 1px solid rgba(255,255,255,0.1);
    }
    .floating-console:hover { bottom: 0px; }
    .trigger-bar { position: fixed; bottom: 0; width: 100%; height: 40px; }
    </style>
""", unsafe_allow_html=True)

# 3. 渲染背景看板 (傳入清洗過的參數)
render_flip_board(text=raw_text, stay_sec=raw_stay)

# 4. 控制面板
st.markdown('<div class="trigger-bar"></div>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="floating-console">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        new_text = st.text_input("看板訊息", value=raw_text)
    with col2:
        new_stay = st.number_input("停留(秒)", 2.0, 20.0, raw_stay)
    
    if st.button("🚀 更新播放", use_container_width=True, type="primary"):
        # 更新 URL 參數並觸發 rerun
        st.query_params["text"] = new_text
        st.query_params["stay"] = str(new_stay)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
