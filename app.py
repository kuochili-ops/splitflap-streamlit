import streamlit as st
import streamlit.components.v1 as components
import math

# --- 1. 頁面透明化樣式 ---
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: transparent !important;}
    .stApp {background: transparent !important;}
    iframe {border: none; min-height: 500px; width: 100%;}
    </style>
    """, unsafe_allow_html=True)

input_text_raw = st.query_params.get("text", "訊息載入中")
stay_sec = float(st.query_params.get("stay", 2.5))

# --- 2. 核心 HTML (加入更深層次的光影設計) ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    :root {{
        --font-family: "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif;
        --flip-speed: 0.65s;
        /* 💡 質感漸層：模擬物理翻板的磨砂金屬光澤 */
        --card-bg: linear-gradient(180deg, #444 0%, #222 49%, #050505 50%, #1a1a1a 100%);
    }}
    body {{ 
        background: transparent; display: flex; justify-content: center; 
        align-items: center; height: 100vh; margin: 0; overflow: hidden; 
    }}
    #board-container {{ 
        display: grid; 
        grid-template-columns: repeat(var(--cols, 8), var(--unit-width, 70px)); 
        gap: 12px; perspective: 2500px; 
    }}
    .flap-unit {{ 
        position: relative; width: var(--unit-width, 70px); height: calc(var(--unit-width, 70px) * 1.5); 
        background: #000; border-radius: 8px; 
        font-family: var(--font-family); font-size: calc(var(--unit-width, 70px) * 1.15); 
        font-weight: 900; color: #fff; 
        /* 💡 雙層環境光陰影 */
        box-shadow: 0 20px 40px rgba(0,0,0,0.7), 0 5px 15px rgba(0,0,0,0.4);
    }}
    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center; 
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }}
    .top {{ 
        top: 0; height: calc(50% + 1px); align-items: flex-start; 
        border-radius: 8px 8px 0 0; border-bottom: 1.5px solid rgba(0,0,0,0.9);
        /* 💡 頂部高光線，模擬上方燈光照射邊緣 */
        box-shadow: inset 0 2px 5px rgba(255,255,255,0.15);
    }}
    .bottom {{ 
        bottom: 0; height: 50%; align-items: flex-end; 
        border-radius: 0 0 8px 8px; 
        /* 💡 底部稍微變暗，增加景深感 */
        background: linear-gradient(180deg, #111 0%, #000 100%);
    }}
    .text {{ 
        height: calc(var(--unit-width, 70px) * 1.5); width: 100%; 
        text-align: center; position: absolute; left: 0; 
        line-height: calc(var(--unit-width, 70px) * 1.5);
        /* 💡 文字微弱發光，模擬夜間告示牌效果 */
        text-shadow: 0 0 8px rgba(255,255,255,0.2);
    }}
    .top .text {{ top: 0; }}
    .bottom .text {{ bottom: 0; }}
    .leaf {{ 
        position: absolute; top: 0; left: 0; width: 100%; height: 50%; 
        z-index: 15; transform-origin: bottom; 
        transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); 
        transform-style: preserve-3d; 
    }}
    .leaf-front {{ z-index: 16; background: var(--card-bg); border-radius: 8px 8px 0 0; }} 
    .leaf-back {{ 
        transform: rotateX(-180deg); z-index: 15; background: #111; 
        display: flex; justify-content: center; align-items: flex-end; 
        overflow: hidden; border-radius: 0 0 8px 8px; 
    }}
    .flipping {{ transform: rotateX(-180deg); }}
    /* 💡 轉軸陰影加深，增加物理感 */
    .flap-unit::before {{ 
        content: ""; position: absolute; top: 50%; left: 0; 
        width: 100%; height: 3px; background: rgba(0,0,0,0.95); 
        transform: translateY(-50%); z-index: 60; 
        box-shadow: 0 1px 2px rgba(255,255,255,0.05);
    }}
</style>
</head>
<body>
<div id="board-container"></div>
<script>
    function superDecode(t) {{
        let d = t;
        try {{ d = decodeURIComponent(d.replace(/\\+/g, ' ')); }} catch(e) {{}}
        const tx = document.createElement('textarea');
        tx.innerHTML = d; d = tx.value;
        tx.innerHTML = d; return tx.value;
    }}

    const cleanText = superDecode("{input_text_raw}");
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
    
    const unitW = Math.min(85, Math.floor((window.innerWidth * 0.9) / maxCols));
    document.documentElement.style.setProperty('--cols', maxCols);
    document.documentElement.style.setProperty('--unit-width', unitW + 'px');

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
        document.getElementById('board-container').innerHTML = createRow(rowsData[0]);
        if (rowsData.length > 1) setInterval(flip, {stay_sec} * 1000);
    }};
</script>
</body>
</html>
"""
components.html(html_code, height=500)
