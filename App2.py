import streamlit as st
import feedparser
import re
import json
import time
import datetime
from flip_board_2 import render_flip_board

# 設定頁面
st.set_page_config(page_title="Multi-Source Flip Clock", layout="centered")

# 隱藏界面與優化手機間距
st.markdown("""<style>.stApp { margin-top: -60px; } #MainMenu, footer, header {visibility: hidden;}</style>""", unsafe_allow_html=True)

# 擴充後的新聞來源字典
NEWS_SOURCES = {
    "中央社-即時": "https://feeds.feedburner.com/cnaFirstNews",
    "中央社-產經": "https://feeds.feedburner.com/cnaBusiness",
    "中央社-國際": "https://feeds.feedburner.com/cnaIntl",
    "中央社-社會": "https://feeds.feedburner.com/cnaSocial",
    "中央社-政治": "https://feeds.feedburner.com/cnaPolitics",
    "公視新聞-要聞": "https://news.pts.org.tw/xml/newsfeed.xml",
    "科技新報-所有資訊": "https://technews.tw/feed/",
}

def get_combined_news(selected_sources):
    """抓取多個來源的新聞並合併"""
    all_titles = []
    if not selected_sources:
        return ["請選擇新聞來源"]

    for name in selected_sources:
        # 在 URL 後面加上時間標記，繞過伺服器快取，確保抓到最新新聞
        base_url = NEWS_SOURCES[name]
        url = f"{base_url}?t={int(time.time())}"
        
        try:
            time.sleep(0.3)
            feed = feedparser.parse(url)
            if not feed.entries:
                continue
                
            source_tag = name.split('-')[1]
            count = 0
            for entry in feed.entries:
                if count >= 5: break
                clean_title = re.sub(r'<[^>]+>', '', entry.title)
                clean_title = re.sub(r'[^\u4e00-\u9fa5A-Z0-9\s]', '', clean_title).upper()
                if clean_title.strip():
                    all_titles.append(f"[{source_tag}] {clean_title}")
                    count += 1
        except:
            continue
            
    return all_titles if all_titles else ["暫無新聞資料，請嘗試刷新"]

# --- 快取邏輯 ---
@st.cache_data(ttl=300) # 5 分鐘快取
def fetch_multi_news(sources_tuple):
    return get_combined_news(list(sources_tuple))

# --- 頂部控制面板 ---
with st.expander("⚙️ 設定顯示內容", expanded=False):
    mode = st.radio("模式選擇", ["新聞輪播", "自定義訊息"], horizontal=True)
    
    if mode == "新聞輪播":
        selected = st.multiselect(
            "選擇新聞頻道 (可複選)", 
            options=list(NEWS_SOURCES.keys()),
            default=["中央社-即時"]
        )
        
        # 執行抓取
        news_list = fetch_multi_news(tuple(selected))
        display_content = json.dumps(news_list)
        
        st.success(f"📋 已載入 {len(news_list)} 則新聞")
        
        if st.button("🔥 徹底清除快取並更新最新新聞"):
            st.cache_data.clear()
            st.rerun()
    else:
        user_input = st.text_input("輸入自定義訊息 (小於16字自動調整翻板)", "HAPPY NEW YEAR")
        display_content = json.dumps([user_input])

# 渲染翻板
render_flip_board(display_content, stay_sec=8.0)
