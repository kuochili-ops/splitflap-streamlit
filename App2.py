import streamlit as st
import json
import feedparser
from flip_board_2 import render_flip_board

# --- 1. 頁面配置 ---
st.set_page_config(page_title="𓃥白六新聞/訊息告示牌", layout="wide", initial_sidebar_state="collapsed")

# 隱藏預設元件並設定底部懸浮面板 CSS
st.markdown("""
    <style>
    header, [data-testid="stHeader"], footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; margin: 0 !important;}
    .stApp {background-color: #f0f2f6;}

    /* 懸浮控制面板：位於翻板下方 */
    .floating-console {
        position: fixed;
        bottom: -320px; 
        left: 50%;
        transform: translateX(-50%);
        width: 95%;
        max-width: 800px;
        background: rgba(30, 30, 30, 0.98);
        backdrop-filter: blur(15px);
        padding: 20px;
        border-radius: 20px 20px 0 0;
        z-index: 10000;
        transition: bottom 0.5s cubic-bezier(0.165, 0.84, 0.44, 1);
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 -10px 30px rgba(0,0,0,0.5);
    }
    
    /* 觸發機制 */
    .floating-console:hover, .floating-console:focus-within {
        bottom: 0px !important;
    }
    
    /* 感應區 */
    .trigger-pad {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 40px;
        background: transparent;
        z-index: 9999;
    }
    .trigger-pad:hover + .floating-console {
        bottom: 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心功能 ---
def get_news_data():
    try:
        feed = feedparser.parse("https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant")
        return [entry.title.split(' - ')[0] for entry in feed.entries[:10]]
    except:
        return ["新聞抓取中...", "請稍候"]

# --- 3. 懸浮面板 UI ---
st.markdown('<div class="trigger-pad"></div>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="floating-console">', unsafe_allow_html=True)
    st.markdown("<h4 style='color:white; margin-top:0;'>⚙️ 告示牌設定</h4>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([2, 1])
    with c1:
        mode = st.radio("模式", ["即時新聞模式", "手動輸入模式"], horizontal=True)
    with c2:
        stay_sec = st.slider("停留秒數", 3.0, 15.0, 7.0)

    if mode == "手動輸入模式":
        user_text = st.text_area("自訂訊息 (每行一則)", "歡迎使用本系統\n白六 NEWS", height=80)
        raw_list = user_text.split('\n')
    else:
        raw_list = get_news_data()
        if st.button("🔄 刷新新聞"):
            st.cache_data.clear()
    
    if st.button("🚀 套用並播放", use_container_width=True):
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. 數據處理 ---
processed_list = ["白六新聞/訊息告示牌"]
for item in raw_list:
    clean = str(item).strip().upper().replace("'", "’")
    if clean: processed_list.append(clean)

# --- 5. 渲染顯示 ---
st.markdown("<h2 style='text-align: center; color: #444; font-family: Microsoft JhengHei; margin-top: 20px;'>𓃥 白六新聞 / 訊息告示牌</h2>", unsafe_allow_html=True)

render_flip_board(json.dumps(processed_list), stay_sec=stay_sec)

st.markdown(f"<p style='text-align: center; color: #999;'>{mode} | 總計 {len(processed_list)-1} 則輪播</p>", unsafe_allow_html=True)
