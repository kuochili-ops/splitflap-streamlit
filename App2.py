import streamlit as st
import streamlit.components.v1 as components
import math
import urllib.parse

# --- 1. 頁面隱藏與樣式設定 ---
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    /* 隱藏 Streamlit 標誌、選單與頁尾 */
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    /* 調整間距，讓看板更靠頂端 */
    .block-container {padding-top: 2rem; padding-bottom: 0rem;}
    body {background-color: transparent;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 統一文字獲取與解碼邏輯 ---
query_params = st.query_params
is_embedded = query_params.get("embed", "false").lower() == "true"
raw_url_text = query_params.get("text", "")

# 如果有網址參數則解碼，否則給予預設值
default_val = urllib.parse.unquote(raw_url_text) if raw_url_text else "Serena 是我的女神"

# 判斷是否顯示輸入框：非嵌入模式下才顯示
if not is_embedded:
    input_text = st.text_input("輸入句子 (每行自動 10 字)", default_val)
else:
    input_text = default_val

# --- 3. 每行 10 個字元的切割與補位邏輯 ---
MAX_COLS = 10
# 將輸入文字切分為每 10 個字一組的陣列 (多行)
rows_data = [list(input_text[i:i+MAX_COLS]) for i in range(0, len(input_text), MAX_COLS)]

# 確保每一行都有 10 個元素，不足的補空白
for row in rows_data:
    while len(row) < MAX_COLS:
        row.append(" ")

# --- 4. 生成 HTML 程式碼 ---
html_code = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    
    :root {{
        /* 固定 10 格的寬度計算 */
        --unit-width: calc(min(70px, 94vw / {MAX_COLS} - 6px));
        --unit-height: calc(var(--unit-width) * 1.5);
        --font-size: calc(var(--unit-width) * 0.85);
        --card-bg: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%);
    }}

    body {{ background: transparent; display: flex; flex-direction: column; align-items: center; padding: 20px 0; margin: 0; overflow-x: hidden; }}
    
    .board-row {{ 
        display: grid; 
        grid-template-columns: repeat({MAX_COLS}, var(--unit-width)); 
        gap: 6px; 
        perspective: 2500px; 
        margin-bottom: 12px;
    }}

    .flap-unit {{ 
        position: relative; 
        width: var(--unit-width); 
        height: var(--unit-height); 
        background: #000; 
        border-radius: 6px; 
        font-family: 'Noto Sans TC', sans-serif; 
        font-size: var(--font-size); 
        font-weight: 900; 
        color: #f0f0f0;
        box-shadow: 0 10px 25px rgba(0,0,0,0.6);
    }}

    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; 
        overflow: hidden; 
        background: var(--card-bg); 
        display: flex; justify-content: center; 
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }}

    .top {{ 
        top: 0; align-items: flex-start; 
        border-radius: 6px 6px 0 0; 
        border-bottom: 1.5px solid rgba(0,0,0,0.8); 
    }}
    .bottom {{ 
        bottom: 0; align-items: flex-end; 
        border-radius: 0 0 6px 6px; 
    }}
    .text {{ height: var(--unit-height); line-height: var(--unit-height); text-align: center; width: 100%; }}

    .leaf {{ 
        position: absolute; top: 0; left: 0; width: 100%; height: 50%; 
        z-index: 15; transform-origin: bottom; 
        transition: transform 0.55s cubic-bezier(0.5, 0, 0.1, 1.25);
        transform-style: preserve-3d;
        will-change: transform, filter;
    }}

    .leaf-front {{ z-index: 16; background: var(--card-bg); }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #1a1a1a; }}
    
    .flipping {{ 
        transform: rotateX(-180deg); 
        filter: contrast(1.1);
    }}

    /* 中央軸承設計 */
    .flap-unit::before {{
        content: ""; position: absolute; top: 50%; left: -1px; width: calc(100% + 2px); height: 3px;
        background: linear-gradient(180deg, #000, #444, #000);
        transform: translateY(-50%) translateZ(10px); z-index: 60;
        border-radius: 1px;
    }}

    .leaf-front::after {{
        content: ""; position: absolute; top:0; left:0; width:100%; height:100%;
        background: rgba(0,0,0,0); transition: background 0.4s;
    }}
    .flipping .leaf-front::after {{ background: rgba(0,0,0,0.4); }}
</style>
</head>
<body>
<div id="main-board"></div>

<script>
    const rows = {rows_data};
    let isFlipped = false;

    function init() {{
        const container = document.getElementById('main-board');
        container.innerHTML = rows.map((row, rIdx) => `
            <div class="board-row">
                ${{row.map((char, cIdx) => `
                    <div class="flap-unit">
                        <div class="half top"><div class="text">${{char}}</div></div>
                        <div class="half bottom"><div class="text">${{char}}</div></div>
                        <div class="leaf">
                            <div class="half top leaf-front"><div class="text">${{char}}</div></div>
                            <div class="half bottom leaf-back"><div class="text">${{char}}</div></div>
                        </div>
                    </div>
                `).join('')}}
            </div>
        `).join('');
    }}

    function flip() {{
        const units = document.querySelectorAll('.flap-unit');
        units.forEach((u, i) => {{
            setTimeout(() => {{
                u.querySelector('.leaf').classList.toggle('flipping');
            }}, i * 30);
        }});
    }}

    document.body.addEventListener('click', flip);
    init();
</script>
</body>
</html>
"""

# 根據行數動態調整 iframe 高度
calc_height = max(350, len(rows_data) * 130)
components.html(html_code, height=calc_height)
