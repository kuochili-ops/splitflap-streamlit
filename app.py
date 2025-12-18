import streamlit as st
import streamlit.components.v1 as components
import math

# --- 1. 頁面極簡透明化 ---
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: transparent !important;}
    .stApp {background: transparent !important;}
    iframe {border: none; min-height: 500px; width: 100%;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 取得原始參數 (完全不處理，避免 Python 報錯) ---
input_text_raw = st.query_params.get("text", "訊息載入中")
stay_sec = float(st.query_params.get("stay", 2.5))

# --- 3. 核心 HTML (包含 JS 端的三次強力還原) ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    :root {{
        --flip-speed: 0.6s;
        /* 光照感漸層：模擬金屬翻板的受光面與背光面 */
        --card-bg: linear-gradient(180deg, #3a3a3a 0%, #1a1a1a 50%, #000 51%, #222 100%);
    }}
    body {{ 
        background: transparent; display: flex; justify-content: center; 
        align-items: center; height: 100vh; margin: 0; overflow: hidden; 
    }}
    #board-container {{ 
        display: grid; 
        grid-template-columns: repeat(var(--cols, 8), var(--unit-width, 70px)); 
        gap: 10px; perspective: 2000px; 
    }}
    .flap-unit {{ 
        position: relative; width: var(--unit-width, 70px); height: calc(var(--unit-width, 70px) * 1.5); 
        background: #000; border-radius: 6px; 
        font-family: 'Noto Sans TC', sans-serif; font-size: calc(var(--unit-width, 70px) * 1.05); 
        font-weight: 900; color: #fff; 
        /* 底部環境陰影 */
        box-shadow: 0 10px 30px rgba(0,0,0,0.8), 0 5px 10px rgba(0,0,0,0.5);
    }}
    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center; 
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }}
    .top {{ 
        top: 0; height: calc(50% + 1px); align-items: flex-start; 
        border-radius: 6px 6px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.8);
        box-shadow: inset 0 2px 3px rgba(255,255,255,0.15); /* 頂部受光反光 */
    }}
    .bottom {{ 
        bottom: 0; height: 50%; align-items: flex-end; 
        border-radius: 0 0 6px 6px; 
        background: linear-gradient(180deg, #151515 0%, #000 100%);
    }}
    .text {{ 
        height: calc(var(--unit-width, 70px) * 1.5); width: 100%; 
        text-align: center; position: absolute; left: 0; 
        line-height: calc(var(--unit-width, 70px) * 1.5);
        text-shadow: 0 0 10px rgba(255,255,255,0.1);
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
    /* 中間轉軸陰影線 */
    .flap-unit::before {{ 
        content: ""; position: absolute; top: 50%; left: 0; 
        width: 100%; height: 2px; background: rgba(0,0,0,0.9); 
        transform: translateY(-50%); z-index: 60; 
    }}
</style>
</head>
<body>
<div id="board-container"></div>
<script>
    // 🚀 三次解碼機制：徹底還原 &#24171; 這種亂碼
    function universalDecode(t) {{
        let res = t;
        try {{ res = decodeURIComponent(res.replace(/\\+/g, ' ')); }} catch(e) {{}}
        const txt = document.createElement('textarea');
        txt.innerHTML = res; 
        res = txt.value; // 第一次還原
        txt.innerHTML = res; 
        res = txt.value; // 第二次還原（防雙重轉義）
        return res;
    }}

    const cleanText = universalDecode("{input_text_raw}");
    let rowsData = [];
    let maxCols = 1;

    // 解析文字並計算寬度
    if (cleanText.includes('，') || cleanText.includes(',')) {{
        const parts = cleanText.replace(/，/g, ',').split(',');
        maxCols = Math.min(Math.max(...parts.map(p => p.trim().length)), 10);
        rowsData = parts.map(p => p.trim().padEnd(maxCols, ' ').substring(0, maxCols).split(''));
    }} else {{
        maxCols = Math.min(Math.ceil(cleanText.length / 2) || 1, 10);
        if (cleanText.length <= maxCols) maxCols = cleanText.length || 1;
        for (let i = 0; i < cleanText.length; i += maxCols) {{
            rowsData.push(cleanText.substring(i, i + maxCols).padEnd(maxCols, ' ').split(''));
        }}
    }}

    // 動態計算尺寸
    const unitW = Math.min(80, Math.floor(window.innerWidth * 0.95 / maxCols - 10));
    document.documentElement.style.setProperty('--cols', maxCols);
    document.documentElement.style.setProperty('--unit-width', unitW + 'px');

    let currentRowIndex = 0;
    let isAnimating = false;

    function createRow(contentArray) {{
        return contentArray.map(char => `
            <div class="flap-unit">
                <div class="half top base-top"><div class="text">${{char}}</div></div>
                <div class="half bottom base-bottom"><div class="text">${{char}}</div></div>
                <div class="leaf">
                    <div class="half top leaf-front"><div class="text">${{char}}</div></div>
                    <div class="half bottom leaf-back"><div class="text">${{char}}</div></div>
                </div>
            </div>`).join('');
    }}

    function performFlip() {{
        if (rowsData.length <= 1 || isAnimating) return;
        isAnimating = true;
        const nextRowIndex = (currentRowIndex + 1) % rowsData.length;
        const nextChars = rowsData[nextRowIndex];
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
                leaf.addEventListener('transitionend', function onEnd() {{
                    leaf.removeEventListener('transitionend', onEnd);
                    u.querySelector('.leaf-front .text').innerText = nextChars[i] || ' ';
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    leaf.offsetHeight; 
                    leaf.style.transition = '';
                    if (i === units.length - 1) isAnimating = false;
                }}, {{once: true}});
            }}, i * 40);
        }});
        currentRowIndex = nextRowIndex;
    }}

    window.onload = () => {{
        const container = document.getElementById('board-container');
        container.innerHTML = createRow(rowsData[0]);
        if (rowsData.length > 1) setInterval(performFlip, {stay_sec} * 1000);
    }};
</script>
</body>
</html>
"""

components.html(html_code, height=500)
