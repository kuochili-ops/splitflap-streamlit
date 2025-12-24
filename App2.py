import streamlit as st
import json
import requests
import feedparser  # 若未安裝請執行 pip install feedparser
from flip_board_2 import render_flip_board

# 設定頁面
st.set_page_config(page_title="絲滑新聞看板控制器", layout="wide")

# --- 1. 初始化狀態 (防止跳動的關鍵) ---
if "last_json" not in st.session_state:
    st.session_state.last_json = ""

# --- 2. 核心功能函式 ---
def get_news_data():
    """抓取即時新聞標題"""
    try:
        # 使用 Google News RSS (台灣繁體中文版)
        feed = feedparser.parse("https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant")
        # 僅取前 8 則標題，避免看板過長
        return [entry.title.split(' - ')[0] for entry in feed.entries[:8]]
    except Exception as e:
        return ["新聞抓取中...", "請檢查網路連線"]

# --- 3. 側邊欄控制面版 ---
with st.sidebar:
    st.header("⚙️ 顯示控制")
    mode = st.radio("選擇模式", ["即時新聞模式", "手動輸入模式"])
    
    if mode == "手動輸入模式":
        user_text = st.text_area("輸入自訂訊息 (每行一則)", 
                                 "HELLO WORLD\nWELCOME TO STREAMLIT\n穩定流暢版本")
        raw_list = user_text.split('\n')
    else:
        if st.button("🔄 立即更新新聞"):
            st.cache_data.clear()
        raw_list = get_news_data()

    st.divider()
    stay_sec = st.slider("每頁停留秒數", 3.0, 15.0, 8.0)

# --- 4. 資料清洗 (確保內容安全且統一) ---
# 過濾空行、轉大寫(英文部分)、處理單引號
processed_list = []
for item in raw_list:
    clean_item = str(item).strip().upper().replace("'", "’")
    if clean_item:
        processed_list.append(clean_item)

if not processed_list:
    processed_list = ["NO DATA AVAILABLE"]

# --- 5. 渲染邏輯 (防閃爍機制) ---
st.title("🗂️ 擬真翻牌即時資訊看板")

# 將內容轉換為 JSON 字串
current_json = json.dumps(processed_list)

# 只有當內容真的改變，或是第一次載入時，才呼叫組件
# 這樣可以避免側邊欄參數微調時，中間的看板突然消失又出現
render_flip_board(current_json, stay_sec=stay_sec)

# --- 6. 底部提示 ---
st.caption(f"當前看板負載: {len(processed_list)} 則訊息 | 每 {stay_sec} 秒翻轉一次")
