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

# --- 2. 圖片處理 (班克西女孩) ---
img_filename = "banksy-girl-with-balloon-logo-png_seeklogo-621871.png"
img_data = ""
if os.path.exists(img_filename):
    with open(img_filename, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
        img_data = f"data:image/png;base64,{img_b64}"
else:
    img_data = "https://upload.wikimedia.org/wikipedia/en/2/21/Girl_with_Balloon.jpg"

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
        background-color: #d0d0d0; 
        background-image: url("{img_data}");
        background-repeat: no-repeat;
        background-position: right 15% top 42%; 
        background-size: auto 22vh;
        display: flex; justify-content: center; align-items: flex-start; 
        padding-top: 5vh; height: 100vh; margin: 0; overflow: hidden;
        font-family: "Impact", "Microsoft JhengHei", sans-serif;
    }}

    .acrylic-board {{
        position: relative; padding: 40px 30px; 
        background: rgba(255, 255, 255, 0.05); 
        backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px; box-shadow: 0 30px 80px rgba(0,0,0,0.5);
        display: inline-flex; flex-direction: column; align-items: center;
        gap: 15px; z-index: 10; margin-top: 2vh;
    }}

    .row-container {{ display: flex; gap: 6px; perspective: 1000px; }}

    /* --- 完全採用第一款 App 的 CSS 結構 --- */
    .card {{ 
        background: #1a1a1a; border-radius: 6px; position: relative; 
        overflow: hidden; perspective: 1000px; color: white;
    }}
    
    .msg-unit {{ width: var(--msg-w); height: calc(var(--msg-w) * 1.4); font-size: calc(var(--msg-w) * 1.0); }}
    .small-unit {{ width: 34px; height: 50px; font-size: 32px; }}

    .panel {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; }}
    .top-p {{ top: 0; border-bottom: 1px solid rgba(0,0,0,0.6); align-items: flex-end; border-radius: 6px 6px 0 0; }}
    .bottom-p {{ bottom: 0; align-items: flex-start; border-radius: 0 0 6px 6px; }}
    
    .text-node {{ position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 0; }}
    .top-p .text-node {{ bottom: -100%; }} 
    .bottom-p .text-node {{ top: -100%; }}

    .leaf-node {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform 0.4s ease-in; transform-style: preserve-3d; }}
    .leaf-side {{ position: absolute; inset: 0; backface-visibility: hidden; background: #1a1a1a; display: flex; justify-content: center; overflow: hidden; }}
    .side-back {{ transform: rotateX(-180deg); }}
    .flipping .leaf-node {{ transform: rotateX(-180deg); }}

    /* 時間與日期顯示微調 */
    #row-info {{ margin-top: 10px; display: flex; flex-direction: column; align-items: center; gap: 8px; }}
</style>
</head>
<body>
    <div class="acrylic-board">
        <div id="row-msg" class="row-container"></div>
        <div id="row-info">
            <div id="row-date" class="row-container"></div>
            <div id="row-clock" class="row-container"></div>
        </div>
    </div>

<script>
    const fullText = "{input_text}";
    const flapCount = Math.min(10, Math.floor(window.innerWidth * 0.8 / 60));
    
    let memory = {{}}; // 儲存每個卡片的目前狀態
    let isBusy = {{}};

    // --- 第一款 App 的核心翻牌動作 ---
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

    // --- 第一款 App 的連續跳動邏輯 ---
    async function smartUpdate(id, target) {{
        const tStr = String(target);
        if (memory[id] === tStr || isBusy[id]) return;
        
        isBusy[id] = true;
        const oldStr = memory[id] || " ";
        
        // 如果是數字且長度為 1，執行連續翻轉效果
        if (!isNaN(tStr) && tStr.trim() !== "" && tStr.length === 1 && !isNaN(oldStr.trim())) {{
            let curN = parseInt(oldStr), tarN = parseInt(tStr);
            while (curN !== tarN) {{
                let prev = String(curN); 
                curN = (curN + 1) % 10;
                performFlip(id, String(curN), prev);
                await new Promise(r => setTimeout(r, 150)); // 縮短數字跳動間隔增加流暢感
            }}
        }} else {{
            // 一般文字或非單一數字直接翻轉
            performFlip(id, tStr, oldStr);
        }}
        
        memory[id] = tStr;
        isBusy[id] = false;
    }}

    function init() {{
        const vw = window.innerWidth;
        const msgW = Math.min(65, Math.floor((vw * 0.85) / flapCount));
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
        
        // 初始訊息翻轉
        msgPages[0].forEach((c, i) => {{
            setTimeout(() => smartUpdate(`m${{i}}`, c), i * 100);
        }});
        
        tick();
        setInterval(tick, 1000);
        
        if (msgPages.length > 1) {{
            let pIdx = 0;
            setInterval(() => {{
                pIdx = (pIdx + 1) % msgPages.length;
                msgPages[pIdx].forEach((c, i) => {{
                    setTimeout(() => smartUpdate(`m${{i}}`, c), i * 100);
                }});
            }}, {stay_sec} * 1000);
        }}
    }};
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=False)
