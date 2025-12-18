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

# --- 2. 獲取原始參數 ---
input_text_raw = st.query_params.get("text", "載入中...")
stay_sec = float(st.query_params.get("stay", 2.5))

# --- 3. 核心 HTML 與解碼器 ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    /* 使用系統內建字體組合，避免 Google Fonts 加載失敗 */
    :root {{
        --font-family: "PingFang TC", "Microsoft JhengHei", sans-serif;
        --flip-speed: 0.6s;
        --card-bg: linear-gradient(180deg, #3a3a3a 0%, #1a1a1a 50%, #000 51%, #222 100%);
    }}
    body {{ 
        background: transparent; display: flex; justify-content: center; 
        align-items: center; height: 100vh; margin: 0; overflow: hidden; 
    }}
    #board-container {{ 
        display: grid; 
        grid-template-columns: repeat(var(--cols, 8), var(--unit-width, 70px)); 
        gap: 12px; perspective: 2000px; 
    }}
    .flap-unit {{ 
        position: relative; width: var(--unit-width, 70px); height: calc(var(--unit-width, 70px) * 1.5); 
        background: #000; border-radius: 8px; 
        font-family: var(--font-family); font-size: calc(var(--unit-width, 70px) * 1.1); 
        font-weight: 900; color: #fff; 
        box-shadow: 0 15px 35px rgba(0,0,0,0.8), 0 5px 15px rgba(0,0,0,0.5);
    }}
    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center; 
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }}
    .top {{ 
        top: 0; height: calc(50% + 1px); align-items: flex-start; 
        border-radius: 8px 8px 0 0; border-bottom: 1px solid rgba(0,0,0,0.85);
        box-shadow: inset 0 2px 4px rgba(255,255,255,0.12);
    }}
    .bottom {{ 
        bottom: 0; height: 50%; align-items: flex-end; 
        border-radius: 0 0 8px 8px; 
        background: linear-gradient(180deg, #151515 0%, #000 100%);
    }}
    .text {{ 
        height: calc(var(--unit-width, 70px) * 1.5); width: 100%; 
        text-align: center; position: absolute; left: 0; 
        line-height: calc(var(--unit-width, 70px) * 1.5);
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
    .flap-unit::before {{ 
        content: ""; position: absolute; top: 50%; left: 0; 
        width: 100%; height: 2.5px; background: rgba(0,0,0,0.95); 
        transform: translateY(-50%); z-index: 60; 
    }}
</style>
</head>
<body>
<div id="board-container"></div>
<script>
    // 🏆 超強力解碼器：將 &#...; 或 % 符號強行轉回中文字
    function ultimateDecode(str) {{
        let d = str;
        try {{ d = decodeURIComponent(d.replace(/\\+/g, ' ')); }} catch(e) {{}}
        const textarea = document.createElement('textarea');
        textarea.innerHTML = d;
        d = textarea.value;
        // 二次還原預防
        textarea.innerHTML = d;
        return textarea.value;
    }}

    const cleanText = ultimateDecode("{input_text_raw}");
    let rowsData = [];
    let maxCols = 1;

    // 分割文字
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
    
    // 動態佈局
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
