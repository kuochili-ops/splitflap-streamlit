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
stay_sec = float(st.query_params.get("stay", 2.5))

# --- 4. 核心 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {{
        --flip-speed: 0.65s;
        --bg-color: #222;
        --text-color: #f0f0f0;
    }}
    body {{ 
        background-color: #f0f0f0;
        background-image: url("https://www.transparenttextures.com/patterns/white-wall.png");
        display: flex; flex-direction: column; align-items: center; 
        height: 100vh; margin: 0; overflow: hidden; padding-top: 4vh;
        font-family: "PingFang TC", "Microsoft JhengHei", sans-serif;
    }}

    .board-case {{
        position: relative; padding: 25px 30px;
        background: rgba(35, 35, 35, 0.96); 
        border-radius: 20px; box-shadow: 0 30px 60px rgba(0,0,0,0.5);
        display: inline-flex; flex-direction: column; align-items: center;
        gap: 12px; z-index: 10; max-width: 95vw;
    }}

    .row-container {{ display: flex; flex-direction: row; gap: 5px; perspective: 1200px; }}

    /* 物理翻板基礎結構 */
    .flip-card {{
        position: relative;
        background: var(--bg-color);
        border-radius: 6px;
        color: var(--text-color);
        font-weight: bold;
    }}

    /* 訊息列尺寸 (動態計算) */
    .msg-unit {{ 
        width: var(--msg-w); height: calc(var(--msg-w) * 1.5); 
        font-size: calc(var(--msg-w) * 1.1); 
    }}

    /* 日期時間列尺寸 (較小) */
    .small-unit {{ 
        width: var(--small-w); height: calc(var(--small-w) * 1.4); 
        font-size: calc(var(--small-w) * 0.9); 
    }}

    /* 四層物理切片樣式 */
    .top, .bottom {{
        position: absolute; left: 0; width: 100%; height: 50%;
        overflow: hidden; background: var(--bg-color); text-align: center;
    }}
    
    .msg-unit .top {{ top: 0; border-radius: 6px 6px 0 0; line-height: calc(var(--msg-w) * 1.5); border-bottom: 0.5px solid #000; z-index: 1; }}
    .msg-unit .bottom {{ bottom: 0; border-radius: 0 0 6px 6px; line-height: 0px; z-index: 0; }}
    
    .small-unit .top {{ top: 0; border-radius: 4px 4px 0 0; line-height: calc(var(--small-w) * 1.4); border-bottom: 0.5px solid #000; z-index: 1; }}
    .small-unit .bottom {{ bottom: 0; border-radius: 0 0 4px 4px; line-height: 0px; z-index: 0; }}

    /* 翻轉葉片 */
    .leaf {{
        position: absolute; top: 0; left: 0; width: 100%; height: 50%;
        z-index: 10; transform-origin: bottom;
        transform-style: preserve-3d;
        transition: transform var(--flip-speed) cubic-bezier(0.3, 0, 0.2, 1);
    }}

    .leaf-front, .leaf-back {{
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        backface-visibility: hidden; background: var(--bg-color); overflow: hidden; text-align: center;
    }}

    .msg-unit .leaf-front {{ border-radius: 6px 6px 0 0; line-height: calc(var(--msg-w) * 1.5); border-bottom: 0.5px solid #000; }}
    .msg-unit .leaf-back {{ transform: rotateX(-180deg); border-radius: 0 0 6px 6px; line-height: 0px; background: linear-gradient(to top, #222 50%, #181818 100%); }}

    .small-unit .leaf-front {{ border-radius: 4px 4px 0 0; line-height: calc(var(--small-w) * 1.4); border-bottom: 0.5px solid #000; }}
    .small-unit .leaf-back {{ transform: rotateX(-180deg); border-radius: 0 0 4px 4px; line-height: 0px; background: linear-gradient(to top, #222 50%, #181818 100%); }}

    .flipping .leaf {{ transform: rotateX(-180deg); }}
    
    .hinge {{
        position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
        background: #000; z-index: 15; transform: translateY(-50%);
    }}

    .banksy-art {{
        position: absolute; bottom: -200px; right: 0; width: 140px; height: 210px;
        background-image: url("data:image/png;base64,{img_base64}");
        background-size: contain; background-repeat: no-repeat; z-index: -1;
    }}
</style>
</head>
<body>
    <div class="board-case" id="main-board">
        <div id="row-msg" class="row-container"></div>
        <div id="row-date" class="row-container" style="margin-top:10px; opacity: 0.75;"></div>
        <div id="row-clock" class="row-container" style="opacity: 0.75;"></div>
        <div id="banksy" class="banksy-art"></div>
    </div>

<script>
    const fullText = "{input_text}";
    // 浮動板數邏輯：字數 <= 20 則商數 (字數/2)，否則上限 10
    const flapCount = Math.min(10, fullText.length <= 20 ? Math.floor(fullText.length / 2) : 10);
    
    let msgPages = [];
    for (let i = 0; i < fullText.length; i += flapCount) {{
        msgPages.push(fullText.substring(i, i + flapCount).padEnd(flapCount, ' ').split(''));
    }}

    function createCardHTML(char, unitClass) {{
        return `
            <div class="flip-card ${{unitClass}}">
                <div class="top">${{char}}</div>
                <div class="bottom">${{char}}</div>
                <div class="leaf">
                    <div class="leaf-front">${{char}}</div>
                    <div class="leaf-back">${{char}}</div>
                </div>
                <div class="hinge"></div>
            </div>`;
    }}

    function updateCard(el, newVal) {{
        const oldVal = el.querySelector('.top').innerText;
        if (newVal === oldVal) return;

        el.querySelector('.top').innerText = newVal;
        el.querySelector('.leaf-back').innerText = newVal;

        el.classList.remove('flipping');
        void el.offsetWidth;
        el.classList.add('flipping');

        setTimeout(() => {{
            el.querySelector('.bottom').innerText = newVal;
            el.querySelector('.leaf-front').innerText = newVal;
            el.classList.remove('flipping');
        }}, 600);
    }}

    function adjustSize() {{
        const vw = window.innerWidth;
        // 訊息大翻板：手機直式縮小，寬螢幕放大
        const msgW = Math.min(vw < 600 ? 70 : 100, Math.floor((vw * 0.85) / flapCount));
        document.documentElement.style.setProperty('--msg-w', msgW + 'px');
        // 日期時間小翻板：設為大翻板的 0.55 倍
        const smallW = Math.floor(msgW * 0.55);
        document.documentElement.style.setProperty('--small-w', smallW + 'px');
    }}

    function init() {{
        adjustSize();
        document.getElementById('row-msg').innerHTML = msgPages[0].map(c => createCardHTML(c, 'msg-unit')).join('');
        document.getElementById('row-date').innerHTML = "        ".split('').map(c => createCardHTML(c, 'small-unit')).join('');
        document.getElementById('row-clock').innerHTML = "     ".split('').map(c => createCardHTML(c, 'small-unit')).join('');
    }}

    function tick() {{
        const n = new Date();
        const dStr = (["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"][n.getMonth()] + String(n.getDate()).padStart(2,'0') + " " + ["日","一","二","三","四","五","六"][n.getDay()]).padEnd(8, ' ');
        const tStr = String(n.getHours()).padStart(2,'0') + ":" + String(n.getMinutes()).padStart(2,'0');
        
        document.querySelectorAll('#row-date .flip-card').forEach((u, i) => updateCard(u, dStr[i]));
        document.querySelectorAll('#row-clock .flip-card').forEach((u, i) => updateCard(u, tStr[i]));
    }}

    let pIdx = 0;
    window.onload = () => {{
        init();
        tick();
        setInterval(tick, 1000);
        if (msgPages.length > 1) setInterval(() => {{
            pIdx = (pIdx + 1) % msgPages.length;
            document.querySelectorAll('#row-msg .flip-card').forEach((u, i) => {{
                setTimeout(() => updateCard(u, msgPages[pIdx][i]), i * 70);
            }});
        }}, {stay_sec} * 1000);
    }};
    window.onresize = adjustSize;
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=False)
