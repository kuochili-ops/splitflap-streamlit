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
input_text_raw = st.query_params.get("text", "HELLO")
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
        display: flex; justify-content: center; align-items: center; 
        height: 100vh; margin: 0; overflow: hidden; cursor: pointer;
    }}

    .board-case {{
        position: relative; padding: 50px 60px;
        background: rgba(0, 0, 0, 0.4); border-radius: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 40px 80px rgba(0,0,0,0.8);
        backdrop-filter: blur(10px);
        display: flex; flex-direction: column; align-items: center;
        min-width: 520px;
    }}

    .screw {{
        position: absolute; width: 12px; height: 12px;
        background: radial-gradient(circle at 4px 4px, #888, #111);
        border-radius: 50%; box-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }}

    /* 主訊息 */
    #board-container {{ 
        display: grid; grid-template-columns: repeat(var(--cols, 8), var(--unit-width, 60px)); 
        gap: 12px; perspective: 1500px; margin-bottom: 40px;
    }}

    /* 時間訊息 */
    #clock-container {{
        display: grid; grid-template-columns: repeat(12, 32px); 
        gap: 6px; perspective: 1000px;
    }}

    .flap-unit {{ 
        position: relative; background: #000; border-radius: 6px; 
        font-family: var(--font-family); font-weight: 900; color: #fff; 
    }}

    /* 翻板尺寸定義 */
    #board-container .flap-unit {{ --w: var(--unit-width, 60px); --h: calc(var(--w) * 1.4); }}
    #clock-container .flap-unit {{ --w: 32px; --h: 46px; font-size: 24px; }}
    #board-container .flap-unit {{ font-size: calc(var(--w) * 0.9); }}

    .flap-unit {{ width: var(--w); height: var(--h); }}

    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; 
        overflow: hidden; background: var(--card-bg); 
        display: flex; justify-content: center; backface-visibility: hidden; 
    }}
    
    .top {{ top: 0; align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 0.5px solid #000; }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 6px 6px; }}

    /* 【核心修正】精確鎖定文字位置 */
    .text {{ 
        position: absolute; left: 0; width: 100%; height: var(--h);
        text-align: center; line-height: var(--h);
    }}
    .top .text {{ top: 0; }}
    .bottom .text {{ bottom: 0; }}

    .leaf {{ 
        position: absolute; top: 0; left: 0; width: 100%; height: 50%; 
        z-index: 15; transform-origin: bottom; 
        transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); 
        transform-style: preserve-3d; 
    }}
    .leaf-front {{ z-index: 16; background: var(--card-bg); border-radius: 6px 6px 0 0; }} 
    .leaf-back {{ 
        transform: rotateX(-180deg); z-index: 15; background: #111; 
        display: flex; justify-content: center; align-items: flex-end; 
        overflow: hidden; border-radius: 0 0 6px 6px; 
    }}
    .flipping {{ transform: rotateX(-180deg); }}
    .flap-unit::before {{ 
        content: ""; position: absolute; top: 50%; left: 0; 
        width: 100%; height: 2px; background: rgba(0,0,0,0.8); 
        transform: translateY(-50%); z-index: 60; 
    }}

    .footer-note {{ margin-top: 30px; font-family: var(--font-family); font-size: 14px; color: rgba(255, 255, 255, 0.3); letter-spacing: 2px; }}
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
    <div class="footer-note">👋 點擊切換風格 | 𓃥白六訊息告示牌</div>

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

    function createFlap(char) {{
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
    
    let rows = [];
    let mCols = 1;
    if (cleanText.includes('，') || cleanText.includes(',')) {{
        const p = cleanText.replace(/，/g, ',').split(',');
        mCols = Math.max(...p.map(x => x.trim().length));
        rows = p.map(x => x.trim().padEnd(mCols, ' ').split(''));
    }} else {{
        mCols = Math.min(Math.ceil(cleanText.length / 2) || 1, 10);
        for (let i = 0; i < cleanText.length; i += mCols) rows.push(cleanText.substring(i, i+mCols).padEnd(mCols, ' ').split(''));
    }}

    function init() {{
        document.getElementById('board-container').innerHTML = rows[0].map(c => createFlap(c)).join('');
        document.documentElement.style.setProperty('--cols', mCols);
        const w = Math.min(80, Math.max(30, Math.floor((window.innerWidth - 200) / mCols)));
        document.documentElement.style.setProperty('--unit-width', w + 'px');
        document.getElementById('clock-container').innerHTML = getTime().split('').map(c => createFlap(c)).join('');
    }}

    function getTime() {{
        const n = new Date();
        const m = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"][n.getMonth()];
        return `${{m}}/${{String(n.getDate()).padStart(2,'0')}} ${{String(n.getHours()).padStart(2,'0')}}:${{String(n.getMinutes()).padStart(2,'0')}}`;
    }}

    let rIdx = 0;
    window.onload = () => {{
        init();
        if (rows.length > 1) setInterval(() => {{
            rIdx = (rIdx + 1) % rows.length;
            document.querySelectorAll('#board-container .flap-unit').forEach((u, i) => setTimeout(() => updateFlap(u, rows[rIdx][i] || ' '), i*50));
        }}, {stay_sec} * 1000);
        setInterval(() => {{
            const s = getTime();
            document.querySelectorAll('#clock-container .flap-unit').forEach((u, i) => updateFlap(u, s[i]));
        }}, 1000);
    }};
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=False)
