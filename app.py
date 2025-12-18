import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: transparent !important;}
    .stApp {background: #000 !important;}
    iframe {border: none; width: 100%; height: 100vh; overflow: hidden;}
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
        --font-family: "PingFang TC", "Microsoft JhengHei", sans-serif;
        --card-bg: linear-gradient(180deg, #3a3a3a 0%, #1a1a1a 50%, #000 51%, #222 100%);
    }}
    body {{ 
        background: #000; display: flex; flex-direction: column; justify-content: center; 
        align-items: center; min-height: 100vh; margin: 0; padding: 15px; box-sizing: border-box; 
    }}
    #board-container {{ 
        display: grid; 
        grid-template-columns: repeat(var(--cols, 8), var(--unit-width, 40px)); 
        gap: 6px; 
        perspective: 1000px;
        justify-content: center;
    }}
    .flap-unit {{ 
        position: relative; 
        width: var(--unit-width, 40px); 
        height: calc(var(--unit-width, 40px) * 1.4); 
        background: #000; border-radius: 4px; 
        font-family: var(--font-family); 
        font-size: calc(var(--unit-width, 40px) * 0.95); 
        font-weight: 900; color: #fff; 
        box-shadow: 0 5px 15px rgba(0,0,0,0.8);
    }}
    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center; 
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }}
    .top {{ top: 0; height: 50%; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 0.5px solid #000; }}
    .bottom {{ bottom: 0; height: 50%; align-items: flex-end; border-radius: 0 0 4px 4px; background: linear-gradient(180deg, #111 0%, #000 100%); }}
    .text {{ height: calc(var(--unit-width, 40px) * 1.4); width: 100%; text-align: center; position: absolute; line-height: calc(var(--unit-width, 40px) * 1.4); }}
    .leaf {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 15; transform-origin: bottom; transition: transform 0.6s; transform-style: preserve-3d; }}
    .leaf-front {{ z-index: 16; background: var(--card-bg); border-radius: 4px 4px 0 0; }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #111; display: flex; justify-content: center; align-items: flex-end; overflow: hidden; border-radius: 0 0 4px 4px; }}
    .flipping {{ transform: rotateX(-180deg); }}
    .flap-unit::before {{ content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 1px; background: #000; transform: translateY(-50%); z-index: 60; }}

    .footer-note {{ margin-top: 40px; font-family: var(--font-family); font-size: 13px; color: rgba(255, 255, 255, 0.3); letter-spacing: 2px; }}
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
    
    // 🚀 新增：自動換行邏輯 (超過 10 個字自動切分)
    function wrapText(text, limit = 10) {{
        let result = [];
        let parts = text.includes('，') || text.includes(',') ? text.replace(/，/g, ',').split(',') : [text];
        
        parts.forEach(p => {{
            let str = p.trim();
            for (let i = 0; i < str.length; i += limit) {{
                result.push(str.substring(i, i + limit));
            }}
        }});
        return result;
    }}

    const lines = wrapText(rawText);
    const maxCols = Math.max(...lines.map(l => l.length));

    function adjustSize() {{
        const winW = window.innerWidth - 40;
        // 確保至少能塞進 maxCols 個字，寬度計算加入 gap
        const calculatedW = Math.floor((winW - (6 * (maxCols - 1))) / maxCols);
        // 設定合理區間，寬度不再任由字數無限縮小
        const finalUnitW = Math.max(30, Math.min(80, calculatedW));
        
        document.documentElement.style.setProperty('--cols', maxCols);
        document.documentElement.style.setProperty('--unit-width', finalUnitW + 'px');
    }}

    // 因為現在是一次錄製多行展示，我們將所有文字組成一個大的 Grid
    function renderBoard() {{
        const container = document.getElementById('board-container');
        container.innerHTML = lines.map(line => {{
            return line.padEnd(maxCols, ' ').split('').map(c => `
                <div class="flap-unit">
                    <div class="half top"><div class="text">${{c}}</div></div>
                    <div class="half bottom"><div class="text">${{c}}</div></div>
                    <div class="leaf">
                        <div class="half top leaf-front"><div class="text">${{c}}</div></div>
                        <div class="half bottom leaf-back"><div class="text">${{c}}</div></div>
                    </div>
                </div>`).join('');
        }}).join('');
    }}

    window.onload = () => {{
        adjustSize();
        renderBoard();
    }};
    window.onresize = adjustSize;
</script>
</body>
</html>
"""

components.html(html_code, height=1000)
