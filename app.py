import streamlit as st
import streamlit.components.v1 as components

# --- 1. 頁面透明化設定 ---
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
input_text_raw = st.query_params.get("text", "WELCOME")
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

    .board-case {{
        position: relative; padding: 35px 45px;
        background: rgba(0, 0, 0, 0.45); border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 30px 60px rgba(0,0,0,0.8);
        backdrop-filter: blur(10px);
        display: inline-flex; flex-direction: column; align-items: center;
        max-width: 98vw;
        gap: 12px;
    }}

    .screw {{
        position: absolute; width: 10px; height: 10px;
        background: radial-gradient(circle at 3px 3px, #888, #111);
        border-radius: 50%; box-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }}

    .row-container {{
        display: flex; flex-direction: row; gap: 6px; 
        perspective: 1000px; justify-content: center;
    }}
    
    .flap-unit {{ position: relative; background: #000; border-radius: 4px; color: #fff; font-weight: 900; }}

    /* 第一排：大尺寸訊息 */
    .msg-unit {{ 
        --unit-w: var(--msg-w, 60px); --unit-h: calc(var(--unit-w) * 1.4); 
        width: var(--unit-w); height: var(--unit-h); font-size: calc(var(--unit-w) * 0.9); 
    }}

    /* 第二、三排：小尺寸翻板 */
    .small-unit {{ 
        --unit-w: 22px; --unit-h: 32px; 
        width: var(--unit-w); height: var(--unit-h); font-size: 16px; 
    }}

    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; 
        overflow: hidden; background: var(--card-bg); 
        display: flex; justify-content: center; backface-visibility: hidden; 
    }}
    
    .top {{ top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 0.5px solid #000; }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; }}

    .text {{ position: absolute; left: 0; width: 100%; text-align: center; }}
    .msg-unit .text {{ height: calc(var(--msg-w) * 1.4); line-height: calc(var(--msg-w) * 1.4); }}
    .small-unit .text {{ height: 32px; line-height: 32px; }}
    
    .top .text {{ top: 0; }}
    .bottom .text {{ bottom: 0; }}

    .leaf {{ 
        position: absolute; top: 0; left: 0; width: 100%; height: 50%; 
        z-index: 15; transform-origin: bottom; transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); 
        transform-style: preserve-3d; 
    }}
    .leaf-front {{ z-index: 16; background: var(--card-bg); border-radius: 4px 4px 0 0; }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #111; display: flex; justify-content: center; align-items: flex-end; overflow: hidden; border-radius: 0 0 4px 4px; }}
    .flipping {{ transform: rotateX(-180deg); }}

    .flap-unit::before {{ content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 1.5px; background: rgba(0,0,0,0.8); transform: translateY(-50%); z-index: 60; }}

    .footer-note {{ margin-top: 20px; font-family: var(--font-family); font-size: 11px; color: rgba(255, 255, 255, 0.3); letter-spacing: 1px; }}
</style>
</head>
<body onclick="changeStyle()">
    <div class="board-case">
        <div class="screw" style="top:12px; left:12px;"></div>
        <div class="screw" style="top:12px; right:12px;"></div>
        
        <div id="row-msg" class="row-container"></div>
        <div id="row-date" class="row-container"></div>
        <div id="row-clock" class="row-container"></div>
        
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

    function createFlap(char, type) {{
        return `
            <div class="flap-unit ${{type}}">
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
    
    // 關鍵修正：翻板數 = 字數 / 2 (最多 10 個)
    const flapCount = Math.min(10, Math.max(1, Math.floor(cleanText.length / 2)));
    let msgPages = [];
    for (let i = 0; i < cleanText.length; i += flapCount) {{
        msgPages.push(cleanText.substring(i, i + flapCount).padEnd(flapCount, ' ').split(''));
    }}

    function init() {{
        const msgRow = document.getElementById('row-msg');
        const dateRow = document.getElementById('row-date');
        const clockRow = document.getElementById('row-clock');
        
        msgRow.innerHTML = msgPages[0].map(c => createFlap(c, 'msg-unit')).join('');
        const w = Math.min(65, Math.max(35, Math.floor((window.innerWidth - 120) / flapCount)));
        document.documentElement.style.setProperty('--msg-w', w + 'px');

        dateRow.innerHTML = getDateString().split('').map(c => createFlap(c, 'small-unit')).join('');
        clockRow.innerHTML = getTimeString().split('').map(c => createFlap(c, 'small-unit')).join('');
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
        // 移除秒數，僅顯示 HH:mm
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
            const dStr = getDateString();
            const tStr = getTimeString();
            document.querySelectorAll('#row-date .flap-unit').forEach((u, i) => updateFlap(u, dStr[i]));
            document.querySelectorAll('#row-clock .flap-unit').forEach((u, i) => updateFlap(u, tStr[i]));
        }}, 1000);
    }};
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=False)
