import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# --- 1. 頁面基礎設定 ---
st.set_page_config(layout="wide", page_title="Banksy Terminal V3")

st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: #1a1a1a !important;}
    .stApp {background-color: #1a1a1a !important;}
    iframe { border: none; width: 100%; height: 100vh; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 圖片處理 (班克西女孩) ---
img_filename = "banksy-girl-with-balloon-logo-png_seeklogo-621871.png"
img_data = "https://upload.wikimedia.org/wikipedia/en/2/21/Girl_with_Balloon.jpg"
if os.path.exists(img_filename):
    with open(img_filename, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
        img_data = f"data:image/png;base64,{img_b64}"

input_text = st.query_params.get("text", "假日愉快 身體健康").upper()
stay_sec = max(3.0, float(st.query_params.get("stay", 4.0)))

# --- 3. 整合 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    * {{ box-sizing: border-box; }}
    body {{ 
        background-color: #dcdcdc; 
        background-image: url("{img_data}");
        background-repeat: no-repeat;
        background-position: right 10% bottom 10%; 
        background-size: auto 32vh;
        display: flex; justify-content: center; align-items: center; 
        height: 100vh; margin: 0; overflow: hidden;
        font-family: "Impact", "Microsoft JhengHei", sans-serif;
    }}

    .acrylic-board {{
        position: relative; 
        width: 92vw; max-width: 850px;
        padding: 55px 30px;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 20px;
        box-shadow: 0 30px 70px rgba(0,0,0,0.2);
        display: flex; flex-direction: column; align-items: center;
        gap: 25px; z-index: 10;
    }}

    /* 四角螺絲修正 */
    .screw {{ position: absolute; width: 15px; height: 15px; background: radial-gradient(circle at 30% 30%, #eee, #666); border-radius: 50%; box-shadow: 1px 1px 3px rgba(0,0,0,0.3); }}
    .s-tl {{ top: 20px; left: 20px; }}
    .s-tr {{ top: 20px; right: 20px; }}
    .s-bl {{ bottom: 20px; left: 20px; }}
    .s-br {{ bottom: 20px; right: 20px; }}

    .row-container {{ display: flex; gap: 6px; perspective: 1000px; justify-content: center; width: 100%; flex-wrap: nowrap; }}

    .card {{ background: #151515; border-radius: 4px; position: relative; overflow: hidden; color: white; }}
    
    /* 訊息翻板 (動態寬度) */
    .msg-unit {{ width: var(--msg-w); height: calc(var(--msg-w) * 1.35); font-size: calc(var(--msg-w) * 0.9); }}

    /* 時間日期 (固定尺寸) */
    .small-unit {{ width: 34px; height: 50px; font-size: 30px; }}
    .separator {{ font-size: 30px; color: #444; font-weight: bold; align-self: center; line-height: 50px; }}

    .panel {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; }}
    .top-p {{ top: 0; border-bottom: 1px solid rgba(0,0,0,0.5); align-items: flex-end; }}
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
        <div id="row-info" style="display: flex; flex-direction: column; gap: 8px; width: 100%; align-items: center;">
            <div id="row-date" class="row-container"></div>
            <div id="row-clock" class="row-container"></div>
        </div>
    </div>

<script>
    const fullText = "{input_text}";
    // 規則：商數，上限 10
    const flapCount = Math.min(10, Math.floor(fullText.length / 2) || 4);
    
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
        
        // 嚴格判定：僅單一數字且舊值也是數字時滾動，解決 NaN 問題
        const isNumeric = /^[0-9]$/.test(tStr) && /^[0-9 ]$/.test(oldStr);

        if (isNumeric && oldStr !== " ") {{
            let curN = parseInt(oldStr), tarN = parseInt(tStr);
            while (curN !== tarN) {{
                let prev = String(curN); 
                curN = (curN + 1) % 10;
                performFlip(id, String(curN), prev);
                await new Promise(r => setTimeout(r, 100));
            }}
        }} else {{
            performFlip(id, tStr, oldStr);
        }}
        memory[id] = tStr; isBusy[id] = false;
    }}

    function init() {{
        const board = document.querySelector('.acrylic-board');
        const msgW = Math.min(80, Math.floor((board.offsetWidth - 80) / flapCount));
        document.documentElement.style.setProperty('--msg-w', msgW + 'px');
        
        document.getElementById('row-msg').innerHTML = Array.from({{length: flapCount}}, (_, i) => `<div class="card msg-unit" id="m${{i}}"></div>`).join('');
        document.getElementById('row-date').innerHTML = Array.from({{length: 10}}, (_, i) => `<div class="card small-unit" id="d${{i}}"></div>`).join('');
        
        // 重新構建時間列，避免 ID 錯位導致 NaN
        const clockRow = document.getElementById('row-clock');
        clockRow.innerHTML = "";
        ['h0','h1','sep1','m0','m1','sep2','s0','s1'].forEach(type => {{
            if(type.startsWith('sep')) {{
                const s = document.createElement('div'); s.className='separator'; s.innerText=':'; clockRow.appendChild(s);
            }} else {{
                const c = document.createElement('div'); c.className='card small-unit'; c.id = type; clockRow.appendChild(c);
            }}
        }});
    }}

    function tick() {{
        const n = new Date();
        const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
        const days = ["SUN","MON","TUE","WED","THU","FRI","SAT"];
        
        // 日期處理
        const dStr = months[n.getMonth()] + " " + String(n.getDate()).padStart(2,'0') + " " + days[n.getDay()];
        dStr.split('').forEach((c, i) => smartUpdate(`d${{i}}`, c));

        // 時間處理 (拆解避免 NaN)
        const h = String(n.getHours()).padStart(2,'0');
        const m = String(n.getMinutes()).padStart(2,'0');
        const s = String(n.getSeconds()).padStart(2,'0');
        
        smartUpdate('h0', h[0]); smartUpdate('h1', h[1]);
        smartUpdate('m0', m[0]); smartUpdate('m1', m[1]);
        smartUpdate('s0', s[0]); smartUpdate('s1', s[1]);
    }}

    window.onload = () => {{
        init();
        const msgPages = [];
        for (let i = 0; i < fullText.length; i += flapCount) {{
            msgPages.push(fullText.substring(i, i + flapCount).padEnd(flapCount, ' ').split(''));
        }}
        let pIdx = 0;
        const rotateMsg = () => {{
            msgPages[pIdx].forEach((c, i) => {{ setTimeout(() => smartUpdate(`m${{i}}`, c), i * 100); }});
            pIdx = (pIdx + 1) % msgPages.length;
        }};
        rotateMsg(); tick();
        setInterval(tick, 1000);
        if (msgPages.length > 1) setInterval(rotateMsg, {stay_sec} * 1000);
    }};
</script>
</body>
</html>
"""

components.html(html_code, height=850, scrolling=False)
