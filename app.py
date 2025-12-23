import streamlit as st
from urllib.parse import urlencode
from flip_board import render_flip_board

st.set_page_config(layout="wide", page_title="Banksy Terminal V12")

# --- 強化的參數讀取邏輯 ---
def get_param(key, default):
    val = st.query_params.get(key, default)
    # 如果回傳的是 list，取第一個元素
    if isinstance(val, list):
        return val[0] if val else default
    return val

# 讀取並確保型別正確
init_text = get_param("text", "KEEP GOING 2025")

try:
    init_stay = float(get_param("stay", 4.0))
except (ValueError, TypeError):
    init_stay = 4.0

# --- 隱藏樣式 (與之前相同) ---
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important;}
    .floating-console {
        position: fixed; bottom: -300px; left: 50%; transform: translateX(-50%);
        width: 100%; max-width: 850px; background: rgba(25, 25, 25, 0.9);
        backdrop-filter: blur(20px); padding: 20px; border-radius: 20px 20px 0 0;
        z-index: 10000; transition: bottom 0.5s; border: 1px solid rgba(255,255,255,0.1);
    }
    .floating-console:hover, .floating-console:focus-within { bottom: 0px !important; }
    .trigger-bar { position: fixed; bottom: 0; width: 100%; height: 40px; z-index: 9999; }
    </style>
""", unsafe_allow_html=True)

# 渲染翻牌看板
render_flip_board(text=init_text, stay_sec=init_stay)

# 懸浮控制面板
st.markdown('<div class="trigger-bar"></div>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="floating-console">', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1:
        new_text = st.text_input("看板訊息", value=init_text)
    with c2:
        new_stay = st.number_input("停留(秒)", 2.0, 20.0, init_stay)
    
    if st.button("🚀 更新播放", use_container_width=True, type="primary"):
        st.query_params.update({"text": new_text, "stay": new_stay})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
