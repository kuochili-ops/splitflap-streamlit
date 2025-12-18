import streamlit as st
import streamlit.components.v1 as components
import math
import urllib.parse

# --- 1. 頁面隱藏與樣式設定 ---
st.set_page_config(layout="wide") # 使用 wide 避免手機版邊距壓縮
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; margin: 0 !important;}
    body {background-color: transparent; overflow: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 參數獲取與分段邏輯 ---
query_params = st.query_params
raw_url_text = query_params.get("text", "")
input_text = urllib.parse.unquote(raw_url_text) if raw_url_text else "質感顯示看板正常運作中"
stay_seconds = float(query_params.get("stay", 3.0))

# 您要求的邏輯：
# 20 字以內，除以二的商為每行字數，最多 10 字。
# 大於 20 字，每 10 字一幕。
N = len(input_text)
if N <= 20:
    cols = math.ceil(N / 2) if N > 1 else 1
    if cols > 10: cols = 10
else:
    cols = 10

# 建立分段數據 (Chunks)
rows_data = [list(input_text[i:i+cols]) for i in range(0, len(input_text), cols)]
for row in rows_data:
    while len(row) < cols:
        row.append(" ") # 補空格保持長度一致

# --- 3. 生成 HTML (修正半字與定位) ---
html_code = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    
    :root {{
        /* 💡 修正：使用更穩定的寬度計算，確保不超出螢幕 */
        --unit-width: calc(min(65px, 92vw / {cols} - 6px));
        --unit-height: calc(var(--unit-width) * 1.4);
        --font-size: calc(var(--unit-width) * 0.82);
    }}

    body {{ 
        background: transparent; margin: 0; display: flex; 
        justify-content: center; align-items: center; 
        height: 100vh; overflow: hidden;
        font-family: 'Noto Sans TC', sans-serif;
    }}
    
    .board-row {{ 
        display: grid; 
        grid-template-columns: repeat({cols}, var(--unit-width)); 
        gap: 8px; 
        perspective: 2000px;
    }}

    .flap-unit {{ 
        position: relative; width: var(--unit-width); height: var(--unit-height); 
        background: #000; border-radius: 6px; 
        font-size: var(--font-size); font-weight: 900; color: #fff;
    }}

    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: linear-gradient(180deg, #333 0%, #1a1a1a 100%); 
        display: flex; justify-content: center; 
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }}

    .top {{ top: 0; align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 1px solid #000; }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 6px 6px; }}

    /* 💡 核心修正：精準的 line-height 解決「半字」 */
    .text {{ 
        height: var(--unit-height); 
        line-height: calc(var(--unit-height) * 1.02); /* 微微增加行高確保垂直置中 */
        text-align: center; width: 100%; 
    }}
    .bottom .text {{ transform: translateY(-50%); }}

    .leaf {{ 
        position: absolute; top: 0; left: 0; width: 100%; height: 50%; 
        z-index: 15; transform-origin: bottom; 
        transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1); 
        transform-style: preserve-3d;
    }}
    .leaf-front {{ z-index: 16; background: linear-gradient(180deg, #333 0%, #1a1a1a 100%); }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #111; }}
    .flipping {{ transform: rotateX(-180deg); }}

    /* 轉軸線 */
    .flap-unit::after {{
        content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
        background: rgba(0,0,0,0.8); z-index: 20; transform: translateY(-50%);
    }}
</style>
</head>
<body>
<div id="board-container" class="board-row"></div>

<script>
    const allRows = {rows_data};
    const stayTime = {stay_seconds} * 1000;
    let currentRowIndex = 0;
    let isAnimating = false;

    function createRow(chars) {{
        return chars.map(char => `
            <div class="flap-unit">
                <div class="half top base-top"><div class="text">${{char}}</div></div>
                <div class="half bottom base-bottom"><div class="text">${{char}}</div></div>
                <div class="leaf">
                    <div class="half top leaf-front"><div class="text">${{char}}</div></div>
                    <div class="half bottom leaf-back"><div class="text">${{char}}</div></div>
                </div>
            </div>
        `).join('');
    }}

    function performFlip() {{
        if (allRows.length <= 1 || isAnimating) return;
        isAnimating = true;

        const nextRowIndex = (currentRowIndex + 1) % allRows.length;
        const nextChars = allRows[nextRowIndex];
        const units = document.querySelectorAll('.flap-unit');

        units.forEach((u, i) => {{
            setTimeout(() => {{
                const leaf = u.querySelector('.leaf');
                u.querySelector('.base-top .text').innerText = nextChars[i];
                u.querySelector('.leaf-back .text').innerText = nextChars[i];
                
                leaf.classList.add('flipping');

                leaf.addEventListener('transitionend', function onEnd() {{
                    leaf.removeEventListener('transitionend', onEnd);
                    u.querySelector('.base-bottom .text').innerText = nextChars[i];
                    u.querySelector('.leaf-front .text').innerText = nextChars[i];
                    
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    leaf.offsetHeight; 
                    leaf.style.transition = '';
                    
                    if (i === units.length - 1) isAnimating = false;
                }});
            }}, i * 50);
        }});
        currentRowIndex = nextRowIndex;
    }}

    document.getElementById('board-container').innerHTML = createRow(allRows[0]);
    if (allRows.length > 1) setInterval(performFlip, stayTime);
</script>
</body>
</html>
"""

# --- 4. 關鍵修正：給予足夠高度預算避免切字 ---
components.html(html_code, height=250)
