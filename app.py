import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# --- 1. 頁面基礎設定 ---
st.set_page_config(layout="wide", page_title="Banksy Terminal V2")

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
if os.path.exists(img_filename):
    with open(img_filename, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
        img_data = f"data:image/png;base64,{img_b64}"
else:
    img_data = "https://upload.wikimedia.org/wikipedia/en/2/21/Girl_with_Balloon.jpg"

input_text = st.query_params.get("text", "假日愉快 身體健康").upper()
stay_sec = max(3.0, float(st.query_params.get("stay", 4.0)))

# --- 3. HTML 結構優化 ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    * {{ box-sizing: border-box; }}
    body {{ 
        background-color: #e0e0e0; 
        background-image: 
            linear-gradient(rgba(0,0,0,0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0,0,0,0.05) 1px, transparent 1px),
            url("{img_data}");
        background-size: 40px 40px, 40px 40px, auto 38vh;
        background-repeat: repeat, repeat, no-repeat;
        background-position: center, center, right 8% bottom 8%; 
        display: flex; justify-content: center; align-items: center; 
        height: 100vh; margin: 0; overflow: hidden;
        font-family: "Impact", "Microsoft JhengHei", sans-serif;
    }}

    .acrylic-board {{
        position: relative; padding: 60px 50px; 
        background: rgba(255, 255, 255, 0.2); 
        backdrop-filter: blur(30px); -webkit-backdrop-filter: blur(30px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 30px; 
        box-shadow: 0 40px 100px rgba(0,0,0,0.25);
        display: inline-flex; flex-direction: column; align-items: center;
        gap: 25px; z-index: 10;
    }}

    .row-container {{ display: flex; gap: 10px; perspective: 1000px; }}

    .card {{ 
        background: #111; border-radius: 5px; position: relative; 
        overflow: hidden; color: #fff;
        box-shadow: 0 5px 15px rgba(0,0,0,0.4);
    }}
    
    /* 訊息大卡片 */
    .msg-unit {{ 
        width: var(--msg-w); 
        height: calc(var(--msg-w) * 1.35); 
        font-size: calc(var(--msg-w) * 0.85); 
    }}

    /* 時間日期小卡片 */
    .small-unit {{ width: 42px; height: 60px; font-size: 36px; }}
    .separator {{ font-size: 36px; color: #333; align-self: center; font-weight: bold; padding: 0 2px; }}

    .panel {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; }}
    .top-p {{ top: 0; border-bottom: 1px solid rgba(0,0,0,0.5); align-items: flex-end; }}
    .bottom-p {{ bottom: 0; align-items: flex-start; }}
    
    .text-node {{ position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 0; }}
    .top-p .text-node {{ bottom: -100%; }} 
    .bottom-p .text-node {{ top: -100%; }}

    .leaf-node {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform 0.45s ease-in; transform-style: preserve-3d; }}
    .leaf-side {{ position: absolute; inset: 0; backface-visibility: hidden; background: #1a1a1a; display: flex; justify-content: center; overflow: hidden; }}
    .side-back {{ transform: rotateX(-180deg); }}
    .flipping .leaf-node {{ transform: rotateX(-180deg); }}

    .brand {{ color: rgba(0,0,0,0.5); font-size: 14px; letter-spacing: 8px; font-weight: 800; margin-bottom: 10px; }}
</style>
</head>
<body>
    <div class="acrylic-board">
        <div class="brand">BANKSY TERMINAL</div>
        <div id="row-msg" class="row-container"></div>
        <div id="row-info">
            <div id="row-date" class="row-container" style="margin-bottom:10px;"></div>
            <div id="row-clock" class="row-container"></div>
        </div>
    </div>

<script>
    const fullText = "{input_text}";
    // 限制翻牌數量避免溢出，手機端會自動調整
    const flapCount = Math.max(8, Math.min(10, Math.floor(window.innerWidth * 0.8 / 70)));
    
    let memory = {{}};
    let isBusy = {{}};

    function performFlip(id, nextVal, prevVal) {{
        const el = document.getElementById(id);
        if(!el) return;
        el.innerHTML = ""; 
        el.classList.remove('flipping');
        const n = String(nextVal || " "), p = String(prevVal || " ");
        
        el.innerHTML = `
            <div class="panel top-p"><div class="text-node">${{n}}</div></div>
            <div class="panel bottom-p"><div class="text-node">${{p}}</div></div>
            <div class="leaf-node">
                <div class="leaf-side top-p"><div class="text-node">${{p}}</div></div>
                <div class="leaf-side side-back bottom-p"><div class="text-node">${{n}}</div></div>
            </div>`;
        
        requestAnimationFrame(() => {{
            void el.offsetWidth;
            requestAnimationFrame(() => el.classList.add('flipping'));
        }});
    }}

    async function smartUpdate(id, target) {{
        const tStr = String(target);
        if (memory[id] === tStr || isBusy[id]) return;
        
        isBusy[id] = true;
        const oldStr = memory[id] || " ";
        
        // 修正 NaN 邏輯：確保只有單一數字執行滾動，其餘直接翻轉
        const isNum = !isNaN(parseInt(tStr)) && tStr.length === 1 && !isNaN(parseInt(oldStr));

        if (isNum) {{
            let curN = parseInt(oldStr), tarN = parseInt(tStr);
            while (curN !== tarN) {{
                let prev = String(curN); 
                curN = (curN + 1) % 10;
                performFlip(id, String(curN), prev);
                await new Promise(r => setTimeout(r, 150));
            }}
        }} else {{
            performFlip(id, tStr, oldStr);
        }}
        
        memory[id] = tStr;
        isBusy[id] = false;
    }}

    function init() {{
        const vw = window.innerWidth;
        const msgW = Math.min(75, Math.floor((vw * 0.8) / flapCount));
        document.documentElement.style.setProperty('--msg-w', msgW + 'px');
        
        document.getElementById('row-msg').innerHTML = Array.from({{length: flapCount}}, (_, i) => `<div class="card msg-unit" id="m${{i}}"></div>`).join('');
        document.getElementById('row-date').innerHTML = Array.from({{length: 10}}, (_, i) => `<div class="card small-unit" id="d${{i}}"></div>`).join('');
        
        // 加上分隔符 :
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
        
        // 格式化日期與時間，確保不出現 NaN
        const dStr = months[n.getMonth()] + " " + String(n.getDate()).padStart(2,'0') + " " + days[n.getDay()];
        const HH = String(n.getHours()).padStart(2,'0');
        const MM = String(n.getMinutes()).padStart(2,'0');
        const SS = String(n.getSeconds()).padStart(2,'0');
        const tStr = HH + ":" + MM + ":" + SS;

        dStr.split('').forEach((c, i) => smartUpdate(`d${{i}}`, c));
        tStr.split('').forEach((c, i) => {{
            if (c !== ":") smartUpdate(`t${{i}}`, c);
        }});
    }}

    window.onload = () => {{
        init();
        const msgPages = [];
        for (let i = 0; i < fullText.length; i += flapCount) {{
            msgPages.push(fullText.substring(i, i + flapCount).padEnd(flapCount, ' ').split(''));
        }}
        
        let pIdx = 0;
        const rotateMsg = () => {{
            msgPages[pIdx].forEach((c, i) => {{
                setTimeout(() => smartUpdate(`m${{i}}`, c), i * 100);
            }});
            pIdx = (pIdx + 1) % msgPages.length;
        }};

        rotateMsg();
        tick();
        setInterval(tick, 1000);
        if (msgPages.length > 1) setInterval(rotateMsg, {stay_sec} * 1000);
    }};
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=False)
