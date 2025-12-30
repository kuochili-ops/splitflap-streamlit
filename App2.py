import streamlit as st
import json
import feedparser
from flip_board_2 import render_flip_board

# --- 1. 頁面配置 ---
st.set_page_config(
    page_title="𓃥白六新聞/訊息告示牌", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 隱藏預設元件並設定懸浮面板 CSS
st.markdown("""
    <style>
    header, [data-testid="stHeader"], footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important;}
    
    /* 懸浮面板隱藏邏輯 */
    .floating-console {
        position: fixed;
        bottom: -280px; 
        left: 50%;
        transform: translateX(-50%);
        width: 95%;
        max-width: 800px;
        background: rgba(30, 30, 30, 0.95);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 20px 20px 0 0;
        z-index: 10000;
        transition: bottom 0.5s ease-in-out;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .floating-console:hover { bottom: 0; }
    
    /* 觸發感應區 */
    .trigger-zone {
        position: fixed;
        bottom: 0;
        width: 100%;
        height: 30px;
        background: transparent;
        z-index: 9999;
    }
    .trigger-zone:hover + .floating-console { bottom: 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心功能函式 ---
def get_news_data():
    try:
        feed = feedparser.parse("https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant")
        return [entry.title.split(' - ')[0] for entry in feed.entries[:10]]
    except Exception:
        return ["新聞系統連接中...", "請稍候再試"]

# --- 3. 懸浮面板 (原本的 Sidebar 內容) ---
st.markdown('<div class="trigger-zone"></div>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="floating-console">', unsafe_allow_html=True)
    st.subheader("⚙️ 告示牌設定")
    
    col1, col2 = st.columns(2)
    with col1:
        mode = st.radio("選擇播放模式", ["即時新聞模式", "手動輸入模式"], horizontal=True)
    with col2:
        stay_sec = st.slider("資訊停留秒數", 3.0, 15.0, 7.0)

    if mode == "手動輸入模式":
        user_text = st.text_area("自訂訊息 (每行一則)", "歡迎使用本系統\n祝您有美好的一天", height=100)
        raw_list = user_text.split('\n')
    else:
        if st.button("🔄 刷新即時新聞"):
            st.cache_data.clear()
        raw_list = get_news_data()
    
    if st.button("🚀 應用設定並隱藏"):
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. 資料預處理 ---
processed_list = ["白六新聞/訊息告示牌"]
for item in raw_list:
    clean_item = str(item).strip().upper().replace("'", "’")
    if clean_item:
        processed_list.append(clean_item)

# --- 5. 渲染畫面 ---
st.markdown("<h2 style='text-align: center; color: #555; font-family: Microsoft JhengHei; margin-top:20px;'>𓃥 白六新聞 / 訊息告示牌</h2>", unsafe_allow_html=True)

render_flip_board(json.dumps(processed_list), stay_sec=stay_sec)

st.markdown(f"<p style='text-align: center; color: #888;'>當前模式: {mode} | 共 {len(processed_list)-1} 則</p>", unsafe_allow_html=True)
