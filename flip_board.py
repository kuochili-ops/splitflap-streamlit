import streamlit.components.v1 as components
import base64

def render_flip_board(text, stay_sec=4.0):
    img_data = "https://upload.wikimedia.org/wikipedia/en/2/21/Girl_with_Balloon.jpg"
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            /* 這裡保留妳最完美的 CSS 結構 */
            * {{ box-sizing: border-box; }}
            body {{ 
                background-color: #dcdcdc; background-image: url("{img_data}");
                background-repeat: no-repeat; background-position: right 10% bottom 35%; 
                background-size: auto 30vh; display: flex; justify-content: center; 
                align-items: flex-start; height: 100vh; margin: 0; overflow: hidden;
                font-family: "Impact", "Arial Black", "Microsoft JhengHei", sans-serif;
            }}
            .acrylic-board {{
                position: relative; width: 95vw; max-width: 850px;
                margin-top: 5vh; padding: 45px 30px;
                background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px);
                border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 25px;
                display: flex; flex-direction: column; align-items: center; gap: 15px;
                box-shadow: 0 20px 50px rgba(0,0,0,0.15);
            }}
            .row-container {{ display: flex; gap: 5px; perspective: 1000px; justify-content: center; width: 100%; }}
            .card {{ background: #1a1a1a; border-radius: 6px; position: relative; overflow: hidden; color: white; display: flex; align-items: center; justify-content: center; }}
            .msg-unit {{ width: var(--msg-w); height: calc(var(--msg-w) * 1.45); font-size: calc(var(--msg-w) * 0.8); }}
            .small-unit {{ width: 34px; height: 50px; font-size: 32px; }}
            .separator {{ font-size: 32px; color: #555; font-weight: bold; line-height: 50px; padding: 0 2px; }}
            .panel {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; }}
            .top-p {{ top: 0; border-bottom: 1px solid rgba(0,0,0,0.5); align-items: flex-end; border-radius: 6px 6px 0 0; }}
            .bottom-p {{ bottom: 0; align-items: flex-start; border-radius: 0 0 6px 6px; }}
            .text-node {{ position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 1; }}
            .top-p .text-node {{ bottom: -100%; transform: translateY(1px); }} 
            .bottom-p .text-node {{ top: -100%; transform: translateY(-1px); }}
            .leaf-node {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform 0.4s ease-in; transform-style: preserve-3d; }}
            .leaf-side {{ position: absolute; inset: 0; backface-visibility: hidden; background: #1a1a1a; display: flex; justify-content: center; overflow: hidden; }}
            .side-back {{ transform: rotateX(-180deg); }}
            .flipping .leaf-node {{ transform: rotateX(-180deg); }}
        </style>
    </head>
    <body>
        <div class="acrylic-board">
            <div id="row-msg" class="row-container"></div>
            <div id="row-info" style="display: flex; flex-direction: column; gap: 10px; width: 100%; align-items: center;">
                <div id="row-date" class="row-container"></div>
                <div id="row-clock" class="row-container"></div>
            </div>
        </div>
    <script>
        const fullText = "{text.upper()}";
        const charPool_AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split('');
        const charPool_Num = "0123456789".split('');
        // 僅從訊息中提取中文字作為隨機池
        const charPool_CN = [...new Set(fullText.replace(/[A-Z0-9\s]/g, '').split(''))];
        
        let memory = {{}};
        let isBusy = {{}};

        function performFlip(id, nVal, pVal) {{
            const el = document.getElementById(id);
            if(!el) return;
            const n = (nVal === 0 || nVal === "0") ? "0" : (nVal || "&nbsp;");
            const p = (pVal === 0 || pVal === "0") ? "0" : (pVal || "&nbsp;");
            el.innerHTML = ""; el.classList.remove('flipping');
            el.innerHTML = `<div class="panel top-p"><div class="text-node">${{n}}</div></div>
                            <div class="panel bottom-p"><div class="text-node">${{p}}</div></div>
                            <div class="leaf-node"><div class="leaf-side top-p"><div class="text-node">${{p}}</div></div>
                            <div class="leaf-side side-back bottom-p"><div class="text-node">${{n}}</div></div></div>`;
            requestAnimationFrame(() => {{ void el.offsetWidth; el.classList.add('flipping'); }});
        }}

        // 分離邏輯：mode 用來區分是「時鐘/日期」還是「訊息」
        async function smartUpdate(id, target, mode = 'msg') {{
            const tStr = (target === 0 || target === "0") ? "0" : (target ? String(target).toUpperCase() : " ");
            if (memory[id] === tStr || isBusy[id]) return;
            isBusy[id] = true;
            let curStr = memory[id] || " ";

            const isDigit = (s) => /^\d$/.test(s.trim());
            const isAlpha = (s) => /^[A-Z]$/.test(s.trim());

            // 1. 如果是時鐘或日期中的數字，強制執行 0-9 循序翻動 (不受訊息影響)
            if (mode === 'clock' && isDigit(tStr)) {{
                let curN = isDigit(curStr) ? parseInt(curStr) : 0;
                let tarN = parseInt(tStr);
                while (curN !== tarN) {{
                    let prev = String(curN); curN = (curN + 1) % 10;
                    performFlip(id, String(curN), prev);
                    await new Promise(r => setTimeout(r, 80));
                }}
            }} 
            // 2. 如果是英文字母，執行 A-Z 循序翻動
            else if (isAlpha(tStr)) {{
                let curIdx = charPool_AZ.indexOf(curStr);
                if (curIdx === -1) curIdx = 0;
                let tarIdx = charPool_AZ.indexOf(tStr);
                while (curIdx !== tarIdx) {{
                    let prev = charPool_AZ[curIdx];
                    curIdx = (curIdx + 1) % 26;
                    performFlip(id, charPool_AZ[curIdx], prev);
                    await new Promise(r => setTimeout(r, 60));
                }}
            }} 
            // 3. 如果是中文字，從訊息池中隨機跳動後定格
            else {{
                const steps = 6;
                for (let i = 0; i < steps; i++) {{
                    let rand = charPool_CN.length > 0 ? charPool_CN[Math.floor(Math.random()*charPool_CN.length)] : "?";
                    performFlip(id, rand, curStr); curStr = rand;
                    await new Promise(r => setTimeout(r, 100));
                }}
                performFlip(id, tStr, curStr);
            }}
            memory[id] = tStr; isBusy[id] = false;
        }}

        function tick() {{
            const n = new Date();
            const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
            const days = ["SUN","MON","TUE","WED","THU","FRI","SAT"];
            
            // 日期與時間標記為 'clock' 模式
            const dStr = months[n.getMonth()] + " " + String(n.getDate()).padStart(2,'0') + " " + days[n.getDay()];
            dStr.split('').forEach((c, i) => smartUpdate(`d${{i}}`, c, 'clock'));
            
            const hh = String(n.getHours()).padStart(2, '0'), mm = String(n.getMinutes()).padStart(2, '0'), ss = String(n.getSeconds()).padStart(2, '0');
            smartUpdate('h0', hh[0], 'clock'); smartUpdate('h1', hh[1], 'clock');
            smartUpdate('tm0', mm[0], 'clock'); smartUpdate('tm1', mm[1], 'clock');
            smartUpdate('ts0', ss[0], 'clock'); smartUpdate('ts1', ss[1], 'clock');
        }}

        window.onload = () => {{
            const flapCount = 10;
            const board = document.querySelector('.acrylic-board');
            const msgW = Math.min(75, Math.floor((board.offsetWidth - 70) / flapCount));
            document.documentElement.style.setProperty('--msg-w', msgW + 'px');
            document.getElementById('row-msg').innerHTML = Array.from({{length: flapCount}}, (_, i) => `<div class="card msg-unit" id="m${{i}}"></div>`).join('');
            document.getElementById('row-date').innerHTML = Array.from({{length: 11}}, (_, i) => `<div class="card small-unit" id="d${{i}}"></div>`).join('');
            document.getElementById('row-clock').innerHTML = `<div class="card small-unit" id="h0"></div><div class="card small-unit" id="h1"></div><div class="separator">:</div><div class="card small-unit" id="tm0"></div><div class="card small-unit" id="tm1"></div><div class="separator">:</div><div class="card small-unit" id="ts0"></div><div class="card small-unit" id="ts1"></div>`;
            
            const msgPages = [];
            for (let i = 0; i < fullText.length; i += flapCount) msgPages.push(fullText.substring(i, i + flapCount).padEnd(flapCount, ' ').split(''));
            let pIdx = 0;
            const rotateMsg = () => {{
                msgPages[pIdx].forEach((c, i) => setTimeout(() => smartUpdate(`m${{i}}`, c, 'msg'), i * 150));
                pIdx = (pIdx + 1) % msgPages.length;
            }};
            rotateMsg(); tick(); setInterval(tick, 1000);
            if (msgPages.length > 1) setInterval(rotateMsg, {stay_sec} * 1000);
        }};
    </script>
    </body>
    </html>
    """
    
    # 最終使用 Base64 封裝，保證不噴 TypeError，且維持所有機械動畫
    import base64
    b64_html = base64.b64encode(html_code.encode("utf-8")).decode("utf-8")
    components.iframe(f"data:text/html;base64,{b64_html}", height=850, scrolling=False)
