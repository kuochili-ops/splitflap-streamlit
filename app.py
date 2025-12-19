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

# --- 2. 參數獲取 ---
input_text = st.query_params.get("text", "假日愉快，身體健康").upper()
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
        background-color: #1a1a1a;
        background-image: radial-gradient(circle at center, #2c2c2c 0%, #1a1a1a 100%);
        display: flex; justify-content: center; align-items: center; 
        height: 100vh; margin: 0; overflow: hidden;
        font-family: 'Arial Black', "PingFang TC", sans-serif;
    }}

    /* 壓克力面板：極高透明度、超緊湊行距 */
    .acrylic-board {{
        position: relative;
        padding: 40px 30px; 
        background: rgba(255, 255, 255, 0.02); 
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        box-shadow: 0 40px 100px rgba(0,0,0,0.6);
        display: inline-flex; flex-direction: column; align-items: center;
        gap: 5px; /* 進一步縮短行距 */
        z-index: 10;
    }}

    /* 螺絲：確保在手機邊緣清晰可見 */
    .screw {{
        position: absolute; width: 14px; height: 14px;
        background: radial-gradient(circle at 35% 35%, #ddd, #555);
        border-radius: 50%; box-shadow: 1px 2px 4px rgba(0,0,0,0.8);
        z-index: 50;
    }}
    .screw::after, .screw::before {{
        content: ''; position: absolute; top: 50%; left: 50%;
        width: 8px; height: 1.5px; background: rgba(0,0,0,0.5);
    }}
    .screw::after {{ transform: translate(-50%, -50%) rotate(45deg); }}
    .screw::before {{ transform: translate(-50%, -50%) rotate(-45deg); }}
    
    .tl {{ top: 12px; left: 12px; }}
    .tr {{ top: 12px; right: 12px; }}
    .bl {{ bottom: 12px; left: 12px; }}
    .br {{ bottom: 12px; right: 12px; }}

    /* 翻板基礎 */
    .row-container {{ display: flex; flex-direction: row; gap: 4px; perspective: 1200px; }}
    .flip-card {{
        position: relative; background-color: #111; border-radius: 4px;
        color: #fff; text-align: center; font-weight: bold;
    }}

    /* 排版尺寸 */
    .msg-unit {{ 
        width: var(--msg-w); height: calc(var(--msg-w) * 1.5); 
        font-size: calc(var(--msg-w) * 1.0); 
    }}
    .small-unit {{ 
        width: var(--small-w); height: calc(var(--small-w) * 1.4); 
        font-size: calc(var(--small-w) * 0.8); 
    }}

    /* 翻轉物理結構 - 保留原始邏輯 */
    .top, .bottom {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #151515; }}
    .msg-unit .top, .msg-unit .leaf-front {{ 
        top: 0; border-radius: 4px 4px 0 0; line-height: calc(var(--msg-w) * 1.5); border-bottom: 0.5px solid #000; z-index: 1; 
    }}
    .msg-unit .bottom, .msg-unit .leaf-back {{ 
        bottom: 0; border-radius: 0 0 4px 4px; line-height: 0px; z-index: 0; 
    }}
    .small-unit .top, .small-unit .leaf-front {{ 
        top: 0; border-radius: 3px 3px 0 0; line-height: calc(var(--small-w) * 1.4); border-bottom: 0.5px solid #000; z-index: 1; 
    }}
    .small-unit .bottom, .small-unit .leaf-back {{ 
        bottom: 0; border-radius: 0 0 3px 3px; line-height: 0px; z-index: 0; 
    }}

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
<body>
    <div class="acrylic-board">
        <div class="screw tl"></div><div class="screw tr"></div>
        <div class="screw bl"></div><div class="screw br"></div>

        <div id="row-msg" class="row-container"></div>
        <div id="row-date" class="row-container"></div>
        <div id="row-clock" class="row-container"></div>
    </div>

<script>
    const fullText = "{input_text}";
    const flapCount = Math.min(10, Math.max(1, Math.floor(fullText.length / 2)));
    
    let prevMsg = Array(flapCount).fill(' ');
    let prevDate = Array(10).fill(' '); // 增加長度給星期
    let prevTime = Array(5).fill(' ');
    
    let msgPages = [];
    for (let i = 0; i < fullText.length; i += flapCount) {{
        msgPages.push(fullText.substring(i, i + flapCount).padEnd(flapCount, ' ').split(''));
    }}

    function updateCard(elId, newVal, oldVal) {{
        if (newVal === oldVal) return;
        const el = document.getElementById(elId);
        if (!el) return;
        el.innerHTML = `
            <div class="top">${{newVal}}</div>
            <div class="bottom">${{oldVal}}</div>
            <div class="leaf"><div class="leaf-front">${{oldVal}}</div><div class="leaf-back">${{newVal}}</div></div>
            <div class="hinge"></div>
        `;
        el.classList.remove('flipping');
        void el.offsetWidth; 
        el.classList.add('flipping');
    }}

    function adjustSize() {{
        const vw = window.innerWidth;
        // 第一排計算：文字長度/2
        const msgW = Math.min(60, Math.floor((vw * 0.85) / flapCount));
        document.documentElement.style.setProperty('--msg-w', msgW + 'px');
        // 第二三排縮小
        document.documentElement.style.setProperty('--small-w', (msgW * 0.75) + 'px');
    }}

    function init() {{
        adjustSize();
        document.getElementById('row-msg').innerHTML = Array.from({{length: flapCount}}, (_, i) => `<div class="flip-card msg-unit" id="m${{i}}"></div>`).join('');
        document.getElementById('row-date').innerHTML = Array.from({{length: 10}}, (_, i) => `<div class="flip-card small-unit" id="d${{i}}"></div>`).join('');
        document.getElementById('row-clock').innerHTML = Array.from({{length: 5}}, (_, i) => `<div class="flip-card small-unit" id="t${{i}}"></div>`).join('');
    }}

    function tick() {{
        const n = new Date();
        const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
        const weeks = ["日","一","二","三","四","五","六"];
        
        // 格式：MONDD 星期X (例如 DEC19 一 )
        const dStr = (months[n.getMonth()] + String(n.getDate()).padStart(2,'0') + " " + weeks[n.getDay()]).padEnd(10, ' ');
        const tStr = String(n.getHours()).padStart(2,'0') + ":" + String(n.getMinutes()).padStart(2,'0');
        
        for (let i=0; i<10; i++) {{ updateCard(`d${{i}}`, dStr[i], prevDate[i]); prevDate[i] = dStr[i]; }}
        for (let i=0; i<5; i++) {{ updateCard(`t${{i}}`, tStr[i], prevTime[i]); prevTime[i] = tStr[i]; }}
    }}

    let pIdx = 0;
    function cycleMsg() {{
        if (msgPages.length <= 1) return;
        pIdx = (pIdx + 1) % msgPages.length;
        msgPages[pIdx].forEach((char, i) => {{
            setTimeout(() => {{ updateCard(`m${{i}}`, char, prevMsg[i]); prevMsg[i] = char; }}, i * 110);
        }});
    }}

    window.onload = () => {{
        init();
        tick();
        msgPages[0].forEach((char, i) => {{ updateCard(`m${{i}}`, char, " "); prevMsg[i] = char; }});
        setInterval(tick, 1000);
        if (msgPages.length > 1) setInterval(cycleMsg, {stay_sec} * 1000);
    }};
    window.onresize = adjustSize;
</script>
</body>
</html>
"""

components.html(html_code, height=600, scrolling=False)
