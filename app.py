import streamlit as st
from urllib.parse import urlencode
from flip_board import render_flip_board

# --- 1. 徹底清除 Streamlit 預設介面遮擋 ---
st.set_page_config(layout="wide", page_title="Banksy Terminal V12")

st.markdown("""
    <style>
    /* 徹底隱藏 Header 與原生按鈕 */
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; margin: 0 !important; background-color: #1a1a1a !important;}
    .stApp {background-color: #1a1a1a !important;}

    /* 設定控制面板：平常隱藏在螢幕下方 300px 處 */
    .floating-console {
        position: fixed;
        bottom: -300px; 
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        max-width: 850px;
        background: rgba(25, 25, 25, 0.98);
        backdrop-filter: blur(20px);
        padding: 20px;
        border-radius: 25px 25px 0 0;
        z-index: 10000;
        transition: bottom 0.5s cubic-bezier(0.165, 0.84, 0.44, 1);
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 -15px 50px rgba(0,0,0,0.8);
    }
    
    /* 觸碰感應機制：當面板被 active 或點擊時彈出 */
    .floating-console:hover, .floating-console:active, .floating-console:focus-within {
        bottom: 0px !important;
    }
    
    /* 底部透明觸發感應區 */
    .trigger-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 40px;
        background: transparent;
        z-index: 9999;
    }
    .trigger-bar:hover + .floating-console {
        bottom: 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 參數處理 ---
qp = st.query_params
init_text = qp.get("text", "KEEP GOING 2025")
init_stay = float(qp.get("stay", 4.0))

# --- 3. 呼叫翻牌看板 (作為底層背景) ---
render_flip_board(text=init_text, stay_sec=init_stay)

# --- 4. 渲染感應面板 (懸浮層) ---
st.markdown('<div class="trigger-bar"></div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="floating-console">', unsafe_allow_html=True)
    
    # 第一排：訊息內容與時間設定
    c1, c2 = st.columns([3, 1])
    with c1:
        new_text = st.text_input("看板訊息", value=init_text, label_visibility="collapsed", placeholder="輸入英文或數字...")
    with c2:
        new_stay = st.number_input("停留(秒)", 2.0, 10.0, init_stay, 0.5, label_visibility="collapsed")
    
    # 第二排：動態分享連結生成
    # 這裡已自動帶入您的真實網址
    current_url = "https://6vcj29fwzgpbmtkyn7er8g.streamlit.app"
    share_link = f"{current_url}?{urlencode({'text': new_text, 'stay': new_stay})}"
    
    sc1, sc2 = st.columns([3, 1])
    with sc1:
        st.code(share_link, wrap_lines=False)
    with sc2:
        if st.button("🚀 更新播放", use_container_width=True):
            # 更新參數並自動收起面板
            st.query_params.update({"text": new_text, "stay": new_stay})
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)
