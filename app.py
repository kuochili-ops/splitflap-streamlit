import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# --- 1. 頁面基礎設定 ---
st.set_page_config(layout="wide", page_title="Mechanical Flip Board")
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

input_text = st.query_params.get("text", "假日愉快 身體健康").upper()
stay_sec = max(3.0, float(st.query_params.get("stay", 4.0)))

# --- 3. 整合 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    :root {{
        --bg-color: #c8c8c8;
        --card-bg: #222222;
        --text-color: #e0e0e0;
        --border-color: #111;
        --anim-speed: 0.6s;
    }}

    body {{ 
        background-color: var(--bg-color); 
        background-image: url("{img_data}");
        background-repeat: no-repeat;
        background-position: right 10% top 45%; 
        background-size: auto 25vh;
        display: flex; justify-content: center; align-items: flex-start; 
        padding-top: 8vh; height: 100vh; margin: 0; overflow: hidden;
        font-family: "Courier New", "Microsoft JhengHei", monospace;
    }}

    .acrylic-board {{
        position: relative; padding: 40px; 
        background: rgba(40, 40, 40, 0.15); 
        backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px; 
        box-shadow: 0 40px 100px rgba(0,0,0,0.4), inset 0 0 2px rgba(255,255,255,0.2);
        display: inline-flex; flex-direction: column; align-items: center;
        gap: 15px; z-index: 10;
    }}

    .row-container {{ display: flex; gap: 6px; perspective: 1000px; }}

    /* 翻板核心結構 */
    .flip-card {{
        position: relative;
        width: var(--w); height: var(--h);
        background: var(--card-bg);
        border-radius: 6px;
        font-size: var(--fs);
        font-weight: 800;
        line-height: var(--h);
        color: var(--text-color);
    }}

    .top, .bottom, .leaf-front, .leaf-back {{
        position: absolute; left: 0; width: 100%; height: 50%;
        overflow: hidden; background: var(--card-bg);
        -webkit-backface-visibility: hidden; backface-visibility: hidden;
        text-align: center;
    }}

    .top, .leaf-front {{
        top: 0; border-radius: 4px 4px 0 0;
        line-height: var(--h); 
        border-bottom: 1px solid rgba(0,0,0,0.5);
    }}

    .bottom, .leaf-back {{
        bottom: 0; border-radius: 0 0 4px 4px;
        line-height: 0; 
    }}

    /* 翻轉葉片 */
    .leaf {{
        position: absolute; top: 0; left: 0; width: 100%; height: 50%;
        z-index: 10; transform-origin: bottom;
        transition: transform var(--anim-speed) cubic-bezier(0.45, 0.05, 0.55, 0.95);
        transform-style: preserve-3d;
    }}

    .leaf-back {{ transform: rotateX(-180deg); }}

    /* 翻轉中的陰影效果 */
    .flipping .leaf-front {{
        animation: shadow-top var(--anim-speed) ease-in forwards;
    }}
    .flipping .leaf-back {{
        animation: shadow-bottom var(--anim-speed) ease-in forwards;
    }}

    @keyframes shadow-top {{
        0% {{ background: var(--card-bg); }}
        50% {{ background: #000; }}
        100% {{ background: #000; }}
    }}
    @keyframes shadow-bottom {{
        0% {{ background: #000; }}
        50% {{ background: #000; }}
        100% {{ background: var(--card-bg); }}
    }}

    .flipping .leaf {{ transform: rotateX(-180deg); }}

    /* 中間的機械橫桿 */
    .hinge {{
        position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
        background: rgba(0,0,0,0.8); z-index: 20; transform: translateY(-50%);
    }}

    /* 尺寸變數 */
    .msg-unit {{ --w: var(--msg-w); --h: calc(var(--msg-w) * 1.4); --fs: calc(var(--msg-w) * 1.1); }}
    .small-unit {{ --w: 32px; --h: 46px; --fs: 28px; }}

</style>
</head>
<body>
    <div class="acrylic-board">
        <div id="row-msg" class="row-container"></div>
        <div id="row-date" class="row-container" style="margin-top: 10px; opacity: 0.8;"></div>
        <div id="row-clock" class="row-container" style="opacity: 0.8;"></div>
    </div>

<script>
    const fullText = "{input_text}";
    // 根據螢幕寬度決定格子數量，最多 12 格
    const flapCount = Math.min(12, Math.floor(window.innerWidth * 0.8 / 70)); 
    let prevMsg = [], prevDate = [], prevTime = [];

    function updateDigit(el, nv, ov) {{
        if (nv === ov && el.innerHTML !== "") return;
        if (!ov) ov = " ";
        if (!nv) nv = " ";

        // 建立翻轉結構
        el.innerHTML = `
            <div class="top">${{nv}}</div>
            <div class="bottom">${{ov}}</div>
            <div class="leaf">
                <div class="leaf-front">${{ov}}</div>
                <div class="leaf-back">${{nv}}</div>
            </div>
            <div class="hinge"></div>
        `;

        el.classList.remove('flipping');
        void el.offsetWidth; // 觸發重繪
        el.classList.add('flipping');
    }}

    function init() {{
        const vw = window.innerWidth;
        const msgW = Math.min(70, Math.floor((vw * 0.9) / flapCount));
        document.documentElement.style.setProperty('--msg-w', msgW + 'px');
        
        document.getElementById('row-msg').innerHTML = Array.from({{length: flapCount}}, (_, i) => `<div class="flip-card msg-unit" id="m${{i}}"></div>`).join('');
        document.getElementById('row-date').innerHTML = Array.from({{length: 10}}, (_, i) => `<div class="flip-card small-unit" id="d${{i}}"></div>`).join('');
        document.getElementById('row-clock').innerHTML = Array.from({{length: 8}}, (_, i) => `<div class="flip-card small-unit" id="t${{i}}"></div>`).join('');
    }}

    function tick() {{
        const n = new Date();
        const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
        const days = ["SUN","MON","TUE","WED","THU","FRI","SAT"];
        
        // 格式化日期: JUN 15 SAT
        const dStr = months[n.getMonth()] + " " + String(n.getDate()).padStart(2,'0') + " " + days[n.getDay()];
        const tStr = String(n.getHours()).padStart(2,'0') + ":" + String(n.getMinutes()).padStart(2,'0') + ":" + String(n.getSeconds()).padStart(2,'0');

        dStr.split('').forEach((c, i) => {{ 
            const el = document.getElementById(`d${{i}}`);
            if(prevDate[i] !== c) {{ updateDigit(el, c, prevDate[i]); prevDate[i] = c; }}
        }});
        tStr.split('').forEach((c, i) => {{ 
            const el = document.getElementById(`t${{i}}`);
            if(prevTime[i] !== c) {{ updateDigit(el, c, prevTime[i]); prevTime[i] = c; }}
        }});
    }}

    window.onload = () => {{
        init();
        
        // 訊息分段處理
        const msgPages = [];
        for (let i = 0; i < fullText.length; i += flapCount) {{
            msgPages.push(fullText.substring(i, i + flapCount).padEnd(flapCount, ' ').split(''));
        }}
        
        // 初始訊息
        msgPages[0].forEach((c, i) => {{ 
            setTimeout(() => {{
                updateDigit(document.getElementById(`m${{i}}`), c, " "); 
                prevMsg[i] = c;
            }}, i * 80); // 階層式延遲
        }});
        
        tick();
        setInterval(tick, 1000);
        
        // 輪播訊息
        if (msgPages.length > 1) {{
            let pageIdx = 0;
            setInterval(() => {{
                pageIdx = (pageIdx + 1) % msgPages.length;
                msgPages[pageIdx].forEach((c, i) => {{ 
                    if(prevMsg[i] !== c) {{
                        setTimeout(() => {{
                            updateDigit(document.getElementById(`m${{i}}`), c, prevMsg[i]); 
                            prevMsg[i] = c;
                        }}, i * 80); // 增加機械感延遲
                    }}
                }});
            }}, {stay_sec} * 1000);
        }}
    }};
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=False)
