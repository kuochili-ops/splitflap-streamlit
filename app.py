import streamlit as st
from flip_board import render_flip_board

st.set_page_config(layout="wide", page_title="Split-Flap Terminal")

# 1. 取得參數
def get_params():
    query = st.query_params
    text = query.get("text", "STAY HUNGRY")
    stay = query.get("stay", "4.0")
    return str(text), float(stay)

current_text, current_stay = get_params()

# 2. 頁面樣式
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .block-container {padding: 2rem !important; background: #1a1a1a;}
    .control-panel {
        margin-top: 100px; padding: 20px; background: #262626; 
        border-radius: 15px; border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# 3. 優先渲染頂部看板
st.write("### 📢 目前顯示內容")
render_flip_board(text=current_text, stay_sec=current_stay)

# 4. 將輸入欄放在頁面下方 (使用 Expander 或簡單 Container)
st.write("---")
with st.container():
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    st.subheader("⚙️ 修改看板訊息")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        input_text = st.text_input("輸入新訊息 (ENTER 更新)", value=current_text)
    with col2:
        input_stay = st.number_input("停留時間", 1.0, 10.0, current_stay)
    
    if st.button("🚀 點此同步更新", use_container_width=True):
        st.query_params["text"] = input_text
        st.query_params["stay"] = str(input_stay)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
