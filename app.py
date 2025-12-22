import streamlit as st
from urllib.parse import urlencode
from flip_board import render_flip_board

# --- 基礎 UI 設定 ---
st.set_page_config(layout="wide", page_title="Banksy Terminal V12")

st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: #1a1a1a !important;}
    
    /* 面板初始隱藏在下方 */
    .floating-console {
        position: fixed;
        bottom: -220px; 
        left: 50%;
        transform: translateX(-50%);
        width: 95%;
        max-width: 800px;
        background: rgba(30, 30, 30, 0.95);
        backdrop-filter: blur(15px);
        padding: 15px;
        border-radius: 20px 20px 0 0;
        z-index: 1000;
        transition: bottom 0.4s ease-out;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* 觸碰感應區或面板本身時彈出 */
    .floating-console:hover, .floating-console:active {
        bottom: 0px;
    }
    
    /* 感應底條 */
    .trigger-bar {
        position: fixed;
        bottom: 0;
        width: 100%;
        height: 20px;
        background: transparent;
        z-index: 999;
    }
    .trigger-bar:hover + .floating-console {
        bottom: 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 參數處理 ---
qp = st.query_params
init_text = qp.get("text", "EVERYTHING IS FINE")
init_stay = float(qp.get("stay", 4.0))

# --- 感應面板 UI ---
st.markdown('<div class="trigger-bar"></div>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="floating-console">', unsafe_allow_html=True)
    
    c1, c2 = st.columns([3, 1])
    with c1:
        new_text = st.text_input("Message", value=init_text, label_visibility="collapsed")
    with c2:
        new_stay = st.number_input("Stay", 2.0, 10.0, init_stay, 0.5, label_visibility="collapsed")
    
    link = f"https://share.streamlit.io/your-app?{urlencode({'text': new_text, 'stay': new_stay})}"
    sc1, sc2 = st.columns([3, 1])
    with sc1:
        st.code(link, wrap_lines=False)
    with sc2:
        if st.button("🚀 UPDATE", use_container_width=True):
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

# --- 呼叫模組渲染翻牌 ---
render_flip_board(text=new_text, stay_sec=new_stay)
