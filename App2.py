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
    body {background-color: transparent !important; overflow: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 您的分段規劃邏輯 ---
query_params = st.query_params
raw_text = query_params.get("text", "")
input_text = urllib.parse.unquote(raw_text) if raw_text else "質感看板正常顯示"
stay_sec = float(query_params.get("stay", 3.0))

N = len(input_text)
# 邏輯：20字內除以二(最多10字)，超過20字固定10字一幕
if N <= 20:
    cols = math.ceil(N / 2) if N > 1 else 1
    if cols > 10: cols = 10
else:
    cols = 10

# 切割分段
rows_data = [list(input_text[i:i+cols]) for i in range(0, len(input_text), cols)]
for row in rows_data:
    while len(row) < cols: row.append(" ") # 補空格

# --- 3. 核心 HTML (解決無字問題) ---
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
        transform: scale(min(1, calc(94vw / {cols * 68}))); /* 螢幕自動縮放 */
    }}

    .flap {{
        position: relative; width: 60px; height: 90px;
        background: #000; border-radius: 4px;
        font-size: 54px; font-weight: 900; color: #FFFFFF !important; /* 強制白色 */
        perspective: 1000px;
    }}

    .half {{
        position: absolute; left: 0; width: 100%; height: 50%;
        overflow: hidden; backface-visibility: hidden;
        background: linear-gradient(180deg, #333 0%, #1a1a1a 100%);
    }}

    .top {{ 
        top: 0; border-radius: 4px 4px 0 0; border-bottom: 1px solid #000;
        display: flex; align-items: flex-start; justify-content: center;
        transform-origin: bottom; transition: transform 0.6s; z-index: 2;
    }}

    .bottom {{ 
        bottom: 0; border-radius: 0 0 4px 4px;
        display: flex; align-items: flex-end; justify-content: center;
        background: linear-gradient(180deg, #151515 0%, #000 100%); z-index: 1;
    }}

    /* 💡 徹底解決「沒字」或「半字」：強制行高並確保顏色顯示 */
    .text {{ 
        display: block; width: 100%; height: 180px; 
        line-height: 180px; text-align: center; color: #FFFFFF;
    }}
    
    .bottom .text {{ transform: translateY(-50%); }}
    .flipping .top {{ transform: rotateX(-180deg); }}

    /* 轉軸細節 */
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

            // 觸發翻轉動畫
            setTimeout(() => {{
                document.querySelectorAll('.flap').forEach((f, i) => {{
                    setTimeout(() => f.classList.add('flipping'), i * 70);
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

# --- 4. 關鍵修正：解決容器高度裁切問題 ---
components.html(html_code, height=250)
