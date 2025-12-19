import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# --- 1. 頁面基礎設定 ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-image: url('https://www.transparenttextures.com/patterns/concrete-wall.png'); background-color: #2b2b2b;}
    iframe { border: none; width: 100%; height: 100vh; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 參數與邏輯獲取 ---
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
        --flip-speed: 0.7s;
        --glass-bg: rgba(255, 255, 255, 0.1);
        --screw-color: #888;
    }}
    body {{ 
        display: flex; justify-content: center; align-items: center; 
        height: 100vh; margin: 0; overflow: hidden;
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    }}

    /* 壓克力面板設定 */
    .acrylic-board {{
        position: relative;
        padding: 60px 50px;
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.5), inset 0 0 15px rgba(255,255,255,0.1);
        display: flex; flex-direction: column; align-items: center;
        gap: 25px;
    }}

    /* 四個角落的螺絲 */
    .acrylic-board::before, .acrylic-board::after,
    .screw-bottom-left, .screw-bottom-right {{
        content: ''; position: absolute; width: 14px; height: 14px;
        background: radial-gradient(circle at 30% 30%, #bbb, #444);
        border-radius: 50%; box-shadow: 2px 2px 4px rgba(0,0,0,0.6);
        z-index: 100;
    }}
    /* 螺絲位置 */
    .acrylic-board::before {{ top: 15px; left: 15px; }} /* 左上 */
    .acrylic-board::after {{ top: 15px; right: 15px; }} /* 右上 */
    .screw-bottom-left {{ bottom: 15px; left: 15px; position: absolute; }}
    .screw-bottom-right {{ bottom: 15px; right: 15px; position: absolute; }}

    /* 螺絲的十字刻痕 */
    .screw-mark {{
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        width: 8px; height: 1px; background: rgba(0,0,0,0.3);
    }}
    .screw-mark::after {{
        content: ''; position: absolute; width: 8px; height: 1px; 
        background: rgba(0,0,0,0.3); transform: rotate(90deg);
    }}

    /* 翻板通用樣式 */
    .row-container {{ display: flex; flex-direction: row; gap: 6px; perspective: 1000px; }}
    .flip-card {{
        position: relative; background-color: #1a1a1a; border-radius: 4px;
        color: #eee; font-weight: bold; text-align: center;
    }}

    /* 第一排：大 (訊息) */
    .msg-unit {{ width: var(--msg-w); height: calc(var(--msg-w) * 1.5); font-size: calc(var(--msg-w) * 1.1); }}
    /* 第二、三排：小 (日期、時間) */
    .small-unit {{ width: var(--small-w); height: calc(var(--small-w) * 1.4); font-size: calc(var(--small-w) * 0.9); }}

    /* 翻板物理構造 */
    .top, .bottom, .leaf-front, .leaf-back {{
        position: absolute; left: 0; width: 100%; height: 50%;
        overflow: hidden; background: #222; display: flex; justify-content: center;
    }}
    .top, .leaf-front {{ top: 0; align-items: flex-end; line-height: 0; border-radius: 4px 4px 0 0; border-bottom: 0.5px solid #000; }}
    .bottom, .leaf-back {{ bottom: 0; align-items: flex-start; line-height: 0; border-radius: 0 0 4px 4px; }}
    
    .leaf {{
        position: absolute; top: 0; left: 0; width: 100%; height: 50%;
        z-index: 10; transform-origin: bottom; transform-style: preserve-3d;
        transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .leaf-front, .leaf-back {{ backface-visibility: hidden; }}
    .leaf-back {{ transform: rotateX(-180deg); background: #222; }}
    .flipping .leaf {{ transform: rotateX(-180deg); }}

    .hinge {{
        position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
        background: #000; z-index: 20; transform: translateY(-50%);
    }}
</style>
</head>
<body>
    <div class="acrylic-board">
        <div class="screw-bottom-left"></div>
        <div class="screw-bottom-right"></div>
        
        <div id="row-msg" class="row-container"></div>
        <div id="row-date" class="row-container"></div>
        <div id="row-clock" class="row-container"></div>
    </div>

<script>
    const fullText = "{input_text}";
    // 邏輯：訊息字數除以二，最多10個
    const flapCount = Math.min(10, Math.max(4, Math.floor(fullText.length / 2)));
    
    let prevMsg = Array(flapCount).fill(' ');
    let prevDate = Array(8).fill(' ');
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
        // 確保在手機上也能橫向塞入面板
        const msgW = Math.min(65, Math.floor((vw * 0.8) / flapCount));
        document.documentElement.style.setProperty('--msg-w', msgW + 'px');
        document.documentElement.style.setProperty('--small-w', (msgW * 0.75) + 'px');
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
        for(let i=0; i<8; i++) {{ updateCard(`d${{i}}`, dStr[i], prevDate[i]); prevDate[i] = dStr[i]; }}
        for(let i=0; i<5; i++) {{ updateCard(`t${{i}}`, tStr[i], prevTime[i]); prevTime[i] = tStr[i]; }}
    }}

    let pIdx = 0;
    function cycleMsg() {{
        if (msgPages.length <= 1) return;
        pIdx = (pIdx + 1) % msgPages.length;
        msgPages[pIdx].forEach((char, i) => {{
            setTimeout(() => {{ updateCard(`m${{i}}`, char, prevMsg[i]); prevMsg[i] = char; }}, i * 100);
        }});
    }}

    window.onload = () => {{
        init();
        tick();
        msgPages[0].forEach((char, i) => {{ updateCard(`m${{i}}`, char, " "); prevMsg[i] = char; }});
        setInterval(tick, 1000);
        setInterval(cycleMsg, {stay_sec} * 1000);
    }};
    window.onresize = adjustSize;
</script>
</body>
</html>
"""

components.html(html_code, height=800, scrolling=False)
