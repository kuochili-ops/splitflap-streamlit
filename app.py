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
    iframe { border: none; width: 100%; height: 100vh; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 圖片處理 ---
img_filename = "banksy-girl-with-balloon-logo-png_seeklogo-621871.png"
img_base64 = ""
if os.path.exists(img_filename):
    with open(img_filename, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode()

# --- 3. 參數獲取 ---
input_text = st.query_params.get("text", "HAPPY HOLIDAY")
stay_sec = float(st.query_params.get("stay", 2.5))

# --- 4. 核心 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {{
        --flip-speed: 0.6s;
        --card-bg: #222;
    }}
    body {{ 
        background-color: #f0f0f0;
        background-image: url("https://www.transparenttextures.com/patterns/white-wall.png");
        display: flex; flex-direction: column; align-items: center; 
        height: 100vh; margin: 0; overflow: hidden; padding-top: 5vh;
    }}

    .board-case {{
        position: relative; padding: 30px;
        background: rgba(30, 30, 30, 0.95); 
        border-radius: 20px; box-shadow: 0 30px 60px rgba(0,0,0,0.5);
        display: inline-flex; flex-direction: column; align-items: center;
        gap: 15px; z-index: 10; max-width: 95vw;
    }}

    .row-container {{ display: flex; flex-direction: row; gap: 6px; perspective: 1000px; }}

    /* 物理翻板基礎結構 */
    .flap-unit {{
        position: relative;
        background: var(--card-bg);
        border-radius: 4px;
        color: #fff;
        font-weight: 900;
        font-family: "PingFang TC", "Microsoft JhengHei", sans-serif;
    }}

    /* 訊息列尺寸 (較大) */
    .msg-unit {{ 
        width: var(--msg-w); 
        height: calc(var(--msg-w) * 1.5); 
        font-size: calc(var(--msg-w) * 0.9); 
    }}

    /* 日期時間列尺寸 (較小) */
    .small-unit {{ 
        width: var(--small-w); 
        height: calc(var(--small-w) * 1.4); 
        font-size: calc(var(--small-w) * 0.8); 
    }}

    .static-half {{
        position: absolute; left: 0; width: 100%; height: 50%;
        overflow: hidden; background: #222; display: flex; justify-content: center;
    }}
    
    /* 調整文字對齊 */
    .msg-unit .static-top {{ top: 0; border-radius: 4px 4px 0 0; line-height: calc(var(--msg-w) * 1.5); border-bottom: 1px solid #000; z-index: 1; }}
    .small-unit .static-top {{ top: 0; border-radius: 3px 3px 0 0; line-height: calc(var(--small-w) * 1.4); border-bottom: 0.5px solid #000; z-index: 1; }}
    
    .static-bottom {{ bottom: 0; line-height: 0px; z-index: 0; }}
    .msg-unit .static-bottom {{ border-radius: 0 0 4px 4px; }}
    .small-unit .static-bottom {{ border-radius: 0 0 3px 3px; }}

    .leaf {{
        position: absolute; top: 0; left: 0; width: 100%; height: 50%;
        z-index: 10; transform-origin: bottom; transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1);
        transform-style: preserve-3d;
    }}
    .leaf-front, .leaf-back {{
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        backface-visibility: hidden; background: #222; display: flex; justify-content: center; overflow: hidden;
    }}
    
    .msg-unit .leaf-front {{ border-radius: 4px 4px 0 0; line-height: calc(var(--msg-w) * 1.5); border-bottom: 1px solid #000; }}
    .small-unit .leaf-front {{ border-radius: 3px 3px 0 0; line-height: calc(var(--small-w) * 1.4); border-bottom: 0.5px solid #000; }}
    
    .leaf-back {{ transform: rotateX(-180deg); line-height: 0px; background: linear-gradient(to top, #222 50%, #111 100%); }}
    .msg-unit .leaf-back {{ border-radius: 0 0 4px 4px; }}
    .small-unit .leaf-back {{ border-radius: 0 0 3px 3px; }}

    .flipping .leaf {{ transform: rotateX(-180deg); }}
    .hinge {{ position: absolute; top: 50%; left: 0; width: 100%; height: 2px; background: #000; z-index: 20; transform: translateY(-50%); }}

    .banksy-art {{
        position: absolute; bottom: -200px; right: 0; width: 150px; height: 220px;
        background-image: url("data:image/png;base64,{img_base64}");
        background-size: contain; background-repeat: no-repeat; z-index: -1;
    }}
</style>
</head>
<body>
    <div class="board-case" id="main-board">
        <div id="row-msg" class="row-container"></div>
        <div id="row-date" class="row-container" style="margin-top:15px; opacity: 0.8;"></div>
        <div id="row-clock" class="row-container" style="opacity: 0.8;"></div>
        <div id="banksy" class="banksy-art"></div>
    </div>

<script>
    const fullText = "{input_text}";
    // 規則：字數 <= 20 則商數 (字數/2)，否則上限 10
    const flapCount = Math.min(10, fullText.length <= 20 ? Math.floor(fullText.length / 2) : 10);
    
    let msgPages = [];
    for (let i = 0; i < fullText.length; i += flapCount) {{
        msgPages.push(fullText.substring(i, i + flapCount).padEnd(flapCount, ' ').split(''));
    }}

    function createHTML(char, unitClass) {{
        return `<div class="flap-unit ${{unitClass}}">
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
        const current = unit.querySelector('.static-top div').innerText;
        if (current === newChar) return;
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

    function adjustSize() {{
        const availableW = window.innerWidth * 0.9;
        
        // 訊息列寬度計算 (大)
        const msgUnitW = Math.min(80, Math.floor(availableW / (flapCount + 1)));
        document.documentElement.style.setProperty('--msg-w', msgUnitW + 'px');

        // 日期時間寬度計算 (小，固定比例)
        const smallUnitW = Math.max(20, Math.floor(msgUnitW * 0.5));
        document.documentElement.style.setProperty('--small-w', smallUnitW + 'px');
    }}

    function init() {{
        adjustSize();
        document.getElementById('row-msg').innerHTML = msgPages[0].map(c => createHTML(c, 'msg-unit')).join('');
        document.getElementById('row-date').innerHTML = "        ".split('').map(c => createHTML(c, 'small-unit')).join('');
        document.getElementById('row-clock').innerHTML = "     ".split('').map(c => createHTML(c, 'small-unit')).join('');
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
            document.querySelectorAll('#row-msg .flap-unit').forEach((u, i) => setTimeout(() => updateFlap(u, msgPages[pIdx][i]), i*80));
        }}, {stay_sec} * 1000);
    }};
    window.onresize = adjustSize;
</script>
</body>
</html>
"""

components.html(html_code, height=800, scrolling=False)
