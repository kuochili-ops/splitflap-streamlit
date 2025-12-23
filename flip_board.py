import streamlit.components.v1 as components
import base64

def render_flip_board(text, stay_sec=4.0):
    # 使用維基百科的高清原圖網址，確保連結穩定
    bg_img = "https://upload.wikimedia.org/wikipedia/en/2/21/Girl_with_Balloon.jpg"
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {{ box-sizing: border-box; }}
            html, body {{ height: 100%; margin: 0; padding: 0; }}
            
            body {{ 
                background-color: #dcdcdc; 
                /* 強化塗鴉出現的關鍵設定 */
                background-image: url("{bg_img}");
                background-repeat: no-repeat; 
                background-position: center bottom; /* 改為正中央底部 */
                background-size: contain; /* 確保整張圖完整顯示 */
                background-attachment: fixed;
                
                display: flex; 
                justify-content: center; 
                align-items: flex-start; 
                overflow: hidden;
                font-family: "Impact", "Arial Black", "Microsoft JhengHei", sans-serif;
            }}
            
            /* 壓克力面板 */
            .acrylic-board {{
                position: relative; 
                width: 90vw; 
                max-width: 800px;
                margin-top: 5vh; /* 面板往上提，留空間給下方塗鴉 */
                padding: 50px 30px;
                background: rgba(255, 255, 255, 0.1); 
                backdrop-filter: blur(15px);
                -webkit-backdrop-filter: blur(15px);
                border: 1px solid rgba(255, 255, 255, 0.3); 
                border-radius: 15px;
                display: flex; 
                flex-direction: column; 
                align-items: center; 
                gap: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                z-index: 5;
            }}
            
            /* 面板四角螺絲 */
            .screw {{ 
                position: absolute; width: 14px; height: 14px; 
                background: radial-gradient(circle at 30% 30%, #eee, #666); 
                border-radius: 50%; border: 1px solid #444;
                box-shadow: 1px 1px 2px rgba(0,0,0,0.4);
            }}
            .screw::after {{
                content: ''; position: absolute; top: 6px; left: 1px; width: 10px; height: 2px; 
                background: rgba(0,0,0,0.3); transform: rotate(45deg);
            }}
            .s-tl {{ top: 15px; left: 15px; }}
            .s-tr {{ top: 15px; right: 15px; }}
            .s-bl {{ bottom: 15px; left: 15px; }}
            .s-br {{ bottom: 15px; right: 15px; }}

            /* 翻牌容器 */
            .row-container {{ display: flex; gap: 5px; perspective: 1000px; justify-content: center; width: 100%; }}
            .card {{ background: #1a1a1a; border-radius: 4px; position: relative; overflow: hidden; color: white; display: flex; align-items: center; justify-content: center; }}
            .msg-unit {{ width: var(--msg-w); height: calc(var(--msg-w) * 1.4); font-size: calc(var(--msg-w) * 0.85); }}
            .small-unit {{ width: 36px; height: 52px; font-size: 34px; }}
            .separator {{ font-size: 34px; color: #666; font-weight: bold; line-height: 52px; padding: 0 4px; }}
            
            /* 動態翻牌結構 */
            .panel {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; }}
            .top-p {{ top: 0; border-bottom: 1px solid rgba(0,0,0,0.5); align-items: flex-end; }}
            .bottom-p {{ bottom: 0; align-items: flex-start; }}
            .text-node {{ position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 1; }}
            .top-p .text-node {{ bottom: -100%; }} 
            .bottom-p .text-node {{ top: -100%; }}
            .leaf-node {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform 0.3s ease-in; transform-style: preserve-3d; }}
            .leaf-side {{ position: absolute; inset: 0; backface-visibility: hidden; background: #1a1a1a; display: flex; justify-content: center; overflow: hidden; }}
            .side-back {{ transform: rotateX(-180deg); }}
            .flipping .leaf-node {{ transform: rotateX(-180deg); }}
        </style>
    </head>
    <body>
        <div class="acrylic-board">
            <div class="screw s-tl"></div><div class="screw s-tr"></div>
            <div class="screw s-bl"></div><div class="screw s-br"></div>
            
            <div id="row-msg" class="row-container"></div>
            <div id="row-clock" class="row-container"></div>
        </div>

        <audio id="flipSound" src="https://www.soundjay.com/buttons/button-29.mp3" preload="auto"></audio>

    <script>
        const fullText = "{text.upper()}";
        const charPool_AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ ".split('');
        const charPool_CN = [...new Set(fullText.replace(/[A-Z0-9\s]/g, '').split(''))];
        const flipAudio = document.getElementById('flipSound');
        
        let memory = {{}};
        let isBusy = {{}};

        function playFlipSound() {{
            const s = flipAudio.cloneNode();
            s.volume = 0.1;
            s.play().catch(()=>{{}});
        }}

        function performFlip(id, nVal, pVal) {{
            const el = document.getElementById(id);
            if(!el) return;
            playFlipSound();
            const n = (nVal === 0 || nVal === "0") ? "0" : (nVal || "&nbsp;");
            const p = (pVal === 0 || pVal === "0") ? "0" : (pVal || "&nbsp;");
            el.innerHTML = ""; el.classList.remove('flipping');
            el.innerHTML = `<div class="panel top-p"><div class="text-node">${{n}}</div></div>
                            <div class="panel bottom-p"><div class="text-node">${{p}}</div></div>
                            <div class="leaf-node">
                                <div class="leaf-side top-p"><div class="text-node">${{p}}</div></div>
                                <div class="leaf-side side-back bottom-p"><div class="text-node">${{n}}</div></div>
                            </div>`;
            requestAnimationFrame(() => {{ void el.offsetWidth; el.classList.add('flipping'); }});
        }}

        async function smartUpdate(id, target, mode = 'msg') {{
            const tStr = (target === 0 || target === "0") ? "0" : (target ? String(target).toUpperCase() : " ");
            if (memory[id] === tStr || isBusy[id]) return;
            isBusy[id] = true;
            let curStr = memory[id] || " ";

            if (mode === 'clock' && /^\d$/.test(tStr)) {{
                let curN = /^\d$/.test(curStr) ? parseInt(curStr) : 0;
                let tarN = parseInt(tStr);
                while (curN !== tarN) {{
                    let prev = String(curN); curN = (curN + 1) % 10;
                    performFlip(id, String(curN), prev);
                    await new Promise(r => setTimeout(r, 80));
                }}
            }} else if (/^[A-Z ]$/.test(tStr)) {{
                let curIdx = charPool_AZ.indexOf(curStr);
                if (curIdx === -1) curIdx = 0;
                let tarIdx = charPool_AZ.indexOf(tStr);
                while (curIdx !== tarIdx) {{
                    let prev = charPool_AZ[curIdx];
                    curIdx = (curIdx + 1) % charPool_AZ.length;
                    performFlip(id, charPool_AZ[curIdx], prev);
                    await new Promise(r => setTimeout(r, 50));
                }}
            }} else {{
                for (let i = 0; i < 4; i++) {{
                    let rand = charPool_CN.length > 0 ? charPool_CN[Math.floor(Math.random()*charPool_CN.length)] : "?";
                    performFlip(id, rand, curStr); curStr = rand;
                    await new Promise(r => setTimeout(r, 90));
                }}
                performFlip(id, tStr, curStr);
            }}
            memory[id] = tStr; isBusy[id] = false;
        }}

        function tick() {{
            const n = new Date();
            const hh = String(n.getHours()).padStart(2, '0'), 
                  mm = String(n.getMinutes()).padStart(2, '0'), 
                  ss = String(n.getSeconds()).padStart(2, '0');
            smartUpdate('h0', hh[0], 'clock'); smartUpdate('h1', hh[1], 'clock');
            smartUpdate('tm0', mm[0], 'clock'); smartUpdate('tm1', mm[1], 'clock');
            smartUpdate('ts0', ss[0], 'clock'); smartUpdate('ts1', ss[1], 'clock');
        }}

        window.onload = () => {{
            const flapCount = 10;
            const board = document.querySelector('.acrylic-board');
            const msgW = Math.min(70, Math.floor((board.offsetWidth - 70) / flapCount));
            document.documentElement.style.setProperty('--msg-w', msgW + 'px');
            
            document.getElementById('row-msg').innerHTML = Array.from({{length: flapCount}}, (_, i) => `<div class="card msg-unit" id="m${{i}}"></div>`).join('');
            document.getElementById('row-clock').innerHTML = `
                <div class="card small-unit" id="h0"></div><div class="card small-unit" id="h1"></div>
                <div class="separator">:</div>
                <div class="card small-unit" id="tm0"></div><div class="card small-unit" id="tm1"></div>
                <div class="separator">:</div>
                <div class="card small-unit" id="ts0"></div><div class="card small-unit" id="ts1"></div>`;
            
            const msgPages = [];
            for (let i = 0; i < fullText.length; i += flapCount) msgPages.push(fullText.substring(i, i + flapCount).padEnd(flapCount, ' ').split(''));
            let pIdx = 0;
            const rotateMsg = () => {{
                msgPages[pIdx].forEach((c, i) => setTimeout(() => smartUpdate(`m${{i}}`, c, 'msg'), i * 110));
                pIdx = (pIdx + 1) % msgPages.length;
            }};
            rotateMsg(); tick(); setInterval(tick, 1000);
            if (msgPages.length > 1) setInterval(rotateMsg, {stay_sec} * 1000);
        }};
    </script>
    </body>
    </html>
    """
    b64_html = base64.b64encode(html_code.encode("utf-8")).decode("utf-8")
    components.iframe(f"data:text/html;base64,{b64_html}", height=850, scrolling=False)
