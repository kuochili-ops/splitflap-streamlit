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
    iframe { border: none; width: 100%; height: 100vh; overflow: hidden; background-color: transparent !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 圖片處理 (讀取本地圖片並轉為 Base64) ---
img_filename = "banksy-girl-with-balloon-logo-png_seeklogo-621871.png"
img_base64 = ""

if os.path.exists(img_filename):
    with open(img_filename, "rb") as f:
        data = f.read()
        img_base64 = base64.b64encode(data).decode()

# --- 3. 參數獲取 ---
input_text_raw = st.query_params.get("text", "HAPPY HOLIDAY")
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
        --font-family: "PingFang TC", "Microsoft JhengHei", "Noto Sans TC", sans-serif;
        --flip-speed: 0.6s;
        --card-bg: linear-gradient(180deg, #333 0%, #111 50%, #000 51%, #222 100%);
    }}
    body {{ 
        transition: all 0.8s ease;
        background-color: #f0f0f0;
        background-image: url("https://www.transparenttextures.com/patterns/white-wall.png");
        display: flex; flex-direction: column; 
        justify-content: flex-start; 
        align-items: center; 
        height: 100vh; margin: 0; overflow: hidden; cursor: pointer;
        padding-top: 50px;
        box-sizing: border-box;
    }}

    .board-case {{
        position: relative; 
        padding: 30px 40px; /* 縮小內距確保螺絲可見 */
        background: rgba(35, 35, 35, 0.9); 
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 40px 80px rgba(0,0,0,0.7);
        backdrop-filter: blur(10px);
        display: inline-flex; flex-direction: column; align-items: center;
        max-width: 90vw; /* 稍微縮小寬度，給手機留點邊界 */
        gap: 12px;
        z-index: 10;
    }}

    /* 優化：將女孩往右下角移動，避免遮擋面板 */
    .banksy-art {{
        position: absolute;
        bottom: -220px; /* 降低高度 */
        right: -00px;  /* 往右移開 */
        width: 180px;  /* 稍微縮小比例更精確 */
        height: 250px;
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center bottom;
        background-image: url("data:image/png;base64,{img_base64}");
        pointer-events: none;
        z-index: -1;
        opacity: 0.9;
    }}

    .screw {{
        position: absolute; width: 8px; height: 8px;
        background: radial-gradient(circle at 3px 3px, #888, #111);
        border-radius: 50%; box-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }}
    .row-container {{ display: flex; flex-direction: row; gap: 4px; perspective: 1000px; }}
    
    .flap-unit {{ position: relative; background: #000; border-radius: 4px; color: #fff; font-weight: 900; }}
    
    /* 響應式字體與大小控制 */
    .msg-unit {{ --unit-w: var(--msg-w, 60px); --unit-h: calc(var(--unit-w) * 1.4); width: var(--unit-w); height: var(--unit-h); font-size: calc(var(--unit-w) * 0.9); }}
    .small-unit {{ --unit-w: 20px; --unit-h: 30px; width: var(--unit-w); height: var(--unit-h); font-size: 15px; }}
    
    @media (max-width: 600px) {{
        .board-case {{ padding: 25px 30px; }} /* 手機版螺絲位置微調 */
        .banksy-art {{ width: 140px; right: -40px; bottom: -180px; }} /* 手機版縮小圖片 */
    }}

    .half {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: var(--card-bg); display: flex; justify-content: center; backface-visibility: hidden; }}
    .top {{ top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 0.5px solid #000; }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; }}
    .text {{ position: absolute; left: 0; width: 100%; text-align: center; }}
    .msg-unit .text {{ height: calc(var(--msg-w) * 1.4); line-height: calc(var(--msg-w) * 1.4); }}
    .small-unit .text {{ height: 30px; line-height: 30px; }}
    .top .text {{ top: 0; }}
    .bottom .text {{ bottom: 0; }}
    .leaf {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 15; transform-origin: bottom; transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }}
    .leaf-front {{ z-index: 16; background: var(--card-bg); border-radius: 4px 4px 0 0; }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #111; display: flex; justify-content: center; align-items: flex-end; border-radius: 0 0 4px 4px; }}
    .flipping {{ transform: rotateX(-180deg); }}
    .flap-unit::before {{ content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 1px; background: rgba(0,0,0,0.6); transform: translateY(-50%); z-index: 60; }}
    .footer-note {{ margin-top: 240px; font-family: var(--font-family); font-size: 10px; color: rgba(0, 0, 0, 0.4); font-weight: bold; }}
</style>
</head>
<body onclick="changeStyle()">
    <div class="board-case">
        <div class="screw" style="top:10px; left:10px;"></div>
        <div class="screw" style="top:10px; right:10px;"></div>
        <div id="row-msg" class="row-container"></div>
        <div id="row-date" class="row-container"></div>
        <div id="row-clock" class="row-container"></div>
        <div class="screw" style="bottom:10px; left:10px;"></div>
        <div class="screw" style="bottom:10px; right:10px;"></div>
        <div id="banksy" class="banksy-art"></div>
    </div>
    <div class="footer-note">🎨 CLICK TO SWITCH STYLE | 𓃥白六製作</div>

<script>
    const styles = [
        {{ c: '#f0f0f0', t: 'white-wall', g: true }},
        {{ c: '#333333', t: 'concrete-wall', g: false }},
        {{ c: '#1a1a1a', t: 'carbon-fibre', g: false }}
    ];
    let sIdx = 0;
    function changeStyle() {{
        sIdx = (sIdx + 1) % styles.length;
        const s = styles[sIdx];
        document.body.style.backgroundColor = s.c;
        document.body.style.backgroundImage = s.t === 'none' ? 'none' : `url("https://www.transparenttextures.com/patterns/${{s.t}}.png")`;
        document.getElementById('banksy').style.display = s.g ? 'block' : 'none';
        document.querySelector('.footer-note').style.color = (s.c !== '#f0f0f0') ? 'rgba(255,255,255,0.4)' : 'rgba(0,0,0,0.4)';
    }}

    function createFlap(char, type) {{
        return `<div class="flap-unit ${{type}}"><div class="half top base-top"><div class="text">${{char}}</div></div><div class="half bottom base-bottom"><div class="text">${{char}}</div></div><div class="leaf"><div class="half top leaf-front"><div class="text">${{char}}</div></div><div class="half bottom leaf-back"><div class="text">${{char}}</div></div></div></div>`;
    }}

    function updateFlap(unit, newChar) {{
        if (unit.querySelector('.base-top .text').innerText === newChar) return;
        const leaf = unit.querySelector('.leaf');
        unit.querySelector('.leaf-back .text').innerText = newChar;
        leaf.classList.add('flipping');
        setTimeout(() => {{ unit.querySelectorAll('.base-top .text, .base-bottom .text').forEach(t => t.innerText = newChar); }}, 300);
        leaf.addEventListener('transitionend', () => {{
            unit.querySelector('.leaf-front .text').innerText = newChar;
            leaf.style.transition = 'none'; leaf.classList.remove('flipping');
            leaf.offsetHeight; leaf.style.transition = '';
        }}, {{once: true}});
    }}

    const cleanText = (str => {{
        let d = str; try {{ d = decodeURIComponent(d.replace(/\\+/g, ' ')); }} catch(e) {{}}
        const t = document.createElement('textarea'); t.innerHTML = d; return t.value;
    }})("{input_text_raw}");

    const flapCount = Math.min(10, Math.max(1, Math.floor(cleanText.length / 2)));
    let msgPages = [];
    for (let i = 0; i < cleanText.length; i += flapCount) {{
        msgPages.push(cleanText.substring(i, i + flapCount).padEnd(flapCount, ' ').split(''));
    }}

    function init() {{
        const msgRow = document.getElementById('row-msg');
        msgRow.innerHTML = msgPages[0].map(c => createFlap(c, 'msg-unit')).join('');
        const w = Math.min(65, Math.max(30, Math.floor((window.innerWidth - 80) / flapCount)));
        document.documentElement.style.setProperty('--msg-w', w + 'px');
        document.getElementById('row-date').innerHTML = getDateString().split('').map(c => createFlap(c, 'small-unit')).join('');
        document.getElementById('row-clock').innerHTML = getTimeString().split('').map(c => createFlap(c, 'small-unit')).join('');
    }}

    function getDateString() {{
        const n = new Date();
        const m = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"][n.getMonth()];
        const d = String(n.getDate()).padStart(2,'0');
        const w = ["日","一","二","三","四","五","六"][n.getDay()];
        return `${{m}}${{d}} ${{w}}`;
    }}

    function getTimeString() {{
        const n = new Date();
        return `${{String(n.getHours()).padStart(2,'0')}}:${{String(n.getMinutes()).padStart(2,'0')}}`;
    }}

    let pIdx = 0;
    window.onload = () => {{
        init();
        if (msgPages.length > 1) setInterval(() => {{
            pIdx = (pIdx + 1) % msgPages.length;
            document.querySelectorAll('#row-msg .flap-unit').forEach((u, i) => setTimeout(() => updateFlap(u, msgPages[pIdx][i]), i*50));
        }}, {stay_sec} * 1000);
        setInterval(() => {{
            const dStr = getDateString(); const tStr = getTimeString();
            document.querySelectorAll('#row-date .flap-unit').forEach((u, i) => updateFlap(u, dStr[i]));
            document.querySelectorAll('#row-clock .flap-unit').forEach((u, i) => updateFlap(u, tStr[i]));
        }}, 1000);
    }};
</script>
</body>
</html>
"""

components.html(html_code, height=1000, scrolling=False)
