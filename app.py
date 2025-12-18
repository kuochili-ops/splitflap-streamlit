import streamlit as st
import streamlit.components.v1 as components
import math
import urllib.parse
import html
import re

# --- 1. 極致簡約透明樣式 ---
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0; background-color: transparent !important;}
    .stApp {background: transparent !important;}
    iframe {border: none;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 徹底解決字碼格式邏輯 ---
def get_safe_text():
    # 取得網址 text 參數
    raw = st.query_params.get("text", "訊息載入中")
    
    # 解決 &#24171; 這種 HTML Entity 亂碼
    text = html.unescape(urllib.parse.unquote(raw))
    
    # 解決某些環境下產生的二次轉義問題
    if "&#" in text:
        text = html.unescape(text)
    
    # 移除多餘換行，僅保留逗號作為換行符
    text = re.sub(r'[\r\n]+', ' ', text)
    return text

input_text = get_safe_text()
stay_sec = float(st.query_params.get("stay", 2.5))

# --- 3. 處理行列與對齊 ---
if "，" in input_text or "," in input_text:
    parts = input_text.replace("，", ",").split(",")
    cols = min(max(len(p.strip()) for p in parts), 10)
    rows_data = [list(p.strip().ljust(cols)) for p in parts]
else:
    # 自動切分兩行
    N = len(input_text)
    cols = min(math.ceil(N / 2), 10) if N > 1 else 1
    rows_data = [list(input_text[i:i+cols].ljust(cols)) for i in range(0, N, cols)]

# --- 4. 核心 HTML 內容 ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    :root {{
        --unit-width: calc(min(80px, 95vw / {cols} - 6px));
        --unit-height: calc(var(--unit-width) * 1.5);
        --font-size: calc(var(--unit-width) * 1.05);
        --flip-speed: 0.6s;
    }}
    body {{ background: transparent; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; overflow: hidden; cursor: pointer; }}
    .board-row {{ display: grid; grid-template-columns: repeat({cols}, var(--unit-width)); gap: 8px; perspective: 2000px; }}
    .flap-unit {{ position: relative; width: var(--unit-width); height: var(--unit-height); background: #000; border-radius: 6px; font-family: 'Noto Sans TC', sans-serif; font-size: var(--font-size); font-weight: 900; color: #f0f0f0; }}
    .half {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%); display: flex; justify-content: center; backface-visibility: hidden; -webkit-backface-visibility: hidden; }}
    .top {{ top: 0; height: calc(50% + 1px); align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.5); }}
    .bottom {{ bottom: 0; height: 50%; align-items: flex-end; border-radius: 0 0 6px 6px; }}
    .text {{ height: var(--unit-height); width: 100%; text-align: center; position: absolute; left: 0; line-height: var(--unit-height); }}
    .top .text {{ top: 0; }}
    .bottom .text {{ bottom: 0; }}
    .leaf {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 15; transform-origin: bottom; transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }}
    .leaf-front {{ z-index: 16; background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%); }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #1a1a1a; display: flex; justify-content: center; align-items: flex-end; overflow: hidden; }}
    .flipping {{ transform: rotateX(-180deg); }}
    .flap-unit::before {{ content: ""; position: absolute; top: 50%; left: -1px; width: calc(100% + 2px); height: 2px; background: rgba(0,0,0,0.8); transform: translateY(-50%); z-index: 60; }}
</style>
</head>
<body>
<div id="board-container" class="board-row"></div>
<script>
    const allRows = {rows_data};
    const stayTime = {stay_sec} * 1000;
    let currentRowIndex = 0, isAnimating = false;

    function createRow(contentArray) {{
        return contentArray.map(char => `
            <div class="flap-unit">
                <div class="half top base-top"><div class="text">${{char}}</div></div>
                <div class="half bottom base-bottom"><div class="text">${{char}}</div></div>
                <div class="leaf">
                    <div class="half top leaf-front"><div class="text">${{char}}</div></div>
                    <div class="half bottom leaf-back"><div class="text">${{char}}</div></div>
                </div>
            </div>`).join('');
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
                u.querySelector('.leaf-back .text').innerText = nextChars[i];
                leaf.classList.add('flipping');
                setTimeout(() => {{
                    u.querySelector('.base-top .text').innerText = nextChars[i];
                    u.querySelector('.base-bottom .text').innerText = nextChars[i];
                }}, 300);
                leaf.addEventListener('transitionend', function onEnd() {{
                    leaf.removeEventListener('transitionend', onEnd);
                    u.querySelector('.leaf-front .text').innerText = nextChars[i];
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    leaf.offsetHeight; 
                    leaf.style.transition = '';
                    if (i === units.length - 1) {{ isAnimating = false; }}
                }}, {{once: true}});
            }}, i * 40);
        }});
        currentRowIndex = nextRowIndex;
    }}

    window.onload = () => {{
        document.getElementById('board-container').innerHTML = createRow(allRows[0]);
        setInterval(performFlip, stayTime);
    }};
    document.body.addEventListener('click', () => {{ if (!isAnimating) performFlip(); }});
</script>
</body>
</html>
"""
components.html(html_code, height=450)
