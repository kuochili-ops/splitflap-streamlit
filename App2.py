import streamlit as st
import feedparser
import re
import json
import time
from flip_board_2 import render_flip_board

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
    "科技新報-科技趨勢": "https://technews.tw/category/technews/feed/",
}

def get_combined_news(selected_sources):
    """抓取多個來源的新聞並合併"""
    all_titles = []
    
    if not selected_sources:
        return ["請選擇新聞來源"]

    for name in selected_sources:
        url = NEWS_SOURCES[name]
        try:
            # 為了避免被 RSS 伺服器封鎖，加入微小延遲
            time.sleep(0.3)
            feed = feedparser.parse(url)
            
            if not feed.entries:
                continue
                
            # 提取分類名稱，如 "產經" 或 "科技趨勢"
            source_tag = name.split('-')[1]
            
            # 每個來源抓取最新 5 則標題
            count = 0
            for entry in feed.entries:
                if count >= 5: break
                
                # 清洗標題：移除 HTML 標籤、特殊符號，只留中英數
                title_text = entry.title
                clean_title = re.sub(r'<[^>]+>', '', title_text) # 移除 HTML
                clean_title = re.sub(r'[^\u4e00-\u9fa5A-Z0-9\s]', '', clean_title).upper()
                
                if clean_title.strip():
                    all_titles.append(f"[{source_tag}] {clean_title}")
                    count += 1
        except Exception as e:
            # 發生錯誤時跳過該來源
            continue
            
    return all_titles if all_titles else ["暫無新聞資料，請嘗試刷新"]

# --- 頂部控制面板 ---
with st.expander("⚙️ 設定顯示內容", expanded=False):
    mode = st.radio("模式選擇", ["新聞輪播", "自定義訊息"], horizontal=True)
    
    if mode == "新聞輪播":
        selected = st.multiselect(
            "選擇新聞頻道 (可複選)", 
            options=list(NEWS_SOURCES.keys()),
            default=["中央社-即時", "科技新報-科技趨勢"]
        )
        
        # 使用 cache 提升效能，10 分鐘更新一次
        @st.cache_data(ttl=600)
        def fetch_multi_news(sources_tuple):
            return get_combined_news(list(sources_tuple))
        
        # 執行抓取 (轉成 tuple 才能作為 cache key)
        news_list = fetch_multi_news(tuple(selected))
        display_content = json.dumps(news_list)
        
        st.success(f"📋 已載入 {len(news_list)} 則新聞，來自 {len(selected)} 個頻道")
        
        if st.button("🔄 立即更新所有新聞"):
            st.cache_data.clear()
            st.rerun()
    else:
        user_input = st.text_input("輸入自定義訊息", "HELLO TAIWAN")
        display_content = json.dumps([user_input])

# 渲染翻板
render_flip_board(display_content, stay_sec=8.0)
