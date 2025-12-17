import streamlit as st
import streamlit.components.v1 as components
import math
import urllib.parse

# --- 1. 頁面隱藏設定 ---
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0px; margin: 0px;}
    body {background-color: transparent;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 獲取文字並強制解碼 ---
query_params = st.query_params
raw_text = query_params.get("text", "請輸入文字內容")
input_text = urllib.parse.unquote(raw_text)

# --- 3. 每行 10 個字元的切割邏輯 ---
MAX_COLS = 10
# 將長字串切成長度為 10 的多個清單
rows = [list(input_text[i:i+MAX_COLS]) for i in range(0, len(input_text), MAX_COLS)]

# 補足空格確保每一行都對齊 10 格
for row in rows:
    while len(row) < MAX_COLS:
        row.append(" ")

# 準備兩組狀態 A 和 B（用於翻轉測試，這裡預設 A 為目前的文字，B 為空白或下一組）
# 如果您只需呈現單次顯示，這部分主要提供給 JS 初始化
s1_json = str(rows) # 傳入多維陣列

# --- 4. 嵌入支援多行的 HTML ---
html_code = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
        :root {{
            /* 根據 10 格固定寬度計算尺寸 */
            --unit-width: calc(min(65px, 96vw / {MAX_COLS} - 6px));
            --unit-height: calc(var(--unit-width) * 1.5);
            --font-size: calc(var(--unit-width) * 0.85);
            --card-bg: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%);
        }}
        body {{ background: transparent; display: flex; flex-direction: column; align-items: center; margin: 0; overflow-y: auto; padding: 20px 0; }}
        .board-row {{ 
            display: grid; 
            grid-template-columns: repeat({MAX_COLS}, var(--unit-width)); 
            gap: 6px; 
            perspective: 2000px; 
            margin-bottom: 15px; /* 行距 */
        }}
        .flap-unit {{ position: relative; width: var(--unit-width); height: var(--unit-height); background: #000; border-radius: 6px; font-family: 'Noto Sans TC', sans-serif; font-size: var(--font-size); font-weight: 900; color: #fff; }}
        .half {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: var(--card-bg); display: flex; justify-content: center; backface-visibility: hidden; -webkit-backface-visibility: hidden; }}
        .top {{ top: 0; align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 1px solid #000; }}
        .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 6px 6px; }}
        .text {{ height: var(--unit-height); line-height: var(--unit-height); text-align: center; }}
        .leaf {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 15; transform-origin: bottom; transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; will-change: transform; }}
        .leaf-front {{ z-index: 16; background: var(--card-bg); }} 
        .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #1a1a1a; }}
        .flipping {{ transform: rotateX(-180deg); }}
        .flap-unit::after {{ content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 1px; background: rgba(0,0,0,0.6); z-index: 50; }}
    </style>
</head>
<body>
    <div id="main-board"></div>
    <script>
        const dataRows = {s1_json};
        
        function init() {{
            const container = document.getElementById('main-board');
            container.innerHTML = dataRows.map((row, rIdx) => `
                <div class="board-row">
                    ${{row.map((char, cIdx) => `
                        <div class="flap-unit" id="u-${{rIdx}}-${{cIdx}}">
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

        // 點擊觸發全屏翻轉效果（示範回翻至空白或原字）
        function flipAll() {{
            const units = document.querySelectorAll('.flap-unit');
            units.forEach((u, i) => {{
                setTimeout(() => {{
                    const leaf = u.querySelector('.leaf');
                    leaf.classList.toggle('flipping');
                }}, i * 30);
            }});
        }}

        document.body.addEventListener('click', flipAll);
        init();
    </script>
</body>
</html>
"""

# 根據行數動態調整 iframe 高度
calc_height = len(rows) * 120 + 50
components.html(html_code, height=calc_height)
