import streamlit as st
import feedparser
import re
import json
from flip_board_2 import render_flip_board

st.set_page_config(page_title="Multi-News Flip Clock", layout="centered")

# 隱藏界面
st.markdown("""<style>.stApp { margin-top: -60px; } #MainMenu, footer, header {visibility: hidden;}</style>""", unsafe_allow_html=True)

NEWS_SOURCES = {
    "中央社-即時": "https://feeds.feedburner.com/cnaFirstNews",
    "中央社-產經": "https://feeds.feedburner.com/cnaBusiness",
    "中央社-國際": "https://feeds.feedburner.com/cnaIntl",
    "中央社-社會": "https://feeds.feedburner.com/cnaSocial",
    "中央社-政治": "https://feeds.feedburner.com/cnaPolitics"
}

def get_combined_news(selected_sources):
    """抓取多個來源的新聞並合併成一個單一清單"""
    all_titles = []
    for name in selected_sources:
        url = NEWS_SOURCES[name]
        try:
            # 使用 non-cache 方式抓取以確保最新
            feed = feedparser.parse(url)
            source_tag = name.split('-')[1] # 取得 "即時", "產經" 等字樣
            for entry in feed.entries[:5]: # 每個來源取 5 則
                clean_title = re.sub(r'[^\u4e00-\u9fa5A-Z0-9\s]', '', entry.title).upper()
                all_titles.append(f"[{source_tag}] {clean_title}")
        except:
            continue
    return all_titles if all_titles else ["暫無新聞資料"]

# --- 頂部控制面板 ---
with st.expander("⚙️ 設定顯示內容", expanded=False):
    mode = st.radio("模式選擇", ["新聞輪播", "自定義訊息"], horizontal=True)
    
    if mode == "新聞輪播":
        selected = st.multiselect(
            "選擇新聞頻道 (可多選)", 
            options=list(NEWS_SOURCES.keys()),
            default=["中央社-即時"]
        )
        
        # 這裡不使用 st.cache_data，直接抓取以避免複選時抓到舊資料
        # 或者確保 cache key 包含所有選中的來源
        news_list = get_combined_news(selected)
        display_content = json.dumps(news_list)
        
        st.caption(f"📢 已載入 {len(news_list)} 則新聞 (來自: {', '.join(selected)})")
        if st.button("🔄 強制刷新新聞"):
            st.rerun()
    else:
        user_input = st.text_input("輸入自定義訊息", "HELLO TAIWAN")
        display_content = json.dumps([user_input])

# 渲染翻板
# 注意：這段程式碼會將所有選中的新聞標題一次性傳給 JavaScript
render_flip_board(display_content, stay_sec=7.0)
