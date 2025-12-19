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

    .board-case {{
        position: relative;
        padding: 40px 50px;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 30px 60px rgba(0,0,0,0.7);
        backdrop-filter: blur(8px);
        display: flex; flex-direction: column; align-items: center;
        min-width: 480px;
    }}

    .screw {{
        position: absolute; width: 12px; height: 12px;
        background: radial-gradient(circle at 4px 4px, #aaa, #222);
        border-radius: 50%; box-shadow: 1px 1px 3px rgba(0,0,0,0.6);
    }}

    /* 主訊息 */
    #board-container {{ 
        display: grid; 
        grid-template-columns: repeat(var(--cols, 8), var(--unit-width, 40px)); 
        gap: 10px; perspective: 1500px; margin-bottom: 35px;
    }}

    /* 時間訊息 */
    #clock-container {{
        display: grid; grid-template-columns: repeat(12, 30px); 
        gap: 5px; perspective: 1000px;
    }}

    .flap-unit {{ 
        position: relative; background: #000; border-radius: 4px; 
        font-family: var(--font-family); font-weight: 900; color: #fff; 
    }}

    /* 主訊息翻板尺寸 */
    #board-container .flap-unit {{
        width: var(--unit-width, 40px);
        height: calc(var(--unit-width, 40px) * 1.5);
        font-size: calc(var(--unit-width, 40px) * 1.1);
    }}

    /* 時間翻板尺寸 */
    #clock-container .flap-unit {{ width: 30px; height: 44px; font-size: 22px; }}

    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; 
        overflow: hidden; background: var(--card-bg); 
        display: flex; justify-content: center; backface-visibility: hidden; 
    }}
    
    .top {{ 
        top: 0; height: 50%; align-items: flex-start; 
        border-radius: 4px 4px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.8); 
    }}
    .bottom {{ 
        bottom: 0; height: 50%; align-items: flex-end; 
        border-radius: 0 0 4px 4px; 
        background: linear-gradient(180deg, #151515 0%, #000 100%); 
    }}

    /* 【關鍵修正】使用相對定位與精確的高度計算來對齊文字 */
    .text {{ 
        position: absolute; left: 0; width: 100%; text-align: center;
    }}

    /* 主訊息文字位置 */
    #board-container .text {{ height: calc(var(--unit-width, 40px) * 1.5); line-height: calc(var(--unit-width, 40px) * 1.5); }}
    #board-container .top .text {{ top: 0; }}
    #board-container .bottom .text {{ bottom: -50%; }}

    /* 時間文字位置 */
    #clock-container .text {{ height: 44px; line-height: 44px; }}
    #clock-container .top .text {{ top: 0; }}
    #clock-container .bottom .text {{ bottom: -50%; }}

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
        <div class="screw" style="top:15px; left:15px;"></div>
        <div class="screw" style="top:15px; right:15px;"></div>
        <div id="board-container"></div>
        <div id="clock-container"></div>
        <div class="screw" style="bottom:15px; left:15px;"></div>
        <div class="screw" style="bottom:15px; right:15px;"></div>
    </div>
    <div class="footer-note">👋 點擊牆面切換風格 | 𓃥白六訊息告示牌</div>

<script>
    const styles = [
        {{ color: '#1a1a1a', tex: 'carbon-fibre' }},
        {{ color: '#888888', tex: 'concrete-wall' }},
        {{ color: '#1a2a3a', tex: 'stardust' }},
        {{ color: '#6d2e2e', tex: 'brick-wall' }},
        {{ color: 'transparent', tex: 'none' }}
    ];
    let currentStyleIdx = 0;
    function changeStyle() {{
        currentStyleIdx = (currentStyleIdx + 1) % styles.length;
        const s = styles[currentStyleIdx];
        document.body.style.backgroundColor = s.color;
        document.body.style.backgroundImage = s.tex === 'none' ? 'none' : `url("https://www.transparenttextures.com/patterns/${{s.tex}}.png")`;
    }}

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
        const baseText = unit.querySelector('.base-top .text');
        if (baseText.innerText === newChar) return;
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
        const winW = window.innerWidth - 150;
        const finalUnitW = Math.max(25, Math.min(80, Math.floor((winW - (10 * (maxCols - 1))) / maxCols)));
        document.documentElement.style.setProperty('--unit-width', finalUnitW + 'px');
    }}

    function cycleMainBoard() {{
        if (rowsData.length <= 1) return;
        currentRow = (currentRow + 1) % rowsData.length;
        const nextChars = rowsData[currentRow];
        document.querySelectorAll('#board-container .flap-unit').forEach((u, i) => setTimeout(() => updateFlap(u, nextChars[i] || ' '), i * 50));
    }}

    function getTimeString() {{
        const now = new Date();
        const months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
        return `${{months[now.getMonth()]}}/${{String(now.getDate()).padStart(2, '0')}} ${{String(now.getHours()).padStart(2, '0')}}:${{String(now.getMinutes()).padStart(2, '0')}}`;
    }}

    let currentRow = 0;
    window.onload = () => {{
        initMainBoard();
        document.getElementById('clock-container').innerHTML = getTimeString().split('').map(c => createFlapHTML(c)).join('');
        if (rowsData.length > 1) setInterval(cycleMainBoard, {stay_sec} * 1000);
        setInterval(() => {{
            const timeStr = getTimeString();
            document.querySelectorAll('#clock-container .flap-unit').forEach((u, i) => updateFlap(u, timeStr[i]));
        }}, 1000);
    }};
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=False)
