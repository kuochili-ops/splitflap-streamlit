import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: transparent !important;}
    .stApp {background: transparent !important;}
    iframe {border: none; width: 100%; height: 100vh;}
    </style>
    """, unsafe_allow_html=True)

input_text_raw = st.query_params.get("text", "聖誕快樂")
stay_sec = float(st.query_params.get("stay", 2.5))

html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    :root {{
        --font-family: "PingFang TC", "Microsoft JhengHei", "Noto Sans TC", sans-serif;
        --card-bg: linear-gradient(180deg, #3a3a3a 0%, #1a1a1a 50%, #000 51%, #222 100%);
    }}
    body {{ 
        background: transparent; display: flex; flex-direction: column; justify-content: center; 
        align-items: center; height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; overflow: hidden; 
    }}
    #board-container {{ 
        display: grid; grid-template-columns: repeat(var(--cols, 8), var(--unit-width, 40px)); 
        gap: 8px; perspective: 1500px; transition: transform 0.5s;
    }}
    .flap-unit {{ 
        position: relative; width: var(--unit-width, 40px); height: calc(var(--unit-width, 40px) * 1.4); 
        background: #000; border-radius: 6px; font-family: var(--font-family); 
        font-size: calc(var(--unit-width, 40px) * 1.05); font-weight: 900; color: #fff; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.8);
    }}
    .half {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: var(--card-bg); display: flex; justify-content: center; backface-visibility: hidden; }}
    .top {{ top: 0; height: calc(50% + 0.5px); align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.85); }}
    .bottom {{ bottom: 0; height: 50%; align-items: flex-end; border-radius: 0 0 6px 6px; background: linear-gradient(180deg, #151515 0%, #000 100%); }}
    .text {{ height: calc(var(--unit-width, 40px) * 1.4); width: 100%; text-align: center; position: absolute; line-height: calc(var(--unit-width, 40px) * 1.4); }}
    .leaf {{ position: absolute; top: 0; width: 100%; height: 50%; z-index: 15; transform-origin: bottom; transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }}
    .leaf-front {{ z-index: 16; background: var(--card-bg); border-radius: 6px 6px 0 0; }}
    .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #111; display: flex; justify-content: center; align-items: flex-end; overflow: hidden; border-radius: 0 0 6px 6px; }}
    .flipping {{ transform: rotateX(-180deg); }}
    .flap-unit::before {{ content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px; background: rgba(0,0,0,0.9); transform: translateY(-50%); z-index: 60; }}
    
    .footer-note {{ margin-top: 25px; font-family: var(--font-family); font-size: 14px; color: rgba(255, 255, 255, 0.4); letter-spacing: 2px; transition: opacity 0.3s; }}
    
    /* 錄影模式按鈕 */
    #ui-layer {{ margin-top: 30px; display: flex; gap: 10px; }}
    .ui-btn {{ padding: 10px 20px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.3); color: #fff; border-radius: 20px; cursor: pointer; font-size: 13px; }}
    .hidden {{ opacity: 0 !important; pointer-events: none; }}
</style>
</head>
<body>
    <div id="board-container"></div>
    <div class="footer-note" id="note">𓃥白六訊息告示牌</div>
    
    <div id="ui-layer">
        <button class="ui-btn" onclick="toggleUI()">進入/退出 錄影純淨模式</button>
    </div>

<script>
    function ultimateDecode(str) {{
        let d = str;
        try {{ d = decodeURIComponent(d.replace(/\\+/g, ' ')); }} catch(e) {{}}
        const textarea = document.createElement('textarea');
        textarea.innerHTML = d;
        return textarea.value;
    }}

    const cleanText = ultimateDecode("{input_text_raw}");
    let rowsData = [];
    let maxCols = 1;

    // 分割邏輯
    const parts = cleanText.includes('，') || cleanText.includes(',') ? cleanText.replace(/，/g, ',').split(',') : [cleanText];
    maxCols = Math.max(...parts.map(p => p.trim().length));
    rowsData = parts.map(p => p.trim().padEnd(maxCols, ' ').split(''));

    function adjustSize() {{
        const winW = window.innerWidth - 60;
        const finalUnitW = Math.max(25, Math.min(80, Math.floor((winW - (8 * (maxCols - 1))) / maxCols)));
        document.documentElement.style.setProperty('--cols', maxCols);
        document.documentElement.style.setProperty('--unit-width', finalUnitW + 'px');
    }}

    function toggleUI() {{
        document.getElementById('ui-layer').classList.toggle('hidden');
        document.getElementById('note').classList.toggle('hidden');
        // 自動放大看板以適合錄影
        const board = document.getElementById('board-container');
        if(document.getElementById('ui-layer').classList.contains('hidden')) {{
            board.style.transform = "scale(1.2)";
        }} else {{
            board.style.transform = "scale(1.0)";
        }}
    }}

    let currentRow = 0;
    function flip() {{
        if (rowsData.length <= 1) return;
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
                }}, {{once: true}});
            }}, i * 40);
        }});
        currentRow = nextIdx;
    }}

    window.onload = () => {{
        adjustSize();
        document.getElementById('board-container').innerHTML = rowsData[0].map(c => `
            <div class="flap-unit">
                <div class="half top base-top"><div class="text">${{c}}</div></div>
                <div class="half bottom base-bottom"><div class="text">${{c}}</div></div>
                <div class="leaf">
                    <div class="half top leaf-front"><div class="text">${{c}}</div></div>
                    <div class="half bottom leaf-back"><div class="text">${{c}}</div></div>
                </div>
            </div>`).join('');
        if (rowsData.length > 1) setInterval(flip, {stay_sec} * 1000);
    }};
    window.onresize = adjustSize;
</script>
</body>
</html>
"""
components.html(html_code, height=650)
