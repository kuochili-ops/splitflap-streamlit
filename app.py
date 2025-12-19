import streamlit as st
import streamlit.components.v1 as components

# --- 1. 頁面透明化設定 ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: transparent !important;}
    .stApp {background-color: transparent !important;}
    iframe {
        border: none; 
        width: 100%; 
        height: 100vh; 
        overflow: hidden;
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 參數獲取 ---
input_text_raw = st.query_params.get("text", "載入中...")
stay_sec = float(st.query_params.get("stay", 2.5))
bg_param = st.query_params.get("bg", "transparent")

# 自動補齊 Hex 色碼
if bg_param != "transparent" and not bg_param.startswith("#"):
    if len(bg_param) in [3, 6]:
        bg_param = f"#{bg_param}"

# --- 3. 核心 HTML ---
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
        --card-bg: linear-gradient(180deg, #3a3a3a 0%, #1a1a1a 50%, #000 51%, #222 100%);
        --main-bg: {bg_param};
    }}
    body {{ 
        background-color: var(--main-bg);
        background-image: url("https://www.transparenttextures.com/patterns/concrete-wall.png");
        display: flex; flex-direction: column; justify-content: center; 
        align-items: center; height: 100vh; margin: 0; padding: 20px;
        box-sizing: border-box; overflow: hidden; 
    }}

    /* 告示牌外殼 */
    .board-case {{
        position: relative;
        padding: 30px 40px;
        background: rgba(0, 0, 0, 0.15); /* 半透明外框 */
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 
            0 20px 50px rgba(0,0,0,0.5), /* 外部大陰影 */
            inset 0 0 15px rgba(255,255,255,0.05); /* 內部邊緣光 */
        backdrop-filter: blur(2px); /* 輕微磨砂效果 */
    }}

    /* 模擬螺絲細節 */
    .board-case::before, .board-case::after, 
    .screw-bottom-left, .screw-bottom-right {{
        content: "";
        position: absolute;
        width: 10px; height: 10px;
        background: radial-gradient(circle at 3px 3px, #999, #333);
        border-radius: 50%;
        box-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }}
    .board-case::before {{ top: 10px; left: 10px; }} /* 左上 */
    .board-case::after {{ top: 10px; right: 10px; }} /* 右上 */
    .screw-bottom-left {{ bottom: 10px; left: 10px; }}
    .screw-bottom-right {{ bottom: 10px; right: 10px; }}

    #board-container {{ 
        display: grid; 
        grid-template-columns: repeat(var(--cols, 8), var(--unit-width, 40px)); 
        gap: 8px; /* 稍微增加間距更有工業感 */
        perspective: 1500px; 
    }}

    .flap-unit {{ 
        position: relative; 
        width: var(--unit-width, 40px); 
        height: calc(var(--unit-width, 40px) * 1.4); 
        background: #000; border-radius: 4px; 
        font-family: var(--font-family); 
        font-size: calc(var(--unit-width, 40px) * 1.0); 
        font-weight: 900; color: #fff; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.8);
    }}

    /* 翻牌結構與動畫相關 (與之前相同) */
    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center; 
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }}
    .top {{ top: 0; height: calc(50% + 0.5px); align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.8); }}
    .bottom {{ bottom: 0; height: 50%; align-items: flex-end; border-radius: 0 0 4px 4px; background: linear-gradient(180deg, #151515 0%, #000 100%); }}
    .text {{ height: calc(var(--unit-width, 40px) * 1.4); width: 100%; text-align: center; position: absolute; left: 0; line-height: calc(var(--unit-width, 40px) * 1.4); }}
    .leaf {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 15; transform-origin: bottom; transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }}
    .leaf-front {{ z-index: 16; background: var(--card-bg); border-radius: 4px 4px 0 0; }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #111; display: flex; justify-content: center; align-items: flex-end; overflow: hidden; border-radius: 0 0 4px 4px; }}
    .flipping {{ transform: rotateX(-180deg); }}
    .flap-unit::before {{ content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 1.5px; background: rgba(0,0,0,0.9); transform: translateY(-50%); z-index: 60; }}

    .footer-note {{
        margin-top: 25px;
        font-family: var(--font-family);
        font-size: 14px;
        color: rgba(255, 255, 255, 0.4);
        letter-spacing: 2px;
    }}
</style>
</head>
<body>
    <div class="board-case">
        <div id="board-container"></div>
        <div class="screw-bottom-left"></div>
        <div class="screw-bottom-right"></div>
    </div>
    
    <div class="footer-note">𓃥白六訊息告示牌</div>

<script>
    function ultimateDecode(str) {{
        let d = str;
        try {{ d = decodeURIComponent(d.replace(/\\+/g, ' ')); }} catch(e) {{}}
        const textarea = document.createElement('textarea');
        textarea.innerHTML = d;
        d = textarea.value;
        return d;
    }}

    const cleanText = ultimateDecode("{input_text_raw}");
    let rowsData = [];
    let maxCols = 1;

    if (cleanText.includes('，') || cleanText.includes(',')) {{
        const parts = cleanText.replace(/，/g, ',').split(',');
        maxCols = Math.max(...parts.map(p => p.trim().length));
        rowsData = parts.map(p => p.trim().padEnd(maxCols, ' ').split(''));
    }} else {{
        maxCols = Math.min(Math.ceil(cleanText.length / 2) || 1, 10);
        for (let i = 0; i < cleanText.length; i += maxCols) {{
            rowsData.push(cleanText.substring(i, i + maxCols).padEnd(maxCols, ' ').split(''));
        }}
    }}

    function adjustSize() {{
        const winW = window.innerWidth - 120; // 考慮到外殼的 padding
        const calculatedW = Math.floor((winW - (8 * (maxCols - 1))) / maxCols);
        const finalUnitW = Math.max(25, Math.min(80, calculatedW));
        document.documentElement.style.setProperty('--cols', maxCols);
        document.documentElement.style.setProperty('--unit-width', finalUnitW + 'px');
    }}

    let currentRow = 0, isAnimating = false;

    function createRow(chars) {{
        return chars.map(c => `
            <div class="flap-unit">
                <div class="half top base-top"><div class="text">${{c}}</div></div>
                <div class="half bottom base-bottom"><div class="text">${{c}}</div></div>
                <div class="leaf">
                    <div class="half top leaf-front"><div class="text">${{c}}</div></div>
                    <div class="half bottom leaf-back"><div class="text">${{c}}</div></div>
                </div>
            </div>`).join('');
    }}

    function flip() {{
        if (rowsData.length <= 1 || isAnimating) return;
        isAnimating = true;
        const nextIdx = (currentRow + 1) % rowsData.length;
        const nextChars = rowsData[nextIdx];
        const units = document.querySelectorAll('.flap-unit');

        units.forEach((u, i) => {{
            setTimeout(() => {{
                const leaf = u.querySelector('.leaf');
                u.querySelector('.leaf-back .text').innerText = nextChars[i] || ' ';
                leaf.classList.add('flipping');
                setTimeout(() => {{
                    u.querySelector('.base-top .text').innerText = nextChars[i] || ' ';
                    u.querySelector('.base-bottom .text').innerText = nextChars[i] || ' ';
                }}, 300);
                leaf.addEventListener('transitionend', () => {{
                    u.querySelector('.leaf-front .text').innerText = nextChars[i] || ' ';
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    leaf.offsetHeight; 
                    leaf.style.transition = '';
                    if (i === units.length - 1) isAnimating = false;
                }}, {{once: true}});
            }}, i * 40);
        }});
        currentRow = nextIdx;
    }}

    window.onload = () => {{
        adjustSize();
        document.getElementById('board-container').innerHTML = createRow(rowsData[0]);
        if (rowsData.length > 1) setInterval(flip, {stay_sec} * 1000);
    }};
    window.onresize = adjustSize;
</script>
</body>
</html>
"""

# --- 4. 渲染 ---
components.html(html_code, height=800, scrolling=False)
