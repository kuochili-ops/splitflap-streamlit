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

# --- 2. 圖片處理 ---
img_filename = "banksy-girl-with-balloon-logo-png_seeklogo-621871.png"
img_data = ""
if os.path.exists(img_filename):
    with open(img_filename, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
        img_data = f"data:image/png;base64,{img_b64}"
else:
    img_data = "https://upload.wikimedia.org/wikipedia/en/2/21/Girl_with_Balloon.jpg"

input_text = st.query_params.get("text", "假日愉快，身體健康").upper()
stay_sec = max(3.0, float(st.query_params.get("stay", 3.0)))

# --- 3. 核心 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    :root {{ 
        --flip-speed: 1.2s; /* 速度調慢，增加機械沉穩感 */
        --small-fixed-w: 30px; 
        --card-bg: #1a1a1a;
        --text-color: #e0e0e0;
    }}
    
    body {{ 
        display: flex; justify-content: center; align-items: flex-start; 
        padding-top: 5vh; height: 100vh; margin: 0; overflow: hidden;
        font-family: 'Helvetica Neue', Helvetica, Arial, "PingFang TC", sans-serif;
        cursor: pointer; transition: all 0.5s ease;
    }}
    
    .wall-0 {{ background: #1a1a1a; background-image: radial-gradient(circle, #2c2c2c 0%, #1a1a1a 100%); }}
    .wall-1 {{ background: #444; background-image: url("https://www.transparenttextures.com/patterns/concrete-wall.png"); }}
    .wall-2 {{ 
        background-color: #d0d0d0; 
        background-image: url("{img_data}");
        background-repeat: no-repeat;
        background-position: right 15% top 42%; 
        background-size: auto 22vh;
    }}

    .acrylic-board {{
        position: relative; padding: 50px 40px; 
        background: rgba(255, 255, 255, 0.02); 
        backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px; box-shadow: 0 40px 100px rgba(0,0,0,0.6);
        display: inline-flex; flex-direction: column; align-items: center;
        gap: 12px; z-index: 10; margin-top: 2vh;
    }}

    .screw {{
        position: absolute; width: 12px; height: 12px;
        background: radial-gradient(circle at 30% 30%, #999, #333);
        border-radius: 50%; box-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    }}
    .tl {{ top: 15px; left: 15px; }} .tr {{ top: 15px; right: 15px; }}
    .bl {{ bottom: 15px; left: 15px; }} .br {{ bottom: 15px; right: 15px; }}

    .row-container {{ display: flex; flex-direction: row; gap: 4px; perspective: 1000px; }}
    
    .flip-card {{
        position: relative; width: var(--w); height: var(--h);
        background-color: var(--card-bg); border-radius: 4px;
        font-size: var(--fs); line-height: var(--h);
        color: var(--text-color); font-weight: 700; text-align: center;
    }}

    .top, .bottom {{
        position: absolute; left: 0; width: 100%; height: 50%;
        overflow: hidden; background: var(--card-bg);
        -webkit-backface-visibility: hidden; backface-visibility: hidden;
    }}

    .top {{ 
        top: 0; border-radius: 4px 4px 0 0; 
        line-height: var(--h); border-bottom: 1px solid rgba(0,0,0,0.6); 
    }}
    .bottom {{ 
        bottom: 0; border-radius: 0 0 4px 4px; 
        line-height: 0; 
    }}

    .leaf {{
        position: absolute; top: 0; left: 0; width: 100%; height: 50%;
        z-index: 10; transform-origin: bottom; 
        /* 使用更平滑的貝茲曲線，增加慢速質感 */
        transition: transform var(--flip-speed) cubic-bezier(0.45, 0.05, 0.55, 0.95);
        transform-style: preserve-3d;
    }}

    .leaf-front, .leaf-back {{
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        -webkit-backface-visibility: hidden; backface-visibility: hidden;
        background: var(--card-bg);
    }}

    .leaf-front {{ border-radius: 4px 4px 0 0; line-height: var(--h); border-bottom: 1px solid rgba(0,0,0,0.6); }}
    .leaf-back {{ border-radius: 0 0 4px 4px; transform: rotateX(-180deg); line-height: 0; }}

    .flipping .leaf {{ transform: rotateX(-180deg); }}

    .msg-unit {{ --w: var(--msg-w); --h: calc(var(--msg-w) * 1.5); --fs: calc(var(--msg-w) * 1.1); }}
    .small-unit {{ --w: var(--small-fixed-w); --h: calc(var(--small-fixed-w) * 1.4); --fs: calc(var(--small-fixed-w) * 0.9); }}

    .hinge {{
        position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
        background: rgba(0,0,0,0.8); z-index: 15; transform: translateY(-50%);
    }}
</style>
</head>
<body class="wall-0" onclick="changeWall()">
    <div class="acrylic-board" onclick="event.stopPropagation()">
        <div class="screw tl"></div><div class="screw tr"></div>
        <div id="row-msg" class="row-container"></div>
        <div id="row-date" class="row-container" style="margin-top: 5px;"></div>
        <div id="row-clock" class="row-container"></div>
        <div class="screw bl"></div><div class="screw br"></div>
    </div>

<script>
    const fullText = "{input_text}";
    const flapCount = Math.min(10, Math.max(1, Math.floor(fullText.length / 2)));
    let wallIdx = 0;
    let pIdx = 0;

    function changeWall() {{
        wallIdx = (wallIdx + 1) % 3;
        document.body.className = "wall-" + wallIdx;
    }}

    function createFlap(id, cls) {{
        return `<div class="${{cls}} flip-card" id="${{id}}">
                    <div class="top"></div>
                    <div class="bottom"></div>
                    <div class="leaf"><div class="leaf-front"></div><div class="leaf-back"></div></div>
                    <div class="hinge"></div>
                </div>`;
    }}

    function updateCard(elId, newVal, oldVal) {{
        if (newVal === oldVal) return;
        const el = document.getElementById(elId);
        const top = el.querySelector('.top');
        const bottom = el.querySelector('.bottom');
        const leafFront = el.querySelector('.leaf-front');
        const leafBack = el.querySelector('.leaf-back');

        top.innerText = newVal;
        bottom.innerText = oldVal;
        leafFront.innerText = oldVal;
        leafBack.innerText = newVal;

        el.classList.remove('flipping');
        void el.offsetWidth; 
        el.classList.add('flipping');

        // 同步底部內容，時間設為與動畫速度一致
        setTimeout(() => {{
            bottom.innerText = newVal;
        }}, 1200); 
    }}

    function adjustSize() {{
        const vw = window.innerWidth;
        const msgW = Math.min(65, Math.floor((vw * 0.85) / flapCount));
        document.documentElement.style.setProperty('--msg-w', msgW + 'px');
    }}

    function init() {{
        adjustSize();
        document.getElementById('row-msg').innerHTML = Array.from({{length: flapCount}}, (_, i) => createFlap(`m${{i}}`, 'msg-unit')).join('');
        document.getElementById('row-date').innerHTML = Array.from({{length: 7}}, (_, i) => createFlap(`d${{i}}`, 'small-unit')).join('');
        document.getElementById('row-clock').innerHTML = Array.from({{length: 8}}, (_, i) => createFlap(`t${{i}}`, 'small-unit')).join('');
    }}

    let prevMsg = [], prevDate = [], prevTime = [];

    function tick() {{
        const n = new Date();
        const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
        const weeks = ["日","一","二","三","四","五","六"];
        const dStr = months[n.getMonth()] + String(n.getDate()).padStart(2,'0') + " " + weeks[n.getDay()];
        const tStr = String(n.getHours()).padStart(2,'0') + ":" + String(n.getMinutes()).padStart(2,'0') + ":" + String(n.getSeconds()).padStart(2,'0');

        dStr.split('').forEach((c, i) => {{ updateCard(`d${{i}}`, c, prevDate[i] || ''); prevDate[i] = c; }});
        tStr.split('').forEach((c, i) => {{ updateCard(`t${{i}}`, c, prevTime[i] || ''); prevTime[i] = c; }});
    }}

    window.onload = () => {{
        init();
        const msgPages = [];
        for (let i = 0; i < fullText.length; i += flapCount) {{
            msgPages.push(fullText.substring(i, i + flapCount).padEnd(flapCount, ' ').split(''));
        }}

        msgPages[0].forEach((c, i) => {{ updateCard(`m${{i}}`, c, ''); prevMsg[i] = c; }});
        tick();

        setInterval(tick, 1000);
        if (msgPages.length > 1) setInterval(() => {{
            pIdx = (pIdx + 1) % msgPages.length;
            msgPages[pIdx].forEach((c, i) => {{ updateCard(`m${{i}}`, c, prevMsg[i]); prevMsg[i] = c; }});
        }}, {stay_sec} * 1000);
    }};
    window.onresize = adjustSize;
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=False)
