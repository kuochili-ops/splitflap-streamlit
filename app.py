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
        border: none; width: 100%; height: 100vh; overflow: hidden;
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 參數獲取 ---
input_text_raw = st.query_params.get("text", "載入中...")
stay_sec = float(st.query_params.get("stay", 2.5))
bg_param = st.query_params.get("bg", "transparent")

if bg_param != "transparent" and not bg_param.startswith("#"):
    if len(bg_param) in [3, 6]:
        bg_param = f"#{bg_param}"

# --- 3. 核心 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    :root {{
        --font-family: "PingFang TC", "Microsoft JhengHei", "Noto Sans TC", sans-serif;
        --flip-speed: 0.6s;
        --card-bg: linear-gradient(180deg, #3a3a3a 0%, #1a1a1a 50%, #000 51%, #222 100%);
    }}
    
    body {{ 
        transition: background-color 0.8s ease;
        background-color: {bg_param};
        background-image: url("https://www.transparenttextures.com/patterns/concrete-wall.png");
        display: flex; flex-direction: column; justify-content: center; 
        align-items: center; height: 100vh; margin: 0; padding: 20px;
        box-sizing: border-box; overflow: hidden; cursor: pointer;
    }}

    /* 告示牌外殼 - 最小寬度由時間翻板決定 */
    .board-case {{
        position: relative;
        padding: 30px 40px;
        background: rgba(0, 0, 0, 0.25);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 20px 50px rgba(0,0,0,0.6);
        backdrop-filter: blur(4px);
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 450px; /* 確保時間翻板有足夠空間 */
    }}

    /* 螺絲 */
    .board-case::before, .board-case::after, 
    .screw-bottom-left, .screw-bottom-right {{
        content: ""; position: absolute; width: 10px; height: 10px;
        background: radial-gradient(circle at 3px 3px, #999, #333);
        border-radius: 50%; box-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }}
    .board-case::before {{ top: 12px; left: 12px; }}
    .board-case::after {{ top: 12px; right: 12px; }}
    .screw-bottom-left {{ bottom: 12px; left: 12px; }}
    .screw-bottom-right {{ bottom: 12px; right: 12px; }}

    /* 主訊息容器 */
    #board-container {{ 
        display: grid; 
        grid-template-columns: repeat(var(--cols, 8), var(--unit-width, 40px)); 
        gap: 8px; perspective: 1500px; 
        margin-bottom: 25px;
    }}

    /* 時間容器 */
    #clock-container {{
        display: grid;
        grid-template-columns: repeat(12, 28px); /* 固定 12 格小翻板 */
        gap: 4px;
        perspective: 1000px;
    }}

    /* 翻板單位樣式 (通用) */
    .flap-unit {{ 
        position: relative; 
        background: #000; border-radius: 4px; font-family: var(--font-family); 
        font-weight: 900; color: #fff; 
    }}

    /* 主訊息翻板大小 */
    #board-container .flap-unit {{
        width: var(--unit-width, 40px);
        height: calc(var(--unit-width, 40px) * 1.4);
        font-size: calc(var(--unit-width, 40px) * 1.0);
    }}

    /* 時間小翻板大小 */
    #clock-container .flap-unit {{
        width: 28px;
        height: 40px;
        font-size: 20px;
    }}

    .half {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: var(--card-bg); display: flex; justify-content: center; backface-visibility: hidden; }}
    .top {{ top: 0; height: calc(50% + 0.5px); align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.8); }}
    .bottom {{ bottom: 0; height: 50%; align-items: flex-end; border-radius: 0 0 4px 4px; background: linear-gradient(180deg, #151515 0%, #000 100%); }}
    .text {{ height: 100%; width: 100%; text-align: center; position: absolute; }}
    
    /* 修正文字垂直居中 */
    #board-container .text {{ line-height: calc(var(--unit-width, 40px) * 1.4); }}
    #clock-container .text {{ line-height: 40px; }}

    .leaf {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 15; transform-origin: bottom; transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }}
    .leaf-front {{ z-index: 16; background: var(--card-bg); border-radius: 4px 4px 0 0; }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #111; display: flex; justify-content: center; align-items: flex-end; overflow: hidden; border-radius: 0 0 4px 4px; }}
    .flipping {{ transform: rotateX(-180deg); }}
    .flap-unit::before {{ content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 1.5px; background: rgba(0,0,0,0.9); transform: translateY(-50%); z-index: 60; }}

    .footer-note {{ margin-top: 25px; font-family: var(--font-family); font-size: 14px; color: rgba(255, 255, 255, 0.4); letter-spacing: 2px; }}
</style>
</head>
<body onclick="changeStyle()">
    <div class="board-case">
        <div id="board-container"></div>
        
        <div id="clock-container"></div>

        <div class="screw-bottom-left"></div>
        <div class="screw-bottom-right"></div>
    </div>
    <div class="footer-note">👋 點擊牆面切換風格 | 𓃥白六訊息告示牌</div>

<script>
    // --- 風格切換 ---
    const styles = [
        {{ name: '工業灰', color: '#888888', tex: 'concrete-wall' }},
        {{ name: '深夜黑', color: '#1a1a1a', tex: 'carbon-fibre' }},
        {{ name: '普魯士藍', color: '#1a2a3a', tex: 'stardust' }},
        {{ name: '復古紅磚', color: '#6d2e2e', tex: 'brick-wall' }},
        {{ name: '全透明', color: 'transparent', tex: 'none' }}
    ];
    let currentStyleIdx = 0;
    function changeStyle() {{
        currentStyleIdx = (currentStyleIdx + 1) % styles.length;
        const s = styles[currentStyleIdx];
        document.body.style.backgroundColor = s.color;
        document.body.style.backgroundImage = s.tex === 'none' ? 'none' : `url("https://www.transparenttextures.com/patterns/${{s.tex}}.png")`;
    }}

    // --- 核心翻牌組件 ---
    function createFlapHTML(char) {{
        return `
            <div class="flap-unit">
                <div class="half top base-top"><div class="text">${{char}}</div></div>
                <div class="half bottom base-bottom"><div class="text">${{char}}</div></div>
                <div class="leaf">
                    <div class="half top leaf-front"><div class="text">${{char}}</div></div>
                    <div class="half bottom leaf-back"><div class="text">${{char}}</div></div>
                </div>
            </div>`;
    }}

    function updateFlap(unit, newChar) {{
        const currentText = unit.querySelector('.base-top .text').innerText;
        if (currentText === newChar) return;

        const leaf = unit.querySelector('.leaf');
        unit.querySelector('.leaf-back .text').innerText = newChar;
        leaf.classList.add('flipping');

        setTimeout(() => {{
            unit.querySelector('.base-top .text').innerText = newChar;
            unit.querySelector('.base-bottom .text').innerText = newChar;
        }}, 300);

        leaf.addEventListener('transitionend', () => {{
            unit.querySelector('.leaf-front .text').innerText = newChar;
            leaf.style.transition = 'none';
            leaf.classList.remove('flipping');
            leaf.offsetHeight;
            leaf.style.transition = '';
        }}, {{once: true}});
    }}

    // --- 主訊息邏輯 ---
    const cleanText = (str => {{
        let d = str; try {{ d = decodeURIComponent(d.replace(/\\+/g, ' ')); }} catch(e) {{}}
        const t = document.createElement('textarea'); t.innerHTML = d; return t.value;
    }})("{input_text_raw}");
    
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

    function initMainBoard() {{
        const container = document.getElementById('board-container');
        container.innerHTML = rowsData[0].map(c => createFlapHTML(c)).join('');
        document.documentElement.style.setProperty('--cols', maxCols);
        const winW = window.innerWidth - 120;
        const finalUnitW = Math.max(25, Math.min(80, Math.floor((winW - (8 * (maxCols - 1))) / maxCols)));
        document.documentElement.style.setProperty('--unit-width', finalUnitW + 'px');
    }}

    let currentRow = 0;
    function cycleMainBoard() {{
        if (rowsData.length <= 1) return;
        currentRow = (currentRow + 1) % rowsData.length;
        const nextChars = rowsData[currentRow];
        const units = document.querySelectorAll('#board-container .flap-unit');
        units.forEach((u, i) => setTimeout(() => updateFlap(u, nextChars[i] || ' '), i * 50));
    }}

    // --- 時間邏輯 ---
    function getTimeString() {{
        const now = new Date();
        const months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
        const month = months[now.getMonth()];
        const day = String(now.getDate()).padStart(2, '0');
        const hh = String(now.getHours()).padStart(2, '0');
        const mm = String(now.getMinutes()).padStart(2, '0');
        return `${{month}}/${{day}} ${{hh}}:${{mm}}`; // 正好 12 個字元
    }}

    function initClock() {{
        const clockContainer = document.getElementById('clock-container');
        const timeStr = getTimeString();
        clockContainer.innerHTML = timeStr.split('').map(c => createFlapHTML(c)).join('');
    }}

    function updateClock() {{
        const timeStr = getTimeString();
        const units = document.querySelectorAll('#clock-container .flap-unit');
        timeStr.split('').forEach((char, i) => updateFlap(units[i], char));
    }}

    window.onload = () => {{
        initMainBoard();
        initClock();
        if (rowsData.length > 1) setInterval(cycleMainBoard, {stay_sec} * 1000);
        setInterval(updateClock, 1000);
    }};
</script>
</body>
</html>
"""

components.html(html_code, height=800, scrolling=False)
