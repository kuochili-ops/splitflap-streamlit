import streamlit as st
from urllib.parse import urlencode
from flip_board import render_flip_board  # 匯入剛剛建立的模組

# --- 頁面基礎設定 ---
st.set_page_config(layout="wide", page_title="Banksy Terminal V11.1")

# 隱藏 Streamlit 預設介面
st.markdown("""<style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: #1a1a1a !important;}
    .stApp {background-color: #1a1a1a !important;}
</style>""", unsafe_allow_html=True)

# --- 側邊欄參數設定 ---
query_params = st.query_params
default_text = query_params.get("text", "KEEP GOING")
default_stay = float(query_params.get("stay", 4.0))
default_speed = int(query_params.get("speed", 80))

with st.sidebar:
    st.title("🎨 傳送訊息給親友")
    input_text = st.text_input("想說的話", value=default_text)
    input_stay = st.slider("每頁停頓秒數", 2.0, 10.0, default_stay, 0.5)
    input_speed = st.slider("翻牌速度 (ms)", 20, 200, default_speed, 10)
    
    # 分享連結生成 (這裡請換成您實際部署的網址)
    params = {"text": input_text, "stay": input_stay, "speed": input_speed}
    # 這裡的網址會自動根據參數變動
    share_url = f"https://share.streamlit.io/your-link?{urlencode(params)}"
    
    st.divider()
    st.markdown("### 🔗 分享專屬連結")
    st.code(share_url, wrap_lines=True)

# --- 呼叫模組渲染看板 ---
render_flip_board(
    text=input_text, 
    stay_sec=input_stay, 
    flip_speed=input_speed,
    img_path="banksy-girl-with-balloon-logo-png_seeklogo-621871.png"
)
