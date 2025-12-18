import streamlit as st
import streamlit.components.v1 as components

# --- 1. 頁面配置 ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: transparent !important;}
    .stApp {background: #000 !important;}
    iframe {border: none; width: 100%; height: 100vh; overflow: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 參數獲取 ---
input_text_raw = st.query_params.get("text", "歡迎光臨,白六告示牌,依序輪播中")
stay_sec = float(st.query_params.get("stay", 3.0))

# --- 3. 核心輪播看板 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    :root {{
        --font-family: "PingFang TC", "Microsoft JhengHei", sans-serif;
        --card-bg: linear-gradient(180deg, #3a3a3a 0%, #1a1a1a 50%, #000 51%, #222 100%);
    }}
    body {{ 
        background: #000; display: flex; flex-direction: column; justify-content: center; 
        align-items: center; height: 100vh; margin: 0; padding: 10px; box-sizing: border-box; 
        overflow: hidden;
    }}
    #board-container {{ 
        display: grid; 
        grid-template-columns: repeat(var(--cols, 10), var(--unit-width, 35px)); 
        gap: 6px; 
        perspective: 1000px;
    }}
    .flap-unit {{ 
        position: relative; 
        width: var(--unit-width, 35px); 
        height: calc(var(--unit-width, 35px) * 1.4); 
        background: #000; border-radius: 4px; 
        font-family: var(--font-family); 
        font-size: calc(var(--unit-width, 35px) * 1.0); 
        font-weight: 900; color: #fff; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.8);
    }}
    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center; 
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }}
    .top {{ top: 0; height: calc(50% + 0.5px); align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 0.5px solid #000; }}
    .bottom {{ bottom: 0; height: 50%; align-items: flex-end; border-radius: 0 0 4px 4px; background: linear-gradient(180deg, #111 0%, #000 100%); }}
    .text {{ height: calc(var(--unit-width, 35px) * 1.4); width: 100%; text-align: center; position: absolute; line-height: calc(var(--unit-width, 35px) * 1.4); }}
    
    .leaf {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 15; transform-origin: bottom; transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }}
    .leaf-front {{ z-index: 16; background: var(--card-bg); border-radius: 4px 4px 0 0; }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #111; display: flex; justify-content: center; align-items: flex-end; overflow: hidden; border-radius: 0 0 4px 4px; }}
    .flipping {{ transform: rotateX(-180deg); }}
    
    .flap-unit::before {{ content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 1.5px; background: #000; transform: translateY(-50%); z-index: 60; }}

    .footer-note {{ margin-top: 50px; font-family: var(--font-family); font-size: 14px; color: rgba(255, 255, 255, 0.3); letter-spacing: 2px; }}
</style>
</head>
<body>
    <div id="board-container"></div>
    <div class="footer-note">𓃥白六訊息告示牌</div>

<script>
    function ultimateDecode(str) {{
        let d = str;
        try {{ d = decodeURIComponent(d.replace(/\\+/g, ' ')); }} catch(e) {{}}
        const textarea = document.createElement('textarea');
        textarea.innerHTML = d;
        return textarea.value;
    }}

    const rawText = ultimateDecode("{input_text_raw}");
    // 解析訊息：用逗號隔開，每段強制截斷為 10 個字
    const messages = rawText.replace(/，/g, ',').split(',').map(m => m.trim().substring(0, 10));
    
    // 計算最大字數作為看板寬度基準（最多10個字）
    const maxCols = Math.max(...messages.map(m => m.length));
    let currentIndex = 0;

    function adjustSize() {{
        const winW = window.innerWidth - 40;
        const calculatedW = Math.floor((winW - (6 * (maxCols - 1))) / maxCols);
        const finalUnitW = Math.max(30, Math.min(85, calculatedW));
        document.documentElement.style.setProperty('--cols', maxCols);
        document.documentElement.style.setProperty('--unit-width', finalUnitW + 'px');
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

    function flipToNext() {{
        if (messages.length <= 1) return;
        
        const nextIndex = (currentIndex + 1) % messages.length;
        const nextText = messages[nextIndex].padEnd(maxCols, ' ');
        const units = document.querySelectorAll('.flap-unit');
        
        nextText.split('').forEach((char, i) => {{
            const u = units[i];
            if (!u) return;

            // 如果字元沒變就不翻轉
            if (u.querySelector('.base-top .text').innerText === char) return;

            setTimeout(() => {{
                const leaf = u.querySelector('.leaf');
                u.querySelector('.leaf-back .text').innerText = char;
                leaf.classList.add('flipping');
                
                setTimeout(() => {{
                    u.querySelector('.base-top .text').innerText = char;
                    u.querySelector('.base-bottom .text').innerText = char;
                }}, 300);

                leaf.addEventListener('transitionend', () => {{
                    u.querySelector('.leaf-front .text').innerText = char;
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    leaf.offsetHeight; // 強制重繪
                    leaf.style.transition = '';
                }}, {{once: true}});
            }}, i * 50);
        }});
        
        currentIndex = nextIndex;
    }}

    window.onload = () => {{
        adjustSize();
        const container = document.getElementById('board-container');
        container.innerHTML = messages[0].padEnd(maxCols, ' ').split('').map(c => createFlapHTML(c)).join('');
        
        if (messages.length > 1) {{
            setInterval(flipToNext, {stay_sec} * 1000);
        }}
    }};
    window.onresize = adjustSize;
</script>
</body>
</html>
"""

components.html(html_code, height=800)
