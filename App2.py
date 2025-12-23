import streamlit as st
import feedparser
import re
import json
from flip_board_2 import render_flip_board

# 設定頁面：手機友善佈局
st.set_page_config(page_title="CNA News Flip Clock", layout="centered")

# 隱藏預設介面與調整頂部間距
st.markdown("""
    <style>
    .stApp { margin-top: -60px; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def get_cna_news_list():
    """抓取中央社最新 10 則新聞標題"""
    rss_url = "https://feeds.feedburner.com/cnaFirstNews"
    try:
        feed = feedparser.parse(rss_url)
        titles = []
        for entry in feed.entries[:10]:
            # 過濾標題：僅留中英數，轉大寫
            clean_title = re.sub(r'[^\u4e00-\u9fa5A-Z0-9\s]', '', entry.title).upper()
            titles.append(clean_title)
        return titles if titles else ["WAITING FOR NEWS"]
    except:
        return ["NEWS CONNECTION ERROR"]

# --- 頂部控制面板 ---
with st.expander("⚙️ 點擊設定顯示內容", expanded=False):
    mode = st.radio("模式選擇", ["中央社即時新聞", "自定義訊息"], horizontal=True)
    
    if mode == "中央社即時新聞":
        @st.cache_data(ttl=300) # 5分鐘更新一次新聞
        def fetch_news():
            return get_cna_news_list()
        
        news_list = fetch_news()
        display_content = json.dumps(news_list) 
        st.caption(f"📢 已載入 {len(news_list)} 則即時新聞輪播中")
        if st.button("🔄 立即更新新聞"):
            st.cache_data.clear()
            st.rerun()
    else:
        user_input = st.text_input("輸入自定義訊息", "HELLO TAIWAN")
        display_content = json.dumps([user_input])

# 呼叫翻板組件 (stay_sec 設為 7秒 以利閱讀新聞)
render_flip_board(display_content, stay_sec=7.0)
