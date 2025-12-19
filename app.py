import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# --- 1. 頁面基礎設定 ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: transparent !important;}
    .stApp {background-color: transparent !important;}
    iframe { border: none; width: 100%; height: 100vh; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 圖片處理 (氣球女孩) ---
img_filename = "banksy-girl-with-balloon-logo-png_seeklogo-621871.png"
img_base64 = ""
if os.path.exists(img_filename):
    with open(img_filename, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode()

# --- 3. 參數獲取 ---
input_text = st.query_params.get("text", "HAPPY HOLIDAY")
stay_sec = max(3.0, float(st.query_params.get("stay", 3.0)))

# --- 4. 核心 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {{
        --flip-speed: 0.85s; /* 慢速且有重量感的翻轉 */
    }}
    body {{ 
        background-color: #f0f0f0;
        background-image: url("https://www.transparenttextures.com/patterns/white-wall.png");
        display: flex; flex-direction: column; align-items: center; 
        height: 100vh; margin: 0; overflow: hidden; padding-top: 5vh;
        font-family: 'Arial Black', "PingFang TC", sans-serif;
    }}

    .board-case {{
        position: relative; padding: 25px 35px;
        background: rgba(25, 25, 25, 0.98); 
        border-radius: 12px; box-shadow: 0 40px 80px rgba(0,0,0,0.6);
        display: inline-flex; flex-direction: column; align-items: center;
        gap: 15px; z-index: 10; max-width: 95vw;
    }}

    .row-container {{ display: flex; flex-direction: row; gap: 4px; perspective: 1500px; }}

    .flip-card {{
        position: relative; background-color: #222; border-radius: 6px;
        color: #f0f0f0; text-align: center; font-weight: bold;
        transition: transform 0.2s;
    }}

    .msg-unit {{ width: var(--msg-w); height: calc(var(--msg-w) * 1.5); font-size: calc(var(--msg-w) * 1.0); }}
    .small-unit {{ width: var(--small-w); height: calc(var(--small-w) * 1.4); font-size: calc(var(--small-w) * 0.8); }}

    /* 結構與動畫 */
    .top, .bottom {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #222; }}
    .top {{ top: 0; border-radius: 6px 6px 0 0; line-height: var(--line-h); border-bottom: 0.5px solid #000; z-index: 1; }}
    .bottom {{ bottom: 0; border-radius: 0 0 6px 6px; line-height: 0px; z-index: 0; }}

    .leaf {{
        position: absolute; top: 0; left: 0; width: 100%; height: 50%;
        z-index: 10; transform-origin: bottom; transform-style: preserve-3d;
        transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .leaf-front, .leaf-back {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; backface-visibility: hidden; background: #222; overflow: hidden; }}
    .leaf-front {{ border-radius: 6px 6px 0 0; line-height: var(--line-h); border-bottom: 0.5px solid #000; }}
    .leaf-back {{ transform: rotateX(-180deg); border-radius: 0 0 6px 6px; line-height: 0px; background: linear-gradient(to top, #222 50%, #151515 100%); }}

    .flipping .leaf {{ transform: rotateX(-180deg); }}
    .hinge {{ position: absolute; top: 50%; left: 0; width: 100%; height: 2px; background: #000; z-index: 15; transform: translateY(-50%); }}

    .banksy-art {{
        position: absolute; bottom: -200px; right: 0; width: 140px; height: 210px;
        background-image: url("data:image/png;base64,{img_base64}");
        background-size: contain; background-repeat: no-repeat; z-index: -1;
    }}
</style>
</head>
<body>
    <div class="board-case">
        <div id="row-msg" class="row-container"></div>
        <div id="row-date" class="row-container" style="margin-top:15px; opacity: 0.7;"></div>
        <div id="row-clock" class="row-container" style="opacity: 0.7;"></div>
        <div id="banksy" class="banksy-art"></div>
    </div>

<script>
    const fullText = "{input_text}";
    const flapCount = Math.min(10, fullText.length <= 20 ? Math.floor(fullText.length / 2) : 10);
    let prevMsg = "".padEnd(flapCount, ' ').split('');
    let prevDate = "        ".split('');
    let prevTimeStr = "     ".split('');
    
    let msgPages = [];
    for (let i = 0; i < fullText.length; i += flapCount) {{
        msgPages.push(fullText.substring(i, i + flapCount).padEnd(flapCount, ' ').split(''));
    }}

    function updateCard(elId, newVal, oldVal) {{
        if (newVal === oldVal) return;
        const el = document.getElementById(elId);
        if (!el) return;

        // 完全依照您的 clock1219.py 邏輯：重新寫入整個 HTML 並觸發 reflow
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
        void el.offsetWidth; // 強制重繪
        el.classList.add('flipping');
    }}

    function adjustSize() {{
        const vw = window.innerWidth;
        const msgW = Math.min(85, Math.floor((vw * 0.9) / flapCount));
        document.documentElement.style.setProperty('--msg-w', msgW + 'px');
        document.documentElement.style.setProperty('--line-h', (msgW * 1.5) + 'px');
        const smallW = Math.floor(msgW * 0.55);
        document.documentElement.style.setProperty('--small-w', smallW + 'px');
    }}

    function init() {{
        adjustSize();
        let msgHtml = '';
        for (let i=0; i<flapCount; i++) msgHtml += `<div class="flip-card msg-unit" id="m${{i}}"></div>`;
        document.getElementById('row-msg').innerHTML = msgHtml;

        let dateHtml = '';
        for (let i=0; i<8; i++) dateHtml += `<div class="flip-card small-unit" id="d${{i}}"></div>`;
        document.getElementById('row-date').innerHTML = dateHtml;

        let clockHtml = '';
        for (let i=0; i<5; i++) clockHtml += `<div class="flip-card small-unit" id="t${{i}}"></div>`;
        document.getElementById('row-clock').innerHTML = clockHtml;
    }}

    function tick() {{
        const n = new Date();
        const dStr = (["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"][n.getMonth()] + String(n.getDate()).padStart(2,'0') + " " + ["日","一","二","三","四","五","六"][n.getDay()]).padEnd(8, ' ');
        const tStr = String(n.getHours()).padStart(2,'0') + ":" + String(n.getMinutes()).padStart(2,'0');
        
        for (let i=0; i<8; i++) {{
            updateCard(`d${{i}}`, dStr[i], prevDate[i]);
            prevDate[i] = dStr[i];
        }}
        for (let i=0; i<5; i++) {{
            updateCard(`t${{i}}`, tStr[i], prevTimeStr[i]);
            prevTimeStr[i] = tStr[i];
        }}
    }}

    let pIdx = 0;
    function cycleMsg() {{
        pIdx = (pIdx + 1) % msgPages.length;
        const currentPage = msgPages[pIdx];
        currentPage.forEach((char, i) => {{
            setTimeout(() => {{
                updateCard(`m${{i}}`, char, prevMsg[i]);
                prevMsg[i] = char;
            }}, i * 100);
        }});
    }}

    window.onload = () => {{
        init();
        tick();
        // 初始訊息顯示
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

components.html(html_code, height=900, scrolling=False)
