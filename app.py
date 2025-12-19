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

# --- 2. 圖片處理 (班克西) ---
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
    body {{ 
        display: flex; justify-content: center; align-items: flex-start; 
        padding-top: 5vh; height: 100vh; margin: 0; overflow: hidden;
        font-family: "Microsoft JhengHei", "PingFang TC", sans-serif;
        background-color: #1a1a1a;
        cursor: pointer;
    }}
    
    .wall-2 {{ 
        background-color: #d0d0d0; 
        background-image: url("{img_data}");
        background-repeat: no-repeat;
        background-position: right 15% top 42%; 
        background-size: auto 22vh;
    }}

    .acrylic-board {{
        position: relative; padding: 45px 35px; 
        background: rgba(255, 255, 255, 0.02); 
        backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 15px; box-shadow: 0 30px 80px rgba(0,0,0,0.5);
        display: inline-flex; flex-direction: column; align-items: center;
        gap: 12px; z-index: 10; margin-top: 2vh;
    }}

    .flip-card {{
        position: relative;
        background-color: #1a1a1a;
        color: #e0e0e0;
        text-align: center;
        font-weight: 900;
        perspective: 1000px;
    }}

    /* 靜態底板：上半部與下半部 */
    .top, .bottom {{
        position: absolute; left: 0; width: 100%; height: 50%;
        overflow: hidden; background: #1a1a1a;
    }}
    
    /* 修正：上半部文字一開始維持舊字，翻轉完才變新字，或提高葉片層級 */
    .top {{ top: 0; border-radius: 4px 4px 0 0; line-height: var(--h); border-bottom: 1px solid #000; z-index: 1; }}
    .bottom {{ bottom: 0; border-radius: 0 0 4px 4px; line-height: 0px; z-index: 0; }}

    /* 翻轉葉片：必須是最高層級 */
    .leaf {{
        position: absolute; top: 0; left: 0; width: 100%; height: 50%;
        z-index: 20; /* 確保葉片蓋住 top */
        transform-origin: bottom;
        transform-style: preserve-3d;
        transition: transform 1.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .leaf-front, .leaf-back {{
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        backface-visibility: hidden; background: #1a1a1a;
    }}
    .leaf-front {{ z-index: 2; border-radius: 4px 4px 0 0; line-height: var(--h); border-bottom: 1px solid #000; }}
    .leaf-back {{ transform: rotateX(-180deg); border-radius: 0 0 4px 4px; line-height: 0px; border-top: 1px solid #000; }}

    .flipping .leaf {{ transform: rotateX(-180deg); }}

    .hinge {{
        position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
        background: #000; z-index: 30; transform: translateY(-50%);
    }}

    .msg-unit {{ --w: var(--msg-w); --h: calc(var(--msg-w) * 1.5); --fs: calc(var(--msg-w) * 1.1); width: var(--w); height: var(--h); font-size: var(--fs); }}
    .small-unit {{ --w: 30px; --h: 42px; --fs: 26px; width: var(--w); height: var(--h); font-size: var(--fs); }}
    .row-container {{ display: flex; gap: 4px; }}
</style>
</head>
<body class="wall-2">
    <div class="acrylic-board">
        <div id="row-msg" class="row-container"></div>
        <div id="row-date" class="row-container" style="margin-top: 5px;"></div>
        <div id="row-clock" class="row-container"></div>
    </div>

<script>
    const fullText = "{input_text}";
    const flapCount = Math.min(10, Math.floor(fullText.length / 2) || 5);
    let prevMsg = [], prevDate = [], prevTime = [];

    function updateCard(el, nv, ov) {{
        if (nv === ov && el.innerHTML !== "") return;
        
        // 關鍵結構：
        // .top 顯示【新字】
        // .bottom 顯示【舊字】
        // .leaf-front 顯示【舊字】 (翻下去遮住 bottom)
        // .leaf-back 顯示【新字】 (蓋在底下的內容上)
        
        el.innerHTML = `
            <div class="top">${{nv}}</div>
            <div class="bottom">${{ov}}</div>
            <div class="leaf">
                <div class="leaf-front">${{ov}}</div>
                <div class="leaf-back">${{nv}}</div>
            </div>
            <div class="hinge"></div>
        `;
        
        // 為了防止 nv 在 top 處太早露出：
        // 我們讓 .top 在動畫剛開始時維持 visibility: hidden 或者是讓 leaf 擋死它
        // 這裡透過 z-index 確保 leaf 絕對高於 top 即可解決
        
        el.classList.remove('flipping');
        void el.offsetWidth;
        el.classList.add('flipping');

        // 當翻轉完成後，確保底板文字更新一致
        setTimeout(() => {{
            const b = el.querySelector('.bottom');
            if(b) b.innerText = nv;
        }}, 1200);
    }}

    function init() {{
        const vw = window.innerWidth;
        const msgW = Math.min(65, Math.floor((vw * 0.85) / flapCount));
        document.documentElement.style.setProperty('--msg-w', msgW + 'px');
        
        document.getElementById('row-msg').innerHTML = Array.from({{length: flapCount}}, (_, i) => `<div class="flip-card msg-unit" id="m${{i}}"></div>`).join('');
        document.getElementById('row-date').innerHTML = Array.from({{length: 7}}, (_, i) => `<div class="flip-card small-unit" id="d${{i}}"></div>`).join('');
        document.getElementById('row-clock').innerHTML = Array.from({{length: 8}}, (_, i) => `<div class="flip-card small-unit" id="t${{i}}"></div>`).join('');
    }}

    function tick() {{
        const n = new Date();
        const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
        const weeks = ["日","一","二","三","四","五","六"];
        const dStr = months[n.getMonth()] + String(n.getDate()).padStart(2,'0') + " " + weeks[n.getDay()];
        const tStr = String(n.getHours()).padStart(2,'0') + ":" + String(n.getMinutes()).padStart(2,'0') + ":" + String(n.getSeconds()).padStart(2,'0');

        dStr.split('').forEach((c, i) => {{ updateCard(document.getElementById(`d${{i}}`), c, prevDate[i] || ""); prevDate[i] = c; }});
        tStr.split('').forEach((c, i) => {{ updateCard(document.getElementById(`t${{i}}`), c, prevTime[i] || ""); prevTime[i] = c; }});
    }}

    window.onload = () => {{
        init();
        const msgPages = [];
        for (let i = 0; i < fullText.length; i += flapCount) {{
            msgPages.push(fullText.substring(i, i + flapCount).padEnd(flapCount, ' ').split(''));
        }}
        msgPages[0].forEach((c, i) => {{ updateCard(document.getElementById(`m${{i}}`), c, ""); prevMsg[i] = c; }});
        tick();
        setInterval(tick, 1000);
        if (msgPages.length > 1) {{
            setInterval(() => {{
                let pIdx = (Math.floor(Date.now() / ({stay_sec} * 1000))) % msgPages.length;
                msgPages[pIdx].forEach((c, i) => {{ 
                    if(prevMsg[i] !== c) {{
                        updateCard(document.getElementById(`m${{i}}`), c, prevMsg[i]); 
                        prevMsg[i] = c; 
                    }}
                }});
            }}, 1000);
        }}
    }};
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=False)
