import streamlit as st
import feedparser
import re
import json
import time
import datetime
import urllib.request
from flip_board_2 import render_flip_board

# 設定頁面
st.set_page_config(page_title="Multi-Source Flip Clock", layout="centered")

# 隱藏介面
st.markdown("""<style>.stApp { margin-top: -60px; } #MainMenu, footer, header {visibility: hidden;}</style>""", unsafe_allow_html=True)

# 1. 修正後的新聞來源字典 (公視網址已更新)
NEWS_SOURCES = {
    "中央社-即時": "https://feeds.feedburner.com/cnaFirstNews",
    "中央社-產經": "https://feeds.feedburner.com/cnaBusiness",
    "公視新聞-要聞": "https://news.pts.org.tw/rss/news.xml",
    "科技新報": "https://technews.tw/feed/",
}

def get_combined_news(selected_sources):
    all_titles = []
    if not selected_sources:
        return ["請選擇新聞來源"]

    headers = {'User-Agent': 'Mozilla/5.0'}

    for name in selected_sources:
        # 這裡會從 NEWS_SOURCES 字典根據名字抓取網址
        url = NEWS_SOURCES[name]
        
        # 加上時間戳記避免快取 (公視除外，避免 404)
        if "pts.org.tw" not in url:
            url += f"?t={int(time.time())}"
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                feed = feedparser.parse(response.read())
            
            source_tag = name.split('-')[1] if '-' in name else name
            count = 0
            for entry in feed.entries:
                if count >= 5: break
                # 移除 HTML 標籤並轉大寫
                clean_title = re.sub(r'<[^>]+>', '', entry.title)
                clean_title = re.sub(r'[^\u4e00-\u9fa5A-Z0-9\s]', '', clean_title).upper()
                if clean_title.strip():
                    all_titles.append(f"[{source_tag}] {clean_title}")
                    count += 1
        except:
            continue
            
    return all_titles if all_titles else ["暫無新聞資料，請嘗試刷新"]

# --- 快取邏輯 ---
@st.cache_data(ttl=300)
def fetch_multi_news(sources_tuple):
    return get_combined_news(list(sources_tuple))

# --- 控制面板 ---
with st.expander("⚙️ 設定顯示內容", expanded=False):
    mode = st.radio("模式選擇", ["新聞輪播", "自定義訊息"], horizontal=True)
    
    if mode == "新聞輪播":
        selected = st.multiselect("選擇頻道", options=list(NEWS_SOURCES.keys()), default=["中央社-即時"])
        news_list = fetch_multi_news(tuple(selected))
        display_content = news_list # 傳送 List
    else:
        user_input = st.text_input("輸入文字", "HAPPY NEW YEAR")
        display_content = [user_input]

if st.button("🔥 徹底清除快取並更新"):
    st.cache_data.clear()
    st.rerun()

# 2. 呼叫翻板 (stay_sec 控制切換速度)
render_flip_board(display_content, stay_sec=8.0)
