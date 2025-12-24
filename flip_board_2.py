import streamlit.components.v1 as components
import json

def render_flip_board(news_list, stay_sec=6.0):
    # 預設背景與新聞資料
    img_data = "https://upload.wikimedia.org/wikipedia/en/2/21/Girl_with_Balloon.jpg"
    # 將新聞清單轉為大寫並處理空格
    json_news = json.dumps([str(n).upper() for n in news_list])
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        * {{ box-sizing: border-box; }}
        body {{ 
            background-color: #dcdcdc; background-image: url("{img_data}");
            background-repeat: no-repeat; background-position: right 10% bottom 35%; 
            background-size: auto 25vh; display: flex; justify-content: center; 
            align-items: flex-start; height: 100vh; margin: 0; overflow: hidden;
            font-family: "Impact", "Microsoft JhengHei", sans-serif;
        }}
        .acrylic-board {{
            position: relative; width: 92vw; max-width: 850px;
            margin-top: 3vh; padding: 40px 20px;
            background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 25px;
            display: flex; flex-direction: column; align-items: center; gap: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .row-container {{ display: flex; gap: 6px; perspective: 1000px; justify-content: center; width: 100%; }}
        .card {{ background: #1a1a1a; border-radius: 5px; position: relative; overflow: hidden; color: white; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
        
        /* 寬度自適應 */
        .msg-unit {{ width: var(--msg-w); height: calc(var(--msg-w) * 1.4); font-size: calc(var(--msg-w) * 0.9); }}
        .small-unit {{ width: 34px; height: 50px; font-size: 30px; }}
        .separator {{ font-size: 32px; color: #555; font-weight: bold; line-height: 50px; padding: 0 2px; }}
        
        /* 翻牌結構與分層線 */
        .panel {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; }}
        .top-p {{ top: 0; border-bottom: 0.5px solid rgba(255,255,255,0.15); align-items: flex-end; border-radius: 5px 5px 0 0; }}
        .bottom-p {{ bottom: 0; align-items: flex-start; border-radius: 0 0 5px 5px; }}
        .text-node {{ position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 0; }}
        .top-p .text-node {{ bottom: -100%; }} .bottom-p .text-node {{ top: -100%; }}
        
        .leaf-node {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform 0.35s ease-in; transform-style: preserve-3d; }}
        .leaf-side {{ position: absolute; inset: 0; backface-visibility: hidden; background: #1a1a1a; display: flex; justify-content: center; overflow: hidden; }}
        .side-back {{ transform: rotateX(-180deg); border-top: 0.5px solid rgba(255,255,255,0.1); }}
        .flipping .leaf-node {{ transform: rotateX(-180deg); }}
    </style>
    </head>
    <body>
        <div class="acrylic-board">
            <div id="row-msg" class="row-container"></div>
            <div id="row-info" style="display: flex; flex-direction: column; gap: 12px; width: 100%; align-items: center; opacity: 0.85; transform: scale(0.9);">
                <div id="row-date" class="row-container"></div>
                <div id="row-clock" class="row-container"></div>
            </div>
        </div>
    <script>
        const newsData = {json_news};
        const flapCount = 12; // 固定顯示 12 格新聞
        const baseSpeed = 80;
        let memory = {{}};
        let isBusy = {{}};

        function performFlip(id, nextVal, prevVal) {{
            const el = document.getElementById(id);
            if(!el) return;
            const n = (nextVal !== undefined && nextVal !== null) ? String(nextVal) : " ";
            const p = (prevVal !== undefined && prevVal !== null) ? String(prevVal) : " ";
            el.innerHTML = "";
            el.classList.remove('flipping');
            el.innerHTML = `
                <div class="panel top-p"><div class="text-node">${{n}}</div></div>
                <div class="panel bottom-p"><div class="text-node">${{p}}</div></div>
                <div class="leaf-node">
                    <div class="leaf-side top-p"><div class="text-node">${{p}}</div></div>
                    <div class="leaf-side side-back bottom-p"><div class="text-node">${{n}}</div></div>
                </div>`;
            requestAnimationFrame(() => {{ void el.offsetWidth; el.classList.add('flipping'); }});
        }}

        async function smartUpdate(id, target, isInitial = false) {{
            const tStr = (target === undefined || target === null) ? " " : String(target).toUpperCase();
            if (memory[id] === tStr || isBusy[id]) return;
            isBusy[id] = true;
            let oldStr = (memory[id] === undefined) ? " " : String(memory[id]);
            
            if (/^[0-9]$/.test(tStr)) {{
                let curN = /^[0-9]$/.test(oldStr) ? parseInt(oldStr) : 0;
                while (String(curN) !== tStr) {{
                    let prev = String(curN); 
                    curN = (curN + 1) % 10;
                    performFlip(id, String(curN), prev);
                    await new Promise(r => setTimeout(r, baseSpeed * 0.7));
                }}
            }} else {{
                const steps = isInitial ? 6 : 3; 
                for (let i = 0; i < steps; i++) {{
                    let randChar = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"[Math.floor(Math.random()*36)];
                    performFlip(id, randChar, oldStr); 
                    oldStr = randChar;
                    await new Promise(r => setTimeout(r, baseSpeed));
                }}
                performFlip(id, tStr, oldStr);
            }}
            memory[id] = tStr; isBusy[id] = false;
        }}

        function tick() {{
            const n = new Date();
            const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
            const days = ["SUN","MON","TUE","WED","THU","FRI","SAT"];
            const dStr = months[n.getMonth()] + " " + String(n.getDate()).padStart(2,'0') + " " + days[n.getDay()];
            dStr.split('').forEach((c, i) => smartUpdate(`d${{i}}`, c));
            const hh = String(n.getHours()).padStart(2, '0').split('');
            const mm = String(n.getMinutes()).padStart(2, '0').split('');
            const ss = String(n.getSeconds()).padStart(2, '0').split('');
            smartUpdate('h0', hh[0]); smartUpdate('h1', hh[1]);
            smartUpdate('tm0', mm[0]); smartUpdate('tm1', mm[1]);
            smartUpdate('ts0', ss[0]); smartUpdate('ts1', ss[1]);
        }}

        window.onload = () => {{
            const board = document.querySelector('.acrylic-board');
            const msgW = Math.min(65, Math.floor((board.offsetWidth - 80) / flapCount));
            document.documentElement.style.setProperty('--msg-w', msgW + 'px');
            
            document.getElementById('row-msg').innerHTML = Array.from({{length: flapCount}}, (_, i) => `<div class="card msg-unit" id="m${{i}}"></div>`).join('');
            document.getElementById('row-date').innerHTML = Array.from({{length: 10}}, (_, i) => `<div class="card small-unit" id="d${{i}}"></div>`).join('');
            document.getElementById('row-clock').innerHTML = `
                <div class="card small-unit" id="h0"></div><div class="card small-unit" id="h1"></div>
                <div class="separator">:</div>
                <div class="card small-unit" id="tm0"></div><div class="card small-unit" id="tm1"></div>
                <div class="separator">:</div>
                <div class="card small-unit" id="ts0"></div><div class="card small-unit" id="ts1"></div>`;
            
            let newsIdx = 0;
            const rotateNews = (isFirst = false) => {{
                const text = newsData[newsIdx];
                const chars = text.padEnd(flapCount, ' ').substring(0, flapCount).split('');
                chars.forEach((c, i) => {{ 
                    setTimeout(() => smartUpdate(`m${{i}}`, c, isFirst), i * 60); 
                }});
                newsIdx = (newsIdx + 1) % newsData.length;
            }};

            setTimeout(() => rotateNews(true), 500); 
            tick(); setInterval(tick, 1000);
            setInterval(() => rotateNews(false), {stay_sec} * 1000);
        }};
    </script>
    </body>
    </html>
    """
    components.html(html_code, height=850, scrolling=False)
