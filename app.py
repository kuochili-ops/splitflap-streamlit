import streamlit as st
from urllib.parse import urlencode
from flip_board import render_flip_board

# --- 1. 頁面配置與隱藏 Streamlit 原生介面 ---
st.set_page_config(layout="wide", page_title="Banksy Terminal V12")

st.markdown("""
    <style>
    /* 徹底隱藏 Header 與原生按鈕，讓背景純淨 */
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; margin: 0 !important; background-color: #1a1a1a !important;}
    .stApp {background-color: #1a1a1a !important;}

    /* 設定控制面板：平常隱藏在螢幕下方 */
    .floating-console {
        position: fixed;
        bottom: -300px; 
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        max-width: 850px;
        background: rgba(25, 25, 25, 0.95);
        backdrop-filter: blur(25px);
        padding: 25px;
        border-radius: 25px 25px 0 0;
        z-index: 10000;
        transition: bottom 0.6s cubic-bezier(0.165, 0.84, 0.44, 1);
        border: 1px solid rgba(255,255,255,0.15);
        box-shadow: 0 -20px 60px rgba(0,0,0,0.9);
    }
    
    /* 觸碰感應機制：滑鼠移入或焦點在輸入框時彈出 */
    .floating-console:hover, .floating-console:active, .floating-console:focus-within {
        bottom: 0px !important;
    }
    
    /* 底部透明觸發感應區 */
    .trigger-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 50px;
        background: transparent;
        z-index: 9999;
    }
    .trigger-bar:hover + .floating-console {
        bottom: 0px;
    }

    /* 調整 Streamlit 元件在深色背景下的顯示 */
    .stTextInput input, .stNumberInput input {
        background-color: rgba(255,255,255,0.05) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 參數處理：優先讀取 URL 參數，否則使用預設值 ---
qp = st.query_params
# 處理 text 參數，確保即使為空也有預設值
init_text = qp.get("text", "KEEP GOING 2025")
# 處理 stay 參數，確保轉為 float 且處理異常值
try:
    init_stay = float(qp.get("stay", 4.0))
except ValueError:
    init_stay = 4.0

# --- 3. 呼叫翻牌看板 (作為底層全螢幕背景) ---
# 這裡會根據傳入的文字與時間渲染最新的 HTML 內容
render_flip_board(text=init_text, stay_sec=init_stay)

# --- 4. 渲染感應控制面板 (懸浮層) ---
st.markdown('<div class="trigger-bar"></div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="floating-console">', unsafe_allow_html=True)
    
    # 第一排：訊息內容與切換速度設定
    c1, c2 = st.columns([3, 1])
    with c1:
        new_text = st.text_input("看板訊息", value=init_text, placeholder="輸入英文、數字或中文...", key="input_text")
    with c2:
        new_stay = st.number_input("停留(秒)", 2.0, 20.0, init_stay, 0.5, key="input_stay")
    
    # 第二排：分享連結顯示與更新按鈕
    # 自動偵測目前的 URL 基礎位址
    current_url = "https://6vcj29fwzgpbmtkyn7er8g.streamlit.app"
    share_link = f"{current_url}?{urlencode({'text': new_text, 'stay': new_stay})}"
    
    sc1, sc2 = st.columns([3, 1])
    with sc1:
        st.caption("🔗 專屬分享連結：")
        st.code(share_link, wrap_lines=False)
    with sc2:
        st.markdown("<br>", unsafe_allow_html=True) # 微調按鈕對齊
        if st.button("🚀 更新播放", use_container_width=True, type="primary"):
            # 1. 更新 URL 參數
            st.query_params.update({"text": new_text, "stay": new_stay})
            # 2. 強制頁面重整以觸發 render_flip_board 重新繪製
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)
