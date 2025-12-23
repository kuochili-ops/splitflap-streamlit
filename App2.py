import streamlit as st
import feedparser
import re
from flip_board import render_flip_board

# 設定頁面，手機版建議使用 centered 佈局
st.set_page_config(page_title="Flip Clock News", layout="centered")

# 自定義 CSS 讓介面在手機上更緊湊
st.markdown("""
    <style>
    .stApp { margin-top: -50px; }
    /* 隱藏預設元件讓畫面乾淨 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* 讓 Expander 標題更醒目 */
    .p-header { font-weight: bold; color: #444; }
    </style>
    """, unsafe_allow_html=True)

def get_cna_news():
    rss_url = "https://feeds.feedburner.com/cnaFirstNews"
    try:
        feed = feedparser.parse(rss_url)
        if feed.entries:
            title = feed.entries[0].title
            # 僅保留中、英、數與空格
            clean_title = re.sub(r'[^\u4e00-\u9fa5A-Z0-9\s]', '', title).upper()
            return clean_title
        return "WAITING FOR NEWS..."
    except:
        return "NEWS ERROR"

# --- 手機友善的頂部控制面板 ---
with st.expander("⚙️ 設定顯示內容 (點擊展開)", expanded=False):
    mode = st.radio("模式選擇", ["中央社即時新聞", "自定義訊息"], horizontal=True)
    
    if mode == "中央社即時新聞":
        @st.cache_data(ttl=300)
        def fetch_news():
            return get_cna_news()
        
        display_text = fetch_news()
        st.caption(f"即時標題：{display_text}")
        if st.button("🔄 刷新新聞標題"):
            st.cache_data.clear()
            st.rerun()
    else:
        display_text = st.text_input("輸入要顯示的文字", "HELLO WORLD")

# --- 渲染翻板 ---
# 因為手機螢幕較窄，將 stay_sec 稍微拉長一點點讓長標題讀得完
render_flip_board(display_text, stay_sec=6.0)
