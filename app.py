import streamlit as st
import streamlit.components.v1 as components

# --- 1. 設定頁面 (讓內容填滿) ---
st.set_page_config(layout="wide") # 改為 wide 模式避免左右被切

# 強制消除 Streamlit 預設的所有間距與捲軸
st.markdown("""
    <style>
    [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; margin: 0 !important;}
    iframe {display: block; width: 100%; border: none;}
    body {overflow: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 獲取參數
input_text = st.query_params.get("text", "質感看板")
unit_w = int(st.query_params.get("w", 80)) # 可選參數調整大小

# --- 2. 修正後的 HTML ---
html_code = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    
    body {{ 
        margin: 0; padding: 0; background: transparent;
        display: flex; justify-content: center; align-items: center;
        height: 100vh; overflow: hidden;
        font-family: 'Noto Sans TC', sans-serif;
    }}

    #container {{
        display: grid;
        grid-template-columns: repeat({len(input_text)}, {unit_w}px);
        gap: 12px;
        perspective: 2000px;
    }}

    .flap-unit {{
        position: relative; width: {unit_w}px; height: {unit_w * 1.4}px;
        border-radius: 8px; font-size: {unit_w * 0.85}px;
        color: #fff; font-weight: 900;
        box-shadow: 0 10px 30px rgba(0,0,0,0.8);
    }}

    /* 💡 修正：使用更穩定的文字定位法 */
    .half {{
        position: absolute; left: 0; width: 100%; height: 50%;
        overflow: hidden; background: #1a1a1a;
        backface-visibility: hidden;
    }}

    .top {{
        top: 0; border-radius: 8px 8px 0 0;
        background: linear-gradient(180deg, #3a3a3a 0%, #1a1a1a 100%);
        border-bottom: 1px solid #000;
        display: flex; align-items: flex-start; justify-content: center;
    }}

    .bottom {{
        bottom: 0; border-radius: 0 0 8px 8px;
        background: linear-gradient(180deg, #151515 0%, #000 100%);
        display: flex; align-items: flex-end; justify-content: center;
    }}

    .text {{
        height: 200%; line-height: {unit_w * 2.8}px;
        text-align: center; width: 100%;
    }}

    .bottom .text {{ transform: translateY(-50%); }}
</style>
</head>
<body>
    <div id="container">
        {"".join([f'''
        <div class="flap-unit">
            <div class="half top"><div class="text">{char}</div></div>
            <div class="half bottom"><div class="text">{char}</div></div>
        </div>
        ''' for char in input_text])}
    </div>
</body>
</html>
"""

# --- 3. 渲染組件 (高度設為組件高度的 1.5 倍確保不被切掉) ---
components.html(html_code, height=unit_w * 2)
