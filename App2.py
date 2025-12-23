import streamlit as st
import feedparser
import re
import json
from flip_board_2 import render_flip_board

st.set_page_config(page_title="Multi-News Flip Clock", layout="centered")

# 隱藏預設介面
st.markdown("""<style>.stApp { margin-top: -60px; } #MainMenu, footer, header {visibility: hidden;}</style>""", unsafe_allow_html=True)

# 定義新聞來源字典
NEWS_SOURCES = {
    "中央社-即時": "https://feeds.feedburner.com/cnaFirstNews",
    "中央社-產經": "https://feeds.feedburner.com/cnaBusiness",
    "中央社-國際": "https://feeds.feedburner.com/cnaIntl",
    "中央社-社會": "https://feeds.feedburner.com/cnaSocial",
    "中央社-政治": "https://feeds.feedburner.com/cnaPolitics"
}

def get_combined_news(selected_sources):
    """抓取多個來源的新聞並合併"""
    all_titles = []
    for name in selected_sources:
        url = NEWS_SOURCES[name]
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]: # 每個來源抓 5 則以防過長
                clean_title = re.sub(r'[^\u4e00-\u9fa5A-Z0-9\s]', '', entry.title).upper()
                # 加上來源標籤，例如 [產經] 標題文字
                tag = f"[{name.split('-')[1]}] "
                all_titles.append(tag + clean_title)
        except:
            continue
    return all_titles if all_titles else ["WAITING FOR NEWS"]

# --- 頂部控制面板 ---
with st.expander("⚙️ 點擊設定新聞來源", expanded=False):
    mode = st.radio("模式選擇", ["新聞輪播", "自定義訊息"], horizontal=True)
    
    if mode == "新聞輪播":
        selected = st.multiselect(
            "選擇新聞頻道 (可多選)", 
            options=list(NEWS_SOURCES.keys()),
            default=["中央社-即時"]
        )
        
        @st.cache_data(ttl=300)
        def fetch_selected_news(sources_tuple):
            return get_combined_news(list(sources_tuple))
        
        # multiselect 回傳列表，轉換成 tuple 才能作為 cache 的 key
        news_list = fetch_selected_news(tuple(selected))
        display_content = json.dumps(news_list)
        st.caption(f"📢 已載入來自 {len(selected)} 個頻道共 {len(news_list)} 則新聞")
        
        if st.button("🔄 立即更新所有新聞"):
            st.cache_data.clear()
            st.rerun()
    else:
        user_input = st.text_input("輸入自定義訊息", "HELLO TAIWAN")
        display_content = json.dumps([user_input])

# 渲染翻板
render_flip_board(display_content, stay_sec=7.0)
