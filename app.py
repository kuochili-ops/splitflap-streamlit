import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# --- 1. 頁面基礎設定 ---
st.set_page_config(layout="wide", page_title="Banksy Flip Board")

# 隱藏 Streamlit 預設元件並優化背景
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
if os.path.exists(img_filename):
    with open(img_filename, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
        img_data = f"data:image/png;base64,{img_b64}"
else:
    # 備用圖片 (使用高品質版)
    img_data = "https://upload.wikimedia.org/wikipedia/en/2/21/Girl_with_Balloon.jpg"

# 取得參數
input_text = st.query_params.get("text", "假日愉快 身體健康").upper()
stay_sec = max(3.0, float(st.query_params.get("stay", 4.0)))

# --- 3. 整合優化後的 HTML/CSS ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    * {{ box-sizing: border-box; }}
    body {{ 
        background-color: #c4c4c4; 
        background-image: 
            linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px),
            url("{img_data}");
        background-size: 50px 50px, 50px 50px, auto 35vh;
        background-repeat: repeat, repeat, no-repeat;
        background-position: center, center, right 10% bottom 10%; 
        display: flex; justify-content: center; align-items: center; 
        height: 100vh; margin: 0; overflow: hidden;
        font-family: "Impact", "Microsoft JhengHei", sans-serif;
    }}

    /* 強化壓克力板質感 */
    .acrylic-board {{
        position: relative; padding: 50px; 
        background: rgba(255, 255, 255, 0.1); 
        backdrop-filter: blur(25px) saturate(150%);
        -webkit-backdrop-filter: blur(25px) saturate(150%);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 24px; 
        box-shadow: 
            0 50px 100px rgba(0,0,0,0.3),
            inset 0 0 40px rgba(255,255,255,0.1);
        display: inline-flex; flex-direction: column; align-items: center;
        gap: 20px; z-index: 10;
        transition: all 0.5s ease;
    }}

    .row-container {{ display: flex; gap: 8px; perspective: 1000px; }}

    /* 強化卡片細節 */
    .card {{ 
        background: #111; border-radius: 4px; position: relative; 
        overflow: hidden; color: #eee;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }}
    
    .msg-unit {{ 
        width: var(--msg-w); 
        height: calc(var(--msg-w) * 1.4); 
        font-size: calc(var(--msg-w) * 0.9); 
        font-weight: 900;
    }}
    .small-unit {{ width: 38px; height: 56px; font-size: 34px; font-weight: bold; }}

    .panel {{ 
        position: absolute; left: 0; width: 100%; height: 50%; 
        overflow: hidden; background: linear-gradient(to bottom, #222 0%, #111 100%); 
        display: flex; justify-content: center; 
    }}
    .top-p {{ top: 0; border-bottom: 1px solid rgba(0,0,0,0.7); align-items: flex-end; }}
    .bottom-p {{ bottom: 0; align-items: flex-start; background: linear-gradient(to top, #222 0%, #111 100%); }}
    
    .text-node {{ position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 0; }}
    .top-p .text-node {{ bottom: -100%; }} 
    .bottom-p .text-node {{ top: -100%; }}

    .leaf-node {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }}
    .leaf-side {{ position: absolute; inset: 0; backface-visibility: hidden; display: flex; justify-content: center; overflow: hidden; }}
    .side-front {{ background: linear-gradient(to bottom, #222 0%, #111 100%); }}
    .side-back {{ transform: rotateX(-180deg); background: linear-gradient(to top, #222 0%, #111 100%); }}
    .flipping .leaf-node {{ transform: rotateX(-180deg); }}

    /* 機場標誌感的光澤效果 */
    .card::after {{
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, transparent 50%, rgba(0,0,0,0.1) 100%);
        pointer-events: none; z-index: 20;
    }}

    #row-info {{ margin-top: 15px; display: flex; flex-direction: column; align-items: center; gap: 12px; }}
    .brand {{ color: rgba(0,0,0,0.4); font-size: 12px; letter-spacing: 4px; font-weight: bold; }}
</style>
</head>
<body>
    <div class="acrylic-board">
        <div class="brand">BANKSY TERMINAL</div>
        <div id="row-msg" class="row-container"></div>
        <div id="row-info">
            <div id="row-date" class="row-container"></div>
            <div id="row-clock" class="row-container"></div>
        </div>
    </div>

<script>
    const fullText = "{input_text}";
    // 動態計算翻牌數量：增加最小寬度保障
    const flapCount = Math.max(8, Math.min(12, Math.floor(window.innerWidth * 0.9 / 80)));
    
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
                <div class="leaf-side side-front top-p"><div class="text-node">${{p}}</div></div>
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
        
        // 數字跳動動畫
        if (!isNaN(tStr) && tStr.trim() !== "" && tStr.length === 1 && !isNaN(oldStr.trim())) {{
            let curN = parseInt(oldStr), tarN = parseInt(tStr);
            while (curN !== tarN) {{
                let prev = String(curN); 
                curN = (curN + 1) % 10;
                performFlip(id, String(curN), prev);
                await new Promise(r => setTimeout(r, 120));
            }}
        }} else {{
            performFlip(id, tStr, oldStr);
        }}
        
        memory[id] = tStr;
        isBusy[id] = false;
    }}

    function init() {{
        const vw = window.innerWidth;
        // 優化中文寬度
        const msgW = Math.min(80, Math.floor((vw * 0.9) / flapCount));
        document.documentElement.style.setProperty('--msg-w', msgW + 'px');
        
        document.getElementById('row-msg').innerHTML = Array.from({{length: flapCount}}, (_, i) => `<div class="card msg-unit" id="m${{i}}"></div>`).join('');
        document.getElementById('row-date').innerHTML = Array.from({{length: 10}}, (_, i) => `<div class="card small-unit" id="d${{i}}"></div>`).join('');
        document.getElementById('row-clock').innerHTML = Array.from({{length: 8}}, (_, i) => `<div class="card small-unit" id="t${{i}}"></div>`).join('');
    }}

    function tick() {{
        const n = new Date();
        const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
        const days = ["SUN","MON","TUE","WED","THU","FRI","SAT"];
        
        const dStr = months[n.getMonth()] + " " + String(n.getDate()).padStart(2,'0') + " " + days[n.getDay()];
        const tStr = String(n.getHours()).padStart(2,'0') + ":" + String(n.getMinutes()).padStart(2,'0') + ":" + String(n.getSeconds()).padStart(2,'0');

        dStr.split('').forEach((c, i) => smartUpdate(`d${{i}}`, c));
        tStr.split('').forEach((c, i) => smartUpdate(`t${{i}}`, c));
    }}

    window.onload = () => {{
        init();
        const msgPages = [];
        for (let i = 0; i < fullText.length; i += flapCount) {{
            msgPages.push(fullText.substring(i, i + flapCount).padEnd(flapCount, ' ').split(''));
        }}
        
        let pIdx = 0;
        const updateMsg = () => {{
            msgPages[pIdx].forEach((c, i) => {{
                setTimeout(() => smartUpdate(`m${{i}}`, c), i * 80);
            }});
        }};

        updateMsg();
        tick();
        setInterval(tick, 1000);
        
        if (msgPages.length > 1) {{
            setInterval(() => {{
                pIdx = (pIdx + 1) % msgPages.length;
                updateMsg();
            }}, {stay_sec} * 1000);
        }}
    }};
</script>
</body>
</html>
"""

components.html(html_code, height=800, scrolling=False)
