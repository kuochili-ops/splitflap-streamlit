import streamlit as st
import json
import requests
from flip_board_2 import render_flip_board

st.set_page_config(page_title="Flip Board Controller", layout="wide")

# --- 1. 抓取即時新聞函式 ---
def get_latest_news():
    """抓取 Google News RSS 或其他公開 API 的標題"""
    try:
        # 這裡以簡易新聞來源為例，您可以更換為 NewsAPI 或其他來源
        url = "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
        # 註：在真實部署環境中，建議使用 feedparser 解析 RSS
        # 這裡模擬抓取後的清理過的文字列表
        return [
            "聯準會宣布降息一碼",
            "台北國際電腦展今日開幕",
            "全球氣候變遷論壇達共識",
            "科技大廠發表最新 AI 晶片"
        ]
    except:
        return ["新聞抓取失敗，請檢查網路連接"]

# --- 2. 側邊欄控制面版 ---
st.sidebar.header("⚙️ 看板控制面版")
mode = st.sidebar.radio("請選擇顯示模式", ["即時新聞連結", "手動自訂訊息"])

if mode == "手動自訂訊息":
    user_input = st.sidebar.text_area("輸入訊息 (每行一則)", "HELLO WORLD\nSTREAMLIT IS COOL")
    display_content = user_input.split('\n')
else:
    if st.sidebar.button("手動重整新聞"):
        st.cache_data.clear()
    display_content = get_latest_news()

# --- 3. 翻牌顯示 logic ---
st.title("🗂️ 工業風機械翻牌看板")

# 處理內容：確保非空字串，並過濾掉特殊字元避免 JS 錯誤
safe_content = [str(line).strip().upper().replace("'", "’") for line in display_content if line.strip()]

if not safe_content:
    safe_content = ["WAITING FOR INPUT"]

# 呼叫我們修正過的元件
render_flip_board(json.dumps(safe_content), stay_sec=8.0)

# --- 4. 底部狀態顯示 ---
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.info(f"當前模式：{mode}")
with col2:
    st.success(f"循環筆數：{len(safe_content)} 筆")
