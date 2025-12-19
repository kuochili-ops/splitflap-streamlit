import streamlit as st
import streamlit.components.v1 as components

# --- 1. 頁面透明化與基礎設定 ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: transparent !important;}
    .stApp {background-color: transparent !important;}
    iframe { border: none; width: 100%; height: 100vh; overflow: hidden; background-color: transparent !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 參數獲取 ---
input_text_raw = st.query_params.get("text", "載入中...")
stay_sec = float(st.query_params.get("stay", 2.5))
bg_param = st.query_params.get("bg", "transparent")

if bg_param != "transparent" and not bg_param.startswith("#"):
    if len(bg_param) in [3, 6]: bg_param = f"#{bg_param}"

# --- 3. 核心 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    :root {{
        --font-family: "PingFang TC", "Microsoft JhengHei", "Noto Sans TC", sans-serif;
        --flip-speed: 0.6s;
        --card-bg: linear-gradient(180deg, #333 0%, #111 50%, #000 51%, #222 100%);
    }}
    
    body {{ 
        transition: background-color 0.8s ease;
        background-color: {bg_param};
        background-image: url("https://www.transparenttextures.com/patterns/concrete-wall.png");
        display: flex; flex-direction: column; justify-content: center; align-items: center; 
        height: 100vh; margin: 0; overflow: hidden; cursor: pointer;
    }}

    /* 透明外框：尺寸視翻板區域決定 */
    .board-case {{
        position: relative; padding: 35px 30px;
        background: rgba(0, 0, 0, 0.4); border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 30px 60px rgba(0,0,0,0.8);
        backdrop-filter: blur(10px);
        display: inline-flex; flex-direction: column; align-items: center;
        max-width: 95vw;
    }}

    .screw {{
        position: absolute; width: 10px; height: 10px;
        background: radial-gradient(circle at 3px 3px, #888, #111);
        border-radius: 50%; box-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }}

    /* 翻板容器樣式 */
    .row-container {{
        display: grid; 
        grid-template-columns: repeat(var(--cols), var(--unit-width)); 
        gap: 8px; perspective: 1500px;
    }}
    
    #message-rows {{ display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px; }}
    #clock-row {{ margin-top: 10px; }}

    .flap-unit {{ 
        position: relative; background: #000; border-radius: 4px; 
        font-family: var(--font-family); font-weight: 900; color: #fff; 
    }}

    /* 尺寸調整 */
    .msg-unit {{ --unit-width: var(--msg-w, 40px); --unit-height: calc(var(--unit-width) * 1.4); font-size: calc(var(--unit-width) * 0.9); }}
    .clk-unit {{ --unit-width: 24px; --unit-height: 34px; font-size: 18px; }}

    .flap-unit {{ width: var(--unit-width); height: var(--unit-height); }}

    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; 
        overflow: hidden; background: var(--card-bg); 
        display: flex; justify-content: center; backface-visibility: hidden; 
    }}
    
    .top {{ top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 0.5px solid #000; }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; }}

    .text {{ position: absolute; left: 0; width: 100%; height: var(--unit-height); text-align: center; line-height: var(--unit-height); }}
    .top .text {{ top: 0; }}
    .bottom .text {{ bottom: 0; }}

    .leaf {{ 
        position: absolute; top: 0; left: 0; width: 100%; height: 50%; 
        z-index: 15; transform-origin: bottom; 
        transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); 
        transform-style: preserve-3d; 
    }}
    .leaf-front {{ z-index: 16; background: var(--card-bg); border-radius: 4px 4px 0 0; }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #111; display: flex; justify-content: center; align-items: flex-end; overflow: hidden; border-radius: 0 0 4px 4px; }}
    .flipping {{ transform: rotateX(-180deg); }}

    .flap-unit::before {{ 
        content: ""; position: absolute; top: 50%; left: 0; 
        width: 100%; height: 1.5px; background: rgba(0,0,0,0.8); 
        transform: translateY(-50%); z-index: 60; 
    }}

    .footer-note {{ 
        margin-top: 20px; font-family: var(--font-family); font-size: 12px; 
        color: rgba(255, 255, 255, 0.3); letter-spacing: 1px; text-align: center;
    }}
</style>
</head>
<body onclick="changeStyle()">
    <div class="board-case">
        <div class="screw" style="top:12px; left:12px;"></div>
        <div class="screw" style="top:12px; right:12px;"></div>
        
        <div id="message-rows"></div>
        
        <div id="clock-row" class="row-container"></div>
        
        <div class="screw" style="bottom:12px; left:12px;"></div>
        <div class="screw" style="bottom:12px; right:12px;"></div>
    </div>
    
    <div class="footer-note">👋 點擊牆面切換風格 | 𓃥白六訊息告示牌</div>

<script>
    const styles = [
        {{ c: '#1a1a1a', t: 'carbon-fibre' }},
        {{ c: '#888888', t: 'concrete-wall' }},
        {{ c: '#1a2a3a', t: 'stardust' }},
        {{ c: 'transparent', t: 'none' }}
    ];
    let sIdx = 0;
    function changeStyle() {{
        sIdx = (sIdx + 1) % styles.length;
        document.body.style.backgroundColor = styles[sIdx].c;
        document.body.style.backgroundImage = styles[sIdx].t === 'none' ? 'none' : `url("https://www.transparenttextures.com/patterns/${{styles[sIdx].t}}.png")`;
    }}

    function createFlap(char, typeClass) {{
        return `
            <div class="flap-unit ${{typeClass}}">
                <div class="half top base-top"><div class="text">${{char}}</div></div>
                <div class="half bottom base-bottom"><div class="text">${{char}}</div></div>
                <div class="leaf">
                    <div class="half top leaf-front"><div class="text">${{char}}</div></div>
                    <div class="half bottom leaf-back"><div class="text">${{char}}</div></div>
                </div>
            </div>`;
    }}

    function updateFlap(unit, newChar) {{
        if (unit.querySelector('.base-top .text').innerText === newChar) return;
        const leaf = unit.querySelector('.leaf');
        unit.querySelector('.leaf-back .text').innerText = newChar;
        leaf.classList.add('flipping');
        setTimeout(() => {{
            unit.querySelectorAll('.base-top .text, .base-bottom .text').forEach(t => t.innerText = newChar);
        }}, 300);
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
    
    // 計算翻板數：字元數/2，最多10個
    const flapCount = Math.min(10, Math.max(1, Math.floor(cleanText.length / 2)));
    let msgPages = [];
    for (let i = 0; i < cleanText.length; i += (flapCount * 2)) {{
        let chunk = cleanText.substring(i, i + (flapCount * 2)).padEnd(flapCount * 2, ' ');
        msgPages.push([
            chunk.substring(0, flapCount).split(''),
            chunk.substring(flapCount, flapCount * 2).split('')
        ]);
    }}

    function init() {{
        const msgContainer = document.getElementById('message-rows');
        const clockContainer = document.getElementById('clock-row');
        
        // 初始化訊息列
        msgContainer.innerHTML = `
            <div id="row-1" class="row-container" style="--cols: ${{flapCount}}"></div>
            <div id="row-2" class="row-container" style="--cols: ${{flapCount}}"></div>
        `;
        document.getElementById('row-1').innerHTML = msgPages[0][0].map(c => createFlap(c, 'msg-unit')).join('');
        document.getElementById('row-2').innerHTML = msgPages[0][1].map(c => createFlap(c, 'msg-unit')).join('');
        
        // 適配主訊息寬度
        const w = Math.min(50, Math.max(30, Math.floor((window.innerWidth - 100) / flapCount)));
        document.documentElement.style.setProperty('--msg-w', w + 'px');

        // 初始化時鐘列 (11格)
        clockContainer.style.setProperty('--cols', 11);
        clockContainer.innerHTML = getTime().split('').map(c => createFlap(c, 'clk-unit')).join('');
    }}

    function getTime() {{
        const n = new Date();
        const m = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"][n.getMonth()];
        const d = String(n.getDate()).padStart(2,'0');
        const w = ["日","一","二","三","四","五","六"][n.getDay()];
        return `${{m}}${{d}} ${{w}}${{String(n.getHours()).padStart(2,'0')}}:${{String(n.getMinutes()).padStart(2,'0')}}`;
    }}

    let pIdx = 0;
    window.onload = () => {{
        init();
        if (msgPages.length > 1) setInterval(() => {{
            pIdx = (pIdx + 1) % msgPages.length;
            const units1 = document.querySelectorAll('#row-1 .flap-unit');
            const units2 = document.querySelectorAll('#row-2 .flap-unit');
            units1.forEach((u, i) => setTimeout(() => updateFlap(u, msgPages[pIdx][0][i]), i*40));
            units2.forEach((u, i) => setTimeout(() => updateFlap(u, msgPages[pIdx][1][i]), (i + flapCount)*40));
        }}, {stay_sec} * 1000);
        
        setInterval(() => {{
            const s = getTime();
            document.querySelectorAll('#clock-row .flap-unit').forEach((u, i) => updateFlap(u, s[i]));
        }}, 1000);
    }};
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=False)
