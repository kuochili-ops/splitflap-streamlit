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

# --- 2. 核心功能函式 ---
def get_news_data():
    """抓取即時新聞標題"""
    try:
        feed = feedparser.parse("https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant")
        return [entry.title.split(' - ')[0] for entry in feed.entries[:10]]
    except Exception:
        return ["新聞系統連接中...", "請稍候再試"]

# --- 3. 側邊欄控制面版 ---
with st.sidebar:
    st.header("⚙️ 告示牌設定")
    mode = st.radio("選擇播放模式", ["即時新聞模式", "手動輸入模式"])
    
    if mode == "手動輸入模式":
        user_text = st.text_area(
            "輸入自訂訊息 (每行一則)", 
            "歡迎使用本系統\n祝您有美好的一天"
        )
        raw_list = user_text.split('\n')
    else:
        if st.button("🔄 刷新即時新聞"):
            st.cache_data.clear()
        raw_list = get_news_data()

    st.divider()
    stay_sec = st.slider("資訊停留秒數 (秒)", 3.0, 15.0, 7.0)

# --- 4. 資料預處理 (關鍵邏輯) ---
# 強制第 0 則為標題
processed_list = ["白六新聞/訊息告示牌"]

# 將其餘內容加入列表
for item in raw_list:
    clean_item = str(item).strip().upper().replace("'", "’")
    if clean_item:
        processed_list.append(clean_item)

# --- 5. 渲染畫面 ---
# 顯示網頁標題
st.markdown("<h2 style='text-align: center; color: #555; font-family: Microsoft JhengHei;'>𓃥 白六新聞 / 訊息告示牌</h2>", unsafe_allow_html=True)

# 傳遞給翻牌組件
# 注意：JS 端會自動從第 0 則開始顯示，4秒後切換到第 1 則，達成妳的要求
render_flip_board(json.dumps(processed_list), stay_sec=stay_sec)

# --- 6. 狀態顯示 ---
st.markdown("---")
st.caption(f"當前模式: {mode} | 總計 {len(processed_list)-1} 則輪播內容")
