import streamlit as st
from flip_board import render_flip_board

# 基本頁面配置
st.set_page_config(layout="wide", page_title="Split-Flap Display")

# 1. 取得 URL 參數 (確保流程不中斷)
def init_params():
    try:
        q = st.query_params
        t = q.get("text", "STAY HUNGRY")
        s = q.get("stay", "4.0")
        return str(t), float(s)
    except:
        return "STAY HUNGRY", 4.0

current_text, current_stay = init_params()

# 2. 注入全局 CSS 樣式
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .block-container {padding-top: 2rem !important; background-color: #1a1a1a;}
    .stTextInput>div>div>input {
        background-color: #262626; color: white; border: 1px solid #444;
    }
    .footer-panel {
        background: rgba(38, 38, 38, 0.8);
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #333;
        margin-top: 50px;
    }
</style>
""", unsafe_allow_html=True)

# 3. 頂部看板區域
st.markdown("<h2 style='text-align: center; color: #555;'>SPLIT-FLAP TERMINAL</h2>", unsafe_allow_html=True)
render_flip_board(text=current_text, stay_sec=current_stay)

# 4. 底部控制區域
st.write("---")
with st.container():
    st.markdown('<div class="footer-panel">', unsafe_allow_html=True)
    st.write("### ⚙️ 設定看板")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        new_text = st.text_input("輸入要顯示的訊息", value=current_text)
    with col2:
        new_stay = st.number_input("自動切換秒數", 1.0, 10.0, current_stay, step=0.5)
    
    if st.button("🚀 更新並同步看板", use_container_width=True, type="primary"):
        st.query_params["text"] = new_text
        st.query_params["stay"] = str(new_stay)
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# 5. 分享功能提示
st.info("💡 更新後，您可以直接複製瀏覽器 URL 分享給他人，他們將看到相同的內容。")
