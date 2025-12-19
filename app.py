import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# --- 1. 頁面基礎設定 ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: #1a1a1a !important;}
    .stApp {background-color: #1a1a1a !important;}
    iframe { border: none; width: 100%; height: 100vh; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 圖片處理 (氣球女孩) ---
img_filename = "banksy-girl-with-balloon-logo-png_seeklogo-621871.png"
img_data = ""

# 優先讀取本地檔案，若無則使用網路預留圖
if os.path.exists(img_filename):
    with open(img_filename, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
        img_data = f"data:image/png;base64,{img_b64}"
else:
    # 預留一個可靠的網路圖片連結，防止本地檔案讀取失敗
    img_data = "https://upload.wikimedia.org/wikipedia/en/2/21/Girl_with_Balloon.jpg"

# --- 3. 參數獲取 ---
input_text = st.query_params.get("text", "假日愉快，身體健康").upper()
stay_sec = max(3.0, float(st.query_params.get("stay", 3.0)))

# --- 4. 核心 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {{ --flip-speed: 0.85s; }}
    
    body {{ 
        display: flex; justify-content: center; align-items: flex-start; 
        padding-top: 5vh; height: 100vh; margin: 0; overflow: hidden;
        font-family: 'Arial Black', "PingFang TC", sans-serif;
        cursor: pointer; transition: all 0.5s ease;
        background-size: cover; background-position: center;
    }}
    
    /* 風格 0: 深色工業 */
    .wall-0 {{ background: #1a1a1a; background-image: radial-gradient(circle, #2c2c2c 0%, #1a1a1a 100%); }}
    /* 風格 1: 水泥牆 */
    .wall-1 {{ background: #444; background-image: url("https://www.transparenttextures.com/patterns/concrete-wall.png"); }}
    /* 風格 2: Banksy 牆 */
    .wall-2 {{ 
        background-color: #e0e0e0; 
        background-image: url("{img_data}");
        background-repeat: no-repeat;
        background-position: bottom 5% right 5%;
        background-size: auto 40vh; /* 確保圖片高度足夠大 */
    }}

    .acrylic-board {{
        position: relative; padding: 45px 35px; 
        background: rgba(255, 255, 255, 0.05); 
        backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px; box-shadow: 0 30px 80px rgba(0,0,0,0.5);
        display: inline-flex; flex-direction: column; align-items: center;
        gap: 8px; z-index: 10;
    }}

    .screw {{
        position: absolute; width: 14px; height: 14px;
        background: radial-gradient(circle at 35% 35%, #eee, #444);
        border-radius: 50%; box-shadow: 1px 1px 3px rgba(0,0,0,0.6);
        z-index: 20;
    }}
    .screw::after, .screw::before {{
        content: ''; position: absolute; top: 50%; left: 50%;
        width: 8px; height: 1.5px; background: rgba(0,0,0,0.4);
    }}
    .screw::after {{ transform: translate(-50%, -50%) rotate(45deg); }}
    .screw::before {{ transform: translate(-50%, -50%) rotate(-45deg); }}
    .tl {{ top: 15px; left: 15px; }} .tr {{ top: 15px; right: 15px; }}
    .bl {{ bottom: 15px; left: 15px; }} .br {{ bottom: 15px; right: 15px; }}

    .row-container {{ display: flex; flex-direction: row; gap: 4px; perspective: 1200px; }}
    .flip-card {{ position: relative; background-color: #111; border-radius: 4px; color: #fff; text-align: center; font-weight: bold; }}
    
    .msg-unit {{ width: var(--msg-w); height: calc(var(--msg-w) * 1.5); font-size: calc(var(--msg-w) * 1.0); }}
    .small-unit {{ width: var(--small-w); height: calc(var(--small-w) * 1.4); font-size: calc(var(--small-w) * 0.85); }}

    .top, .bottom {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #151515; }}
    .msg-unit .top, .msg-unit .leaf-front {{ top: 0; border-radius: 4px 4px 0 0; line-height: calc(var(--msg-w) * 1.5); border-bottom: 0.5px solid #000; }}
    .small-unit .top, .small-unit .leaf-front {{ top: 0; border-radius: 3px 3px 0 0; line-height: calc(var(--small-w) * 1.4); border-bottom: 0.5px solid #000; }}
    .bottom, .leaf-back {{ bottom: 0; border-radius: 0 0 4px 4px; line-height: 0px; }}

    .leaf {{
        position: absolute; top: 0; left: 0; width: 100%; height: 50%;
        z-index: 10; transform-origin: bottom; transform-style: preserve-3d;
        transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .leaf-front, .leaf-back {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; backface-visibility: hidden; background: #151515; }}
    .leaf-back {{ transform: rotateX(-180deg); }}
    .flipping .leaf {{ transform: rotateX(-180deg); }}
    .hinge {{ position: absolute; top: 50%; left: 0; width: 100%; height: 1.5px; background: #000; z-index: 15; transform: translateY(-50%); }}
</style>
</head>
<body class="wall-0" onclick="changeWall()">
    <div class="acrylic-board" onclick="event.stopPropagation()">
        <div class="screw tl"></div><div class="screw tr"></div>
        <div class="screw bl"></div><div class="screw br"></div>
        <div id="row-msg" class="row-container"></div>
        <div id="row-date" class="row-container"></div>
        <div id="row-clock" class="row-container"></div>
    </div>

<script>
    const fullText = "{input_text}";
    const flapCount = Math.min(10, Math.max(1, Math.floor(fullText.length / 2)));
    let wallIdx = 0;
    
    function changeWall() {{
        wallIdx = (wallIdx + 1) % 3;
        document.body.className = "wall-" + wallIdx;
    }}

    let prevMsg = Array(flapCount).fill(' ');
    let prevDate = Array(7).fill(' '); 
    let prevTime = Array(8).fill(' '); 

    let msgPages = [];
    for (let i = 0; i < fullText.length; i += flapCount) {{
        msgPages.push(fullText.substring(i, i + flapCount).padEnd(flapCount, ' ').split(''));
    }}

    function updateCard(elId, newVal, oldVal) {{
        if (newVal === oldVal) return;
        const el = document.getElementById(elId);
        if (!el) return;
        el.innerHTML = `<div class="top">${{newVal}}</div><div class="bottom">${{oldVal}}</div>
                        <div class="leaf"><div class="leaf-front">${{oldVal}}</div><div class="leaf-back">${{newVal}}</div></div>
                        <div class="hinge"></div>`;
        el.classList.remove('flipping');
        void el.offsetWidth; el.classList.add('flipping');
    }}

    function adjustSize() {{
        const vw = window.innerWidth;
        const msgW = Math.min(65, Math.floor((vw * 0.85) / flapCount));
        document.documentElement.style.setProperty('--msg-w', msgW + 'px');
        document.documentElement.style.setProperty('--small-w', (msgW * 0.72) + 'px');
    }}

    function init() {{
        adjustSize();
        document.getElementById('row-msg').innerHTML = Array.from({{length: flapCount}}, (_, i) => `<div class="flip-card msg-unit" id="m${{i}}"></div>`).join('');
        document.getElementById('row-date').innerHTML = Array.from({{length: 7}}, (_, i) => `<div class="flip-card small-unit" id="d${{i}}"></div>`).join('');
        document.getElementById('row-clock').innerHTML = Array.from({{length: 8}}, (_, i) => `<div class="flip-card small-unit" id="t${{i}}"></div>`).join('');
    }}

    function tick() {{
        const n = new Date();
        const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
        const weeks = ["日","一","二","三","四","五","六"];
        const dStr = months[n.getMonth()] + String(n.getDate()).padStart(2,'0') + " " + weeks[n.getDay()];
        const tStr = String(n.getHours()).padStart(2,'0') + ":" + String(n.getMinutes()).padStart(2,'0') + ":" + String(n.getSeconds()).padStart(2,'0');
        for (let i=0; i<7; i++) {{ updateCard(`d${{i}}`, dStr[i] || ' ', prevDate[i]); prevDate[i] = dStr[i]; }}
        for (let i=0; i<8; i++) {{ updateCard(`t${{i}}`, tStr[i], prevTime[i]); prevTime[i] = tStr[i]; }}
    }}

    window.onload = () => {{
        init(); tick();
        msgPages[0].forEach((char, i) => {{ updateCard(`m${{i}}`, char, " "); prevMsg[i] = char; }});
        setInterval(tick, 1000);
        if (msgPages.length > 1) setInterval(() => {{
            pIdx = (pIdx + 1) % msgPages.length;
            msgPages[pIdx].forEach((char, i) => {{ updateCard(`m${{i}}`, char, prevMsg[i]); prevMsg[i] = char; }});
        }}, {stay_sec} * 1000);
    }};
    let pIdx = 0;
    window.onresize = adjustSize;
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=False)
