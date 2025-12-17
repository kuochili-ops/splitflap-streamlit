import streamlit as st
import streamlit.components.v1 as components
import math
import urllib.parse

# --- 1. 頁面隱藏與樣式設定 ---
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding-top: 2rem;}
    body {background-color: transparent;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 獲取文字並解碼 ---
query_params = st.query_params
is_embedded = query_params.get("embed", "false").lower() == "true"
raw_url_text = query_params.get("text", "")
default_val = urllib.parse.unquote(raw_url_text) if raw_url_text else "Serena 是我的女神"

if not is_embedded:
    input_text = st.text_input("輸入句子", default_val)
else:
    input_text = default_val

# --- 3. 動態計算每行字元數 (The Logic) ---
N = len(input_text)
if N <= 1:
    cols = 1
else:
    # 商 = 總數除以 2 (無條件進位)
    quotient = math.ceil(N / 2)
    # 商如果少於 10，寬度就是商；超過 10，寬度就是 10
    cols = quotient if quotient < 10 else 10

# 根據計算出的 cols 進行切割
rows_data = [list(input_text[i:i+cols]) for i in range(0, len(input_text), cols)]
for row in rows_data:
    while len(row) < cols:
        row.append(" ")

# --- 4. 生成 HTML (含自動輪播 JS) ---
html_code = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    :root {{
        --unit-width: calc(min(75px, 94vw / {cols} - 6px));
        --unit-height: calc(var(--unit-width) * 1.5);
        --font-size: calc(var(--unit-width) * 0.85);
        --card-bg: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%);
    }}
    body {{ background: transparent; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; overflow: hidden; }}
    
    .board-row {{ 
        display: grid; 
        grid-template-columns: repeat({cols}, var(--unit-width)); 
        gap: 8px; 
        perspective: 2000px;
    }}
    .flap-unit {{ 
        position: relative; width: var(--unit-width); height: var(--unit-height); 
        background: #000; border-radius: 6px; font-family: 'Noto Sans TC', sans-serif; 
        font-size: var(--font-size); font-weight: 900; color: #f0f0f0;
    }}
    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center; 
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }}
    .top {{ top: 0; align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 1.5px solid #000; }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 6px 6px; }}
    .text {{ height: var(--unit-height); line-height: var(--unit-height); text-align: center; }}
    .leaf {{ 
        position: absolute; top: 0; left: 0; width: 100%; height: 50%; 
        z-index: 15; transform-origin: bottom; 
        transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1.2); 
        transform-style: preserve-3d;
    }}
    .leaf-front {{ z-index: 16; background: var(--card-bg); }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #1a1a1a; }}
    .flipping {{ transform: rotateX(-180deg); }}
</style>
</head>
<body>
<div id="board-container" class="board-row"></div>

<script>
    const allRows = {rows_data};
    let currentRowIndex = 0;

    function createRow(contentArray) {{
        return contentArray.map(char => `
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

    function init() {{
        document.getElementById('board-container').innerHTML = createRow(allRows[0]);
    }}

    function performFlip() {{
        if (allRows.length <= 1) return;

        const nextRowIndex = (currentRowIndex + 1) % allRows.length;
        const nextChars = allRows[nextRowIndex];
        const units = document.querySelectorAll('.flap-unit');

        units.forEach((u, i) => {{
            setTimeout(() => {{
                const leaf = u.querySelector('.leaf');
                // 準備背面的字 (即將翻下來的字)
                u.querySelector('.base-top .text').innerText = nextChars[i];
                u.querySelector('.leaf-back .text').innerText = nextChars[i];
                
                leaf.classList.add('flipping');

                leaf.addEventListener('transitionend', function onEnd() {{
                    leaf.removeEventListener('transitionend', onEnd);
                    // 同步底部的字
                    u.querySelector('.base-bottom .text').innerText = nextChars[i];
                    u.querySelector('.leaf-front .text').innerText = nextChars[i];
                    
                    // 重置動畫狀態
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    leaf.offsetHeight; // 強制重繪
                    leaf.style.transition = '';
                }});
            }}, i * 50);
        }});

        currentRowIndex = nextRowIndex;
    }}

    init();
    // 每一秒翻轉一次
    setInterval(performFlip, 2000); // 1秒停留 + 約0.6秒動畫 = 2秒一循環較舒適，可改回 1000
</script>
</body>
</html>
"""

components.html(html_code, height=300)
