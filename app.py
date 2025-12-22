import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# --- 1. 頁面基礎設定 ---
st.set_page_config(layout="wide", page_title="Banksy Module Terminal")

st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: #1a1a1a !important;}
    .stApp {background-color: #1a1a1a !important;}
    iframe { border: none; width: 100%; height: 100vh; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 圖片處理 ---
img_filename = "banksy-girl-with-balloon-logo-png_seeklogo-621871.png"
img_data = "https://upload.wikimedia.org/wikipedia/en/2/21/Girl_with_Balloon.jpg"
if os.path.exists(img_filename):
    with open(img_filename, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
        img_data = f"data:image/png;base64,{img_b64}"

input_text = st.query_params.get("text", "假日愉快 身體健康").upper()
stay_sec = max(3.0, float(st.query_params.get("stay", 4.0)))

# --- 3. 核心 HTML/CSS ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    * {{ box-sizing: border-box; }}
    body {{ 
        background-color: #d8d8d8; 
        background-image: url("{img_data}");
        background-repeat: no-repeat;
        background-position: right 5% bottom 5%; 
        background-size: auto 30vh;
        display: flex; justify-content: center; align-items: center; 
        height: 100vh; margin: 0; overflow: hidden;
        font-family: "Impact", "Microsoft JhengHei", sans-serif;
    }}

    /* 壓克力透明板與四角螺絲 */
    .acrylic-board {{
        position: relative; 
        width: 90vw; max-width: 800px;
        padding: 60px 40px;
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        box-shadow: 0 40px 80px rgba(0,0,0,0.3);
        display: flex; flex-direction: column; align-items: center;
        gap: 30px; z-index: 10;
    }}

    /* 螺絲圖案 */
    .acrylic-board::before, .acrylic-board::after {{
        content: ""; position: absolute; width: 12px; height: 12px;
        background: radial-gradient(circle at center, #888 30%, #444 80%);
        border-radius: 50%; box-shadow: inset 0 1px 2px rgba(255,255,255,0.5), 0 2px 4px rgba(0,0,0,0.3);
    }}
    /* 左上與右上螺絲 */
    .acrylic-board::before {{ top: 15px; left: 15px; box-shadow: 758px 0 0 #666; }} /* 這裡的 758px 會隨寬度變動，改用更穩定的方式 */
    
    /* 修正四角螺絲佈局 */
    .screw {{ position: absolute; width: 14px; height: 14px; background: radial-gradient(circle, #aaa, #444); border-radius: 50%; border: 1px solid #777; }}
    .s-tl {{ top: 15px; left: 15px; }}
    .s-tr {{ top: 15px; right: 15px; }}
    .s-bl {{ bottom: 15px; left: 15px; }}
    .s-br {{ bottom: 15px; right: 15px; }}

    .row-container {{ display: flex; gap: 8px; perspective: 1000px; justify-content: center; width: 100%; }}

    /* 翻牌基礎樣式 */
    .card {{ background: #1a1a1a; border-radius: 4px; position: relative; overflow: hidden; color: white; }}
    
    /* 第一排：動態寬度訊息翻板 */
    .msg-unit {{ width: var(--msg-w); height: calc(var(--msg-w) * 1.4); font-size: calc(var(--msg-w) * 0.9); }}

    /* 第二三排：置中且尺寸固定 */
    .small-unit {{ width: 36px; height: 52px; font-size: 32px; }}
    .separator {{ font-size: 32px; color: #222; font-weight: bold; align-self: center; }}

    /* 翻牌動畫面板 */
    .panel {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; }}
    .top-p {{ top: 0; border-bottom: 1px solid rgba(0,0,0,0.6); align-items: flex-end; }}
    .bottom-p {{ bottom: 0; align-items: flex-start; }}
    .text-node {{ position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 0; }}
    .top-p .text-node {{ bottom: -100%; }} .bottom-p .text-node {{ top: -100%; }}
    .leaf-node {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform 0.4s ease-in; transform-style: preserve-3d; }}
    .leaf-side {{ position: absolute; inset: 0; backface-visibility: hidden; background: #1a1a1a; display: flex; justify-content: center; overflow: hidden; }}
    .side-back {{ transform: rotateX(-180deg); }}
    .flipping .leaf-node {{ transform: rotateX(-180deg); }}
</style>
</head>
<body>
    <div class="acrylic-board">
        <div class="screw s-tl"></div><div class="screw s-tr"></div>
        <div class="screw s-bl"></div><div class="screw s-br"></div>
        
        <div id="row-msg" class="row-container"></div>
        <div id="row-info" style="display: flex; flex-direction: column; gap: 10px; width: 100%;">
            <div id="row-date" class="row-container"></div>
            <div id="row-clock" class="row-container"></div>
        </div>
    </div>

<script>
    const fullText = "{input_text}";
    // 規則：翻板數 = 字元數 / 2 (商)，最多 10
    const flapCount = Math.min(10, Math.max(4, Math.floor(fullText.length / 2)));
    
    let memory = {{}};
    let isBusy = {{}};

    function performFlip(id, nextVal, prevVal) {{
        const el = document.getElementById(id);
        if(!el) return;
        el.innerHTML = ""; el.classList.remove('flipping');
        const n = String(nextVal || " "), p = String(prevVal || " ");
        el.innerHTML = `
            <div class="panel top-p"><div class="text-node">${{n}}</div></div>
            <div class="panel bottom-p"><div class="text-node">${{p}}</div></div>
            <div class="leaf-node">
                <div class="leaf-side top-p"><div class="text-node">${{p}}</div></div>
                <div class="leaf-side side-back bottom-p"><div class="text-node">${{n}}</div></div>
            </div>`;
        requestAnimationFrame(() => {{ void el.offsetWidth; el.classList.add('flipping'); }});
    }}

    async function smartUpdate(id, target) {{
        const tStr = String(target);
        if (memory[id] === tStr || isBusy[id]) return;
        isBusy[id] = true;
        const oldStr = memory[id] || " ";
        if (!isNaN(tStr) && tStr.length === 1 && !isNaN(oldStr)) {{
            let curN = parseInt(oldStr), tarN = parseInt(tStr);
            while (curN !== tarN) {{
                let prev = String(curN); curN = (curN + 1) % 10;
                performFlip(id, String(curN), prev);
                await new Promise(r => setTimeout(r, 120));
            }}
        }} else {{
            performFlip(id, tStr, oldStr);
        }}
        memory[id] = tStr; isBusy[id] = false;
    }}

    function init() {{
        const boardWidth = document.querySelector('.acrylic-board').offsetWidth;
        const msgW = Math.min(70, Math.floor((boardWidth - 100) / flapCount));
        document.documentElement.style.setProperty('--msg-w', msgW + 'px');
        
        document.getElementById('row-msg').innerHTML = Array.from({{length: flapCount}}, (_, i) => `<div class="card msg-unit" id="m${{i}}"></div>`).join('');
        document.getElementById('row-date').innerHTML = Array.from({{length: 10}}, (_, i) => `<div class="card small-unit" id="d${{i}}"></div>`).join('');
        document.getElementById('row-clock').innerHTML = `
            <div class="card small-unit" id="t0"></div><div class="card small-unit" id="t1"></div>
            <div class="separator">:</div>
            <div class="card small-unit" id="t3"></div><div class="card small-unit" id="t4"></div>
            <div class="separator">:</div>
            <div class="card small-unit" id="t6"></div><div class="card small-unit" id="t7"></div>
        `;
    }}

    function tick() {{
        const n = new Date();
        const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
        const days = ["SUN","MON","TUE","WED","THU","FRI","SAT"];
        const dStr = months[n.getMonth()] + " " + String(n.getDate()).padStart(2,'0') + " " + days[n.getDay()];
        const tStr = String(n.getHours()).padStart(2,'0') + ":" + String(n.getMinutes()).padStart(2,'0') + ":" + String(n.getSeconds()).padStart(2,'0');
        dStr.split('').forEach((c, i) => smartUpdate(`d${{i}}`, c));
        tStr.split('').forEach((c, i) => {{ if(c!==":") smartUpdate(`t${{i}}`, c); }});
    }}

    window.onload = () => {{
        init();
        const msgPages = [];
        for (let i = 0; i < fullText.length; i += flapCount) {{
            msgPages.push(fullText.substring(i, i + flapCount).padEnd(flapCount, ' ').split(''));
        }}
        let pIdx = 0;
        const updateMsg = () => {{
            msgPages[pIdx].forEach((c, i) => {{ setTimeout(() => smartUpdate(`m${{i}}`, c), i * 100); }});
            pIdx = (pIdx + 1) % msgPages.length;
        }};
        updateMsg(); tick();
        setInterval(tick, 1000);
        if (msgPages.length > 1) setInterval(updateMsg, {stay_sec} * 1000);
    }};
</script>
</body>
</html>
"""

components.html(html_code, height=850, scrolling=False)
