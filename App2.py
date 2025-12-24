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

# --- 2. 初始化狀態管理 ---
if "last_json" not in st.session_state:
    st.session_state.last_json = ""

# --- 3. 核心功能函式 ---
def get_news_data():
    """抓取即時新聞標題並進行清洗"""
    try:
        # 使用 Google News RSS (台灣繁體中文)
        feed = feedparser.parse("https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant")
        # 僅取前 10 則標題，並移除結尾的媒體名稱 (如: - 自由時報)
        news_list = []
        for entry in feed.entries[:10]:
            title = entry.title.split(' - ')[0]
            news_list.append(title)
        return news_list
    except Exception as e:
        return ["新聞系統連接中...", "請稍候再試"]

# --- 4. 側邊欄控制面版 ---
with st.sidebar:
    st.header("⚙️ 告示牌設定")
    mode = st.radio("選擇播放模式", ["即時新聞模式", "手動輸入模式"])
    
    if mode == "手動輸入模式":
        user_text = st.text_area(
            "輸入自訂訊息 (每行一則)", 
            "歡迎來到白六告示牌\n這是一個擬真翻牌系統\n祝您有美好的一天"
        )
        raw_list = user_text.split('\n')
    else:
        if st.button("🔄 刷新即時新聞"):
            st.cache_data.clear()
        raw_list = get_news_data()

    st.divider()
    stay_sec = st.slider("資訊停留秒數 (秒)", 3.0, 15.0, 7.0)
    st.info("💡 超過 16 字將自動拆分顯示")

# --- 5. 資料預處理 ---
processed_list = []
for item in raw_list:
    # 移除前後空格，英文字母大寫化
    clean_item = str(item).strip().upper().replace("'", "’")
    if clean_item:
        processed_list.append(clean_item)

if not processed_list:
    processed_list = ["WAITING FOR DATA"]

# --- 6. 渲染畫面 ---
st.title("𓃥白六新聞/訊息告示牌")

# 轉換為 JSON 字串傳遞給組件
current_json = json.dumps(processed_list)

# 渲染翻牌組件 (具備開場開機序)
render_flip_board(current_json, stay_sec=stay_sec)

# --- 7. 頁尾狀態 ---
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.caption(f"當前模式: {mode}")
with col2:
    st.caption(f"循環筆數: {len(processed_list)} 則訊息")
