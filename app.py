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

input_text_raw = st.query_params.get("text", "載入中...")
stay_sec = float(st.query_params.get("stay", 2.5))

html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gif.js@0.2.0/dist/gif.js"></script>
<style>
    :root {{
        --font-family: "PingFang TC", "Microsoft JhengHei", sans-serif;
        --card-bg: linear-gradient(180deg, #3a3a3a 0%, #1a1a1a 50%, #000 51%, #222 100%);
    }}
    body {{ background: transparent; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
    #board-wrap {{ padding: 20px; background: #000; border-radius: 12px; }}
    #board-container {{ display: grid; grid-template-columns: repeat(var(--cols, 8), var(--unit-width, 40px)); gap: 6px; }}
    .flap-unit {{ position: relative; width: var(--unit-width, 40px); height: calc(var(--unit-width, 40px) * 1.4); background: #000; border-radius: 4px; font-family: var(--font-family); font-size: calc(var(--unit-width, 40px) * 1.1); font-weight: 900; color: #fff; box-shadow: 0 8px 20px rgba(0,0,0,0.7); }}
    .half {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: var(--card-bg); display: flex; justify-content: center; backface-visibility: hidden; }}
    .top {{ top: 0; height: calc(50% + 0.5px); align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.8); }}
    .bottom {{ bottom: 0; height: 50%; align-items: flex-end; border-radius: 0 0 4px 4px; background: linear-gradient(180deg, #151515 0%, #000 100%); }}
    .text {{ height: calc(var(--unit-width, 40px) * 1.4); width: 100%; text-align: center; position: absolute; line-height: calc(var(--unit-width, 40px) * 1.4); }}
    .leaf {{ position: absolute; top: 0; width: 100%; height: 50%; z-index: 15; transform-origin: bottom; transition: transform 0.6s; transform-style: preserve-3d; }}
    .leaf-front {{ z-index: 16; background: var(--card-bg); border-radius: 4px 4px 0 0; }}
    .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #111; display: flex; justify-content: center; align-items: flex-end; overflow: hidden; border-radius: 0 0 4px 4px; }}
    .flipping {{ transform: rotateX(-180deg); }}
    
    .footer-note {{ margin-top: 15px; font-family: var(--font-family); font-size: 14px; color: rgba(255, 255, 255, 0.4); }}
    #download-btn {{ margin-top: 20px; padding: 10px 25px; background: #222; border: 1px solid #444; color: #fff; border-radius: 20px; cursor: pointer; }}
    #progress-container {{ display: none; margin-top: 15px; width: 200px; height: 10px; background: #333; border-radius: 5px; overflow: hidden; }}
    #progress-bar {{ width: 0%; height: 100%; background: #00ffcc; transition: width 0.3s; }}
    #status-text {{ margin-top: 8px; font-size: 12px; color: #00ffcc; font-family: sans-serif; }}
</style>
</head>
<body>
    <div id="board-wrap"><div id="board-container"></div></div>
    <div class="footer-note">𓃥白六訊息告示牌</div>
    <button id="download-btn">🎬 生成 GIF 影片</button>
    <div id="progress-container"><div id="progress-bar"></div></div>
    <div id="status-text"></div>

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

    // 解析文字邏輯
    const parts = cleanText.includes('，') || cleanText.includes(',') ? cleanText.replace(/，/g, ',').split(',') : [cleanText];
    if(parts.length > 1) {{
        maxCols = Math.max(...parts.map(p => p.trim().length));
        rowsData = parts.map(p => p.trim().padEnd(maxCols, ' ').split(''));
    }} else {{
        maxCols = Math.min(Math.ceil(cleanText.length / 2) || 1, 10);
        for (let i = 0; i < cleanText.length; i += maxCols) {{
            rowsData.push(cleanText.substring(i, i + maxCols).padEnd(maxCols, ' ').split(''));
        }}
    }}

    function adjustSize() {{
        const winW = window.innerWidth - 60;
        const finalUnitW = Math.max(25, Math.min(80, Math.floor((winW - (6 * (maxCols - 1))) / maxCols)));
        document.documentElement.style.setProperty('--cols', maxCols);
        document.documentElement.style.setProperty('--unit-width', finalUnitW + 'px');
    }}

    const btn = document.getElementById('download-btn');
    const pBar = document.getElementById('progress-bar');
    const pCont = document.getElementById('progress-container');
    const sText = document.getElementById('status-text');

    btn.onclick = async function() {{
        btn.disabled = true;
        pCont.style.display = 'block';
        pBar.style.width = "5%";
        sText.innerText = "準備中...";

        // 🚀 關鍵修復：不使用外部 Worker 避免跨網域靜止問題
        const gif = new GIF({{
            workers: 0, // 設為 0 使用主線程，雖然慢一點但絕對不會卡住
            quality: 20, // 降低一點品質以提升速度
            width: document.getElementById('board-wrap').offsetWidth,
            height: document.getElementById('board-wrap').offsetHeight
        }});

        // 1. 錄製階段
        for(let i=1; i <= 12; i++) {{
            try {{
                const canvas = await html2canvas(document.getElementById('board-wrap'), {{ 
                    backgroundColor: '#000',
                    scale: 1 // 降低倍率減少運算負擔
                }});
                gif.addFrame(canvas, {{delay: 150, copy: true}});
                pBar.style.width = (i / 12 * 60) + "%"; 
                sText.innerText = "錄製畫面: " + i + "/12";
                if(i === 4) flip(); // 翻轉觸發
                await new Promise(r => setTimeout(r, 100));
            }} catch(err) {{
                console.error("截圖失敗", err);
            }}
        }}

        // 2. 渲染階段
        sText.innerText = "合成中，請稍候...";
        gif.on('finished', function(blob) {{
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = '白六告示牌.gif';
            a.click();
            sText.innerText = "✅ 下載完成！";
            btn.disabled = false;
            setTimeout(() => {{ pCont.style.display = 'none'; sText.innerText = ""; }}, 3000);
        }});

        gif.render();
    }};

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
            }}, i * 30);
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
</script>
</body>
</html>
"""
components.html(html_code, height=650)
