import streamlit as st
import streamlit.components.v1 as components
import math
import urllib.parse

# --- 1. 極致 UI 隱藏設定 ---
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    /* 隱藏所有 Streamlit 預設組件 */
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    /* 移除邊距讓看板置頂 */
    .block-container {padding-top: 0rem; padding-bottom: 0rem;}
    body {background-color: transparent;}
    /* 調整滑桿在 App 中的顯示 (嵌入時會消失) */
    .stSlider label {color: #666; font-size: 0.9rem;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 獲取文字與參數 ---
query_params = st.query_params
is_embedded = query_params.get("embed", "false").lower() == "true"
raw_text = query_params.get("text", "")

# 強制解碼網址中文，若無則顯示預設
default_val = urllib.parse.unquote(raw_text) if raw_text else "Serena 是我的女神"

# 介面控制
if not is_embedded:
    col1, col2 = st.columns([3, 1])
    with col1:
        input_text = st.text_input("輸入內容", default_val)
    with col2:
        stay_seconds = st.slider("停留秒數", 0.5, 5.0, 1.5, 0.5)
else:
    input_text = default_val
    stay_seconds = float(query_params.get("stay", 1.5))

# --- 3. 核心邏輯：動態寬度計算 (商數限定 10 格) ---
N = len(input_text)
if N <= 1:
    cols = 1
else:
    quotient = math.ceil(N / 2)
    cols = quotient if quotient < 10 else 10

# 切割多行並補齊空格
rows_data = [list(input_text[i:i+cols]) for i in range(0, len(input_text), cols)]
for row in rows_data:
    while len(row) < cols:
        row.append(" ")

# --- 4. 生成嵌入 HTML ---
html_code = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    :root {{
        --unit-width: calc(min(72px, 94vw / {cols} - 6px));
        --unit-height: calc(var(--unit-width) * 1.5);
        --font-size: calc(var(--unit-width) * 0.85);
        --card-bg: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%);
    }}
    body {{ 
        background: transparent; display: flex; justify-content: center; align-items: center; 
        height: 100vh; margin: 0; overflow: hidden; cursor: pointer; user-select: none;
    }}
    .board-row {{ 
        display: grid; grid-template-columns: repeat({cols}, var(--unit-width)); 
        gap: 6px; perspective: 2000px;
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
    .top {{ top: 0; align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 1px solid #000; }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 6px 6px; }}
    .text {{ height: var(--unit-height); line-height: var(--unit-height); text-align: center; width: 100%; }}
    .leaf {{ 
        position: absolute; top: 0; left: 0; width: 100%; height: 50%; 
        z-index: 15; transform-origin: bottom; 
        transition: transform 0.55s cubic-bezier(0.5, 0, 0.1, 1.25); 
        transform-style: preserve-3d;
    }}
    .leaf-front {{ z-index: 16; background: var(--card-bg); }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #1a1a1a; }}
    .flipping {{ transform: rotateX(-180deg); }}
    .flap-unit::before {{
        content: ""; position: absolute; top: 50%; left: -1px; width: calc(100% + 2px); height: 3px;
        background: linear-gradient(180deg, #000, #444, #000);
        transform: translateY(-50%) translateZ(10px); z-index: 60; border-radius: 1px;
    }}
</style>
</head>
<body>
<div id="board" class="board-row"></div>
<script>
    const allData = {rows_data};
    const stayTime = {stay_seconds} * 1000;
    let curr = 0;
    let busy = false;
    let timer;

    function build(chars) {{
        document.getElementById('board').innerHTML = chars.map(c => `
            <div class="flap-unit">
                <div class="half top bt"><div class="text">${{c}}</div></div>
                <div class="half bottom bb"><div class="text">${{c}}</div></div>
                <div class="leaf">
                    <div class="half top lf"><div class="text">${{c}}</div></div>
                    <div class="half bottom lb"><div class="text">${{c}}</div></div>
                </div>
            </div>`).join('');
    }}

    function flip() {{
        if (allData.length <= 1 || busy) return;
        busy = true;
        const next = (curr + 1) % allData.length;
        const chars = allData[next];
        const units = document.querySelectorAll('.flap-unit');

        units.forEach((u, i) => {{
            setTimeout(() => {{
                const leaf = u.querySelector('.leaf');
                u.querySelector('.bt .text').innerText = chars[i];
                u.querySelector('.lb .text').innerText = chars[i];
                leaf.classList.add('flipping');
                leaf.addEventListener('transitionend', function end() {{
                    leaf.removeEventListener('transitionend', end);
                    u.querySelector('.bb .text').innerText = chars[i];
                    u.querySelector('.lf .text').innerText = chars[i];
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    leaf.offsetHeight;
                    leaf.style.transition = '';
                    if (i === units.length - 1) {{ busy = false; startTimer(); }}
                }}, {{once: true}});
            }}, i * 40);
        }});
        curr = next;
    }}

    function startTimer() {{
        clearTimeout(timer);
        timer = setTimeout(flip, stayTime);
    }}

    document.body.onclick = () => {{ if(!busy) {{ clearTimeout(timer); flip(); }} }};
    build(allData[0]);
    startTimer();
</script>
</body>
</html>
"""

components.html(html_code, height=250)
