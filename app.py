import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# --- 1. 頁面基礎設定 ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: transparent !important;}
    .stApp {background-color: transparent !important;}
    iframe { border: none; width: 100%; height: 100vh; overflow: hidden; background-color: transparent !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 圖片處理 (讀取本地圖片並轉為 Base64) ---
img_filename = "banksy-girl-with-balloon-logo-png_seeklogo-621871.png"
img_base64 = ""
if os.path.exists(img_filename):
    with open(img_filename, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode()

# --- 3. 參數獲取 ---
input_text_raw = st.query_params.get("text", "HAPPY HOLIDAY")
stay_sec = float(st.query_params.get("stay", 2.5))

# --- 4. 核心 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    :root {{
        --font-family: "PingFang TC", "Microsoft JhengHei", sans-serif;
        --flip-speed: 0.6s;
    }}
    body {{ 
        background-color: #f0f0f0;
        background-image: url("https://www.transparenttextures.com/patterns/white-wall.png");
        display: flex; flex-direction: column; align-items: center; 
        height: 100vh; margin: 0; overflow: hidden;
        padding-top: 40px; box-sizing: border-box;
    }}

    .board-case {{
        position: relative; padding: 25px 35px;
        background: rgba(30, 30, 30, 0.95); 
        border-radius: 18px; box-shadow: 0 30px 60px rgba(0,0,0,0.6);
        display: inline-flex; flex-direction: column; align-items: center;
        gap: 12px; z-index: 10;
    }}

    .row-container {{ display: flex; flex-direction: row; gap: 6px; perspective: 1200px; }}

    /* 單個翻板單元：四層物理結構 */
    .flap-unit {{
        position: relative; width: var(--unit-w); height: var(--unit-h);
        background: #222; border-radius: 6px; color: #fff; font-weight: 900;
    }}

    .msg-unit {{ --unit-w: var(--msg-w, 60px); --unit-h: calc(var(--unit-w) * 1.5); font-size: calc(var(--unit-w) * 0.9); }}
    .small-unit {{ --unit-w: 22px; --unit-h: 32px; font-size: 16px; }}

    /* 靜態層 */
    .static-half {{
        position: absolute; left: 0; width: 100%; height: 50%;
        overflow: hidden; background: #222; display: flex; justify-content: center;
    }}
    .static-top {{ top: 0; border-radius: 4px 4px 0 0; line-height: var(--unit-h); border-bottom: 1px solid #000; z-index: 1; }}
    .static-bottom {{ bottom: 0; border-radius: 0 0 4px 4px; line-height: 0px; z-index: 0; }}

    /* 動態翻轉層 */
    .leaf {{
        position: absolute; top: 0; left: 0; width: 100%; height: 50%;
        z-index: 10; transform-origin: bottom; transition: transform var(--flip-speed) ease-in;
        transform-style: preserve-3d;
    }}
    .leaf-front, .leaf-back {{
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        backface-visibility: hidden; background: #222; display: flex; justify-content: center; overflow: hidden;
    }}
    .leaf-front {{ z-index: 2; border-radius: 4px 4px 0 0; line-height: var(--unit-h); border-bottom: 1px solid #000; }}
    .leaf-back {{ 
        transform: rotateX(-180deg); border-radius: 0 0 4px 4px; line-height: 0px;
        background: linear-gradient(to top, #222 50%, #111 100%);
    }}

    .flipping .leaf {{ transform: rotateX(-180deg); }}

    /* 裝飾細節 */
    .hinge {{ position: absolute; top: 50%; left: 0; width: 100%; height: 2px; background: #000; z-index: 20; transform: translateY(-50%); }}
    .screw {{ position: absolute; width: 8px; height: 8px; background: radial-gradient(circle at 3px 3px, #777, #111); border-radius: 50%; }}

    .banksy-art {{
        position: absolute; bottom: -240px; right: 0px; width: 180px; height: 260px;
        background-image: url("data:image/png;base64,{img_base64}");
        background-size: contain; background-repeat: no-repeat; z-index: -1;
    }}
</style>
</head>
<body>
    <div class="board-case">
        <div class="screw" style="top:8px; left:8px;"></div>
        <div class="screw" style="top:8px; right:8px;"></div>
        <div id="row-msg" class="row-container"></div>
        <div id="row-date" class="row-container" style="margin-top:15px;"></div>
        <div id="row-clock" class="row-container"></div>
        <div class="screw" style="bottom:8px; left:8px;"></div>
        <div class="screw" style="bottom:8px; right:8px;"></div>
        <div id="banksy" class="banksy-art"></div>
    </div>

<script>
    function createFlap(char, type) {{
        return `
            <div class="flap-unit ${{type}}">
                <div class="static-half static-top"><div>${{char}}</div></div>
                <div class="static-half static-bottom"><div>${{char}}</div></div>
                <div class="leaf">
                    <div class="leaf-front"><div>${{char}}</div></div>
                    <div class="leaf-back"><div>${{char}}</div></div>
                </div>
                <div class="hinge"></div>
            </div>`;
    }}

    function updateFlap(unit, newChar) {{
        const oldChar = unit.querySelector('.static-top div').innerText;
        if (oldChar === newChar) return;

        unit.querySelector('.static-top div').innerText = newChar;
        unit.querySelector('.leaf-back div').innerText = newChar;

        unit.classList.remove('flipping');
        void unit.offsetWidth;
        unit.classList.add('flipping');

        setTimeout(() => {{
            unit.querySelector('.static-bottom div').innerText = newChar;
            unit.querySelector('.leaf-front div').innerText = newChar;
            unit.classList.remove('flipping');
        }}, 600);
    }}

    const inputRaw = "{input_text_raw}";
    const flapCount = 10;
    let msgPages = [];
    for (let i = 0; i < inputRaw.length; i += flapCount) {{
        msgPages.push(inputRaw.substring(i, i + flapCount).padEnd(flapCount, ' ').split(''));
    }}

    function init() {{
        const w = Math.min(60, Math.max(30, Math.floor((window.innerWidth - 120) / flapCount)));
        document.documentElement.style.setProperty('--msg-w', w + 'px');
        document.getElementById('row-msg').innerHTML = msgPages[0].map(c => createFlap(c, 'msg-unit')).join('');
        document.getElementById('row-date').innerHTML = "        ".split('').map(c => createFlap(c, 'small-unit')).join('');
        document.getElementById('row-clock').innerHTML = "     ".split('').map(c => createFlap(c, 'small-unit')).join('');
    }}

    function tick() {{
        const n = new Date();
        const dStr = (["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"][n.getMonth()] + String(n.getDate()).padStart(2,'0') + " " + ["日","一","二","三","四","五","六"][n.getDay()]).padEnd(8, ' ');
        const tStr = String(n.getHours()).padStart(2,'0') + ":" + String(n.getMinutes()).padStart(2,'0');
        document.querySelectorAll('#row-date .flap-unit').forEach((u, i) => updateFlap(u, dStr[i]));
        document.querySelectorAll('#row-clock .flap-unit').forEach((u, i) => updateFlap(u, tStr[i]));
    }}

    let pIdx = 0;
    window.onload = () => {{
        init();
        tick();
        setInterval(tick, 1000);
        if (msgPages.length > 1) setInterval(() => {{
            pIdx = (pIdx + 1) % msgPages.length;
            document.querySelectorAll('#row-msg .flap-unit').forEach((u, i) => setTimeout(() => updateFlap(u, msgPages[pIdx][i]), i*60));
        }}, {stay_sec} * 1000);
    }};
</script>
</body>
</html>
"""

components.html(html_code, height=1000, scrolling=False)
