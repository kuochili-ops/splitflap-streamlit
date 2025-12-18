import streamlit as st
import streamlit.components.v1 as components
import math
import urllib.parse

# --- 1. 頁面配置 ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; margin: 0 !important;}
    body {background-color: transparent !important; overflow: hidden; margin: 0;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 參數獲取與分段邏輯 ---
query_params = st.query_params
raw_text = query_params.get("text", "")
input_text = urllib.parse.unquote(raw_text) if raw_text else "質感看板正常顯示中"
stay_sec = float(query_params.get("stay", 3.0))

N = len(input_text)
# 您要求的邏輯：20字內自動除以二，超過20字固定10字一幕
if N <= 20:
    cols = math.ceil(N / 2) if N > 1 else 1
    if cols > 10: cols = 10
else:
    cols = 10

# 切割分段
rows_data = [list(input_text[i:i+cols]) for i in range(0, len(input_text), cols)]
for row in rows_data:
    while len(row) < cols: row.append(" ")

# --- 3. 生成 HTML (採用絕對定位確保文字不消失) ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    
    body {{ 
        margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; 
        height: 100vh; background: transparent; font-family: 'Noto Sans TC', sans-serif;
    }}
    
    #board {{
        display: grid; gap: 8px;
        grid-template-columns: repeat({cols}, 60px);
        /* 💡 確保在手機上自動縮小，不會破圖 */
        transform: scale(min(1, calc(95vw / {cols * 68}))); 
    }}

    .flap {{
        position: relative; width: 60px; height: 90px;
        background: #000; border-radius: 4px;
        perspective: 1000px;
    }}

    .half {{
        position: absolute; left: 0; width: 100%; height: 50%;
        overflow: hidden; backface-visibility: hidden;
        background: linear-gradient(180deg, #333 0%, #1a1a1a 100%);
        display: flex; justify-content: center;
    }}

    /* 💡 改用絕對定位與 transform 確保文字在中心 */
    .text {{
        position: absolute; width: 100%; height: 180px; /* 看板總高的兩倍 */
        font-size: 54px; font-weight: 900; color: #FFFFFF !important;
        text-align: center; line-height: 180px;
        left: 0;
    }}

    .top {{ 
        top: 0; border-radius: 4px 4px 0 0; border-bottom: 1px solid #000;
        align-items: flex-start; transform-origin: bottom; transition: transform 0.6s; z-index: 2;
    }}
    .top .text {{ top: 0; }}

    .bottom {{ 
        bottom: 0; border-radius: 0 0 4px 4px;
        align-items: flex-end; z-index: 1;
    }}
    .bottom .text {{ bottom: 0; }}

    .flipping .top {{ transform: rotateX(-180deg); }}

    .flap::after {{
        content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
        background: rgba(0,0,0,0.8); z-index: 5; transform: translateY(-50%);
    }}
</style>
</head>
<body>
    <div id="board"></div>
    <script>
        const chunks = {rows_data};
        let currentIndex = 0;
        const board = document.getElementById('board');

        function render() {{
            const chars = chunks[currentIndex];
            board.innerHTML = chars.map(c => `
                <div class="flap">
                    <div class="half top"><div class="text">${{c}}</div></div>
                    <div class="half bottom"><div class="text">${{c}}</div></div>
                </div>
            `).join('');

            setTimeout(() => {{
                document.querySelectorAll('.flap').forEach((f, i) => {{
                    setTimeout(() => f.classList.add('flipping'), i * 65);
                }});
            }}, 50);

            currentIndex = (currentIndex + 1) % chunks.length;
        }}

        render();
        if (chunks.length > 1) setInterval(render, {stay_sec * 1000});
    </script>
</body>
</html>
"""

# --- 4. 給予充足高度預算 ---
components.html(html_code, height=220)
