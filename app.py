import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# --- 1. 頁面基礎設定 ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: #222 !important;}
    .stApp {background-color: #222 !important;}
    iframe { border: none; width: 100%; height: 100vh; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 參數獲取 ---
input_text = st.query_params.get("text", "HAPPY HOLIDAY").upper()
stay_sec = max(3.0, float(st.query_params.get("stay", 3.0)))

# --- 3. 核心 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {{
        --flip-speed: 0.85s; 
    }}
    body {{ 
        background-color: #222;
        background-image: url("https://www.transparenttextures.com/patterns/dark-matter.png");
        display: flex; justify-content: center; align-items: center; 
        height: 100vh; margin: 0; overflow: hidden;
        font-family: 'Arial Black', "PingFang TC", sans-serif;
    }}

    /* 壓克力面板：透明、磨砂、四角螺絲 */
    .acrylic-board {{
        position: relative;
        padding: 50px 40px;
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        box-shadow: 0 30px 60px rgba(0,0,0,0.5);
        display: inline-flex; flex-direction: column; align-items: center;
        gap: 15px; z-index: 10;
    }}

    /* 螺絲樣式 */
    .screw {{
        position: absolute; width: 12px; height: 12px;
        background: radial-gradient(circle at 30% 30%, #999, #444);
        border-radius: 50%; box-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }}
    .screw::after {{
        content: '+'; position: absolute; top: 50%; left: 50%;
        transform: translate(-50%, -50%); color: rgba(0,0,0,0.4);
        font-size: 10px; font-family: serif; font-weight: bold;
    }}
    .tl {{ top: 15px; left: 15px; }}
    .tr {{ top: 15px; right: 15px; }}
    .bl {{ bottom: 15px; left: 15px; }}
    .br {{ bottom: 15px; right: 15px; }}

    /* 翻板基礎 */
    .row-container {{ display: flex; flex-direction: row; gap: 6px; perspective: 1500px; }}
    .flip-card {{
        position: relative; background-color: #1a1a1a; border-radius: 6px;
        color: #f0f0f0; text-align: center; font-weight: bold;
    }}

    /* 排版尺寸：第一排大，其餘小 */
    .msg-unit {{ 
        width: var(--msg-w); height: calc(var(--msg-w) * 1.5); 
        font-size: calc(var(--msg-w) * 1.0); 
    }}
    .small-unit {{ 
        width: var(--small-w); height: calc(var(--small-w) * 1.4); 
        font-size: calc(var(--small-w) * 0.8); 
    }}

    /* 保留原有的翻轉物理結構 */
    .top, .bottom {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; }}
    
    .msg-unit .top, .msg-unit .leaf-front {{ 
        top: 0; border-radius: 6px 6px 0 0; line-height: calc(var(--msg-w) * 1.5); border-bottom: 0.5px solid #000; z-index: 1; 
    }}
    .msg-unit .bottom, .msg-unit .leaf-back {{ 
        bottom: 0; border-radius: 0 0 6px 6px; line-height: 0px; z-index: 0; 
    }}

    .small-unit .top, .small-unit .leaf-front {{ 
        top: 0; border-radius: 4px 4px 0 0; line-height: calc(var(--small-w) * 1.4); border-bottom: 0.5px solid #000; z-index: 1; 
    }}
    .small-unit .bottom, .small-unit .leaf-back {{ 
        bottom: 0; border-radius: 0 0 4px 4px; line-height: 0px; z-index: 0; 
    }}

    .leaf {{
        position: absolute; top: 0; left: 0; width: 100%; height: 50%;
        z-index: 10; transform-origin: bottom; transform-style: preserve-3d;
        transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .leaf-front, .leaf-back {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; backface-visibility: hidden; background: #1a1a1a; overflow: hidden; }}
    .leaf-back {{ transform: rotateX(-180deg); }}
    .flipping .leaf {{ transform: rotateX(-180deg); }}
    .hinge {{ position: absolute; top: 50%; left: 0; width: 100%; height: 2px; background: #000; z-index: 15; transform: translateY(-50%); }}

</style>
</head>
<body>
    <div class="acrylic-board">
        <div class="screw tl"></div><div class="screw tr"></div>
        <div class="screw bl"></div><div class="screw br"></div>

        <div id="row-msg" class="row-container"></div>
        <div id="row-date" class="row-container" style="opacity: 0.8;"></div>
        <div id="row-clock" class="row-container" style="opacity: 0.8;"></div>
    </div>

<script>
    const fullText = "{input_text}";
    // 邏輯：訊息字數除以二的商數，最多10個
    const flapCount = Math.min(10, Math.max(1, Math.floor(fullText.length / 2)));
    
    let prevMsg = Array(flapCount).fill(' ');
    let prevDate = Array(8).fill(' ');
    let prevTime = Array(5).fill(' ');
    
    let msgPages = [];
    for (let i = 0; i < fullText.length; i += flapCount) {{
        msgPages.push(fullText.substring(i, i + flapCount).padEnd(flapCount, ' ').split(''));
    }}

    // 完全保留你原始的更新邏輯
    function updateCard(elId, newVal, oldVal) {{
        if (newVal === oldVal) return;
        const el = document.getElementById(elId);
        if (!el) return;
        el.innerHTML = `
            <div class="top">${{newVal}}</div>
            <div class="bottom">${{oldVal}}</div>
            <div class="leaf">
                <div class="leaf-front">${{oldVal}}</div>
                <div class="leaf-back">${{newVal}}</div>
            </div>
            <div class="hinge"></div>
        `;
        el.classList.remove('flipping');
        void el.offsetWidth; 
        el.classList.add('flipping');
    }}

    function adjustSize() {{
        const vw = window.innerWidth;
        // 根據寬度計算格寬，確保不溢出螢幕
        const msgW = Math.min(75, Math.floor((vw * 0.85) / flapCount));
        document.documentElement.style.setProperty('--msg-w', msgW + 'px');
        document.documentElement.style.setProperty('--small-w', (msgW * 0.7) + 'px');
    }}

    function init() {{
        adjustSize();
        document.getElementById('row-msg').innerHTML = Array.from({{length: flapCount}}, (_, i) => `<div class="flip-card msg-unit" id="m${{i}}"></div>`).join('');
        document.getElementById('row-date').innerHTML = Array.from({{length: 8}}, (_, i) => `<div class="flip-card small-unit" id="d${{i}}"></div>`).join('');
        document.getElementById('row-clock').innerHTML = Array.from({{length: 5}}, (_, i) => `<div class="flip-card small-unit" id="t${{i}}"></div>`).join('');
    }}

    function tick() {{
        const n = new Date();
        const dStr = (["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"][n.getMonth()] + String(n.getDate()).padStart(2,'0') + "  ").substring(0,8);
        const tStr = String(n.getHours()).padStart(2,'0') + ":" + String(n.getMinutes()).padStart(2,'0');
        
        for (let i=0; i<8; i++) {{ updateCard(`d${{i}}`, dStr[i], prevDate[i]); prevDate[i] = dStr[i]; }}
        for (let i=0; i<5; i++) {{ updateCard(`t${{i}}`, tStr[i], prevTime[i]); prevTime[i] = tStr[i]; }}
    }}

    let pIdx = 0;
    function cycleMsg() {{
        if (msgPages.length <= 1) return;
        pIdx = (pIdx + 1) % msgPages.length;
        const currentPage = msgPages[pIdx];
        currentPage.forEach((char, i) => {{
            setTimeout(() => {{
                updateCard(`m${{i}}`, char, prevMsg[i]);
                prevMsg[i] = char;
            }}, i * 110);
        }});
    }}

    window.onload = () => {{
        init();
        tick();
        msgPages[0].forEach((char, i) => {{
            updateCard(`m${{i}}`, char, " ");
            prevMsg[i] = char;
        }});
        setInterval(tick, 1000);
        if (msgPages.length > 1) setInterval(cycleMsg, {stay_sec} * 1000);
    }};
    window.onresize = adjustSize;
</script>
</body>
</html>
"""

components.html(html_code, height=800, scrolling=False)
