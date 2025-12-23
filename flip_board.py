import streamlit.components.v1 as components
import base64

def render_flip_board(text, stay_sec=4.0):
    bg_img = "https://upload.wikimedia.org/wikipedia/en/2/21/Girl_with_Balloon.jpg"
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {{ box-sizing: border-box; }}
            html, body {{ height: 100vh; margin: 0; padding: 0; overflow: hidden; background-color: #dcdcdc; }}
            
            body {{ 
                display: flex; justify-content: center; align-items: flex-start;
                font-family: "Impact", "Arial Black", "Microsoft JhengHei", sans-serif;
            }}

            .graffiti-wall {{
                position: fixed; bottom: 0; left: 0; width: 100%; height: 50vh;
                background-image: url("{bg_img}");
                background-repeat: no-repeat; background-position: center bottom;
                background-size: contain; z-index: 1;
            }}
            
            .acrylic-board {{
                position: relative; width: 95vw; max-width: 850px;
                margin-top: 5vh; padding: 40px 25px;
                background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(15px);
                -webkit-backdrop-filter: blur(15px);
                border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 20px;
                display: flex; flex-direction: column; align-items: center; gap: 15px;
                box-shadow: 0 30px 60px rgba(0,0,0,0.2); z-index: 10;
            }}
            
            .screw {{ 
                position: absolute; width: 16px; height: 16px; 
                background: radial-gradient(circle at 30% 30%, #eee, #444); 
                border-radius: 50%; border: 1px solid #333;
            }}
            .s-tl {{ top: 15px; left: 15px; }} .s-tr {{ top: 15px; right: 15px; }}
            .s-bl {{ bottom: 15px; left: 15px; }} .s-br {{ bottom: 15px; right: 15px; }}

            .row-container {{ display: flex; gap: 8px; perspective: 1000px; justify-content: center; width: 100%; }}
            .card {{ background: #1a1a1a; border-radius: 6px; position: relative; overflow: hidden; color: white; display: flex; align-items: center; justify-content: center; }}
            
            /* 訊息翻板大小由 JS 動態調整 */
            .msg-unit {{ width: var(--msg-w); height: calc(var(--msg-w) * 1.4); font-size: calc(var(--msg-w) * 0.85); }}
            
            .small-unit {{ width: 34px; height: 50px; font-size: 30px; }}
            .separator {{ font-size: 30px; color: #444; font-weight: bold; line-height: 50px; padding: 0 3px; }}
            
            .panel {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; }}
            .top-p {{ top: 0; border-bottom: 1px solid rgba(0,0,0,0.6); align-items: flex-end; }}
            .bottom-p {{ bottom: 0; align-items: flex-start; }}
            .text-node {{ position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 1; }}
            .top-p .text-node {{ bottom: -100%; }} .bottom-p .text-node {{ top: -100%; }}
            .leaf-node {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 20; transform-origin: bottom; transition: transform 0.35s ease-in; transform-style: preserve-3d; }}
            .leaf-side {{ position: absolute; inset: 0; backface-visibility: hidden; background: #1a1a1a; display: flex; justify-content: center; overflow: hidden; }}
            .side-back {{ transform: rotateX(-180deg); }}
            .flipping .leaf-node {{ transform: rotateX(-180deg); }}
        </style>
    </head>
    <body>
        <div class="graffiti-wall"></div>
        <div class="acrylic-board">
            <div class="screw s-tl"></div><div class="screw s-tr"></div>
            <div class="screw s-bl"></div><div class="screw s-br"></div>
            <div id="row-msg" class="row-container"></div>
            <div id="row-date" class="row-container" style="margin-top: 10px;"></div>
            <div id="row-clock" class="row-container"></div>
        </div>

        <audio id="flipSound" src="https://www.soundjay.com/buttons/button-29.mp3" preload="auto"></audio>

    <script>
        const rawText = "{text.upper()}";
        const flipAudio = document.getElementById('flipSound');
        let memory = {{}}, isBusy = {{}};

        // --- 嚴格分頁邏輯實作 ---
        function getMsgPages(text) {{
            const len = text.length;
            if (len <= 1) return [text.split('')];
            
            let pages = [];
            if (len >= 17) {{
                // 規則：17字以上，每頁固定 8 字
                for (let i = 0; i < len; i += 8) {{
                    pages.push(text.substring(i, i + 8).split(''));
                }}
            }} else if (len > 8) {{
                // 規則：9-16字，非對稱拆分 (例如 9->5+4)
                const firstSize = Math.ceil(len / 2);
                pages = [text.substring(0, firstSize).split(''), text.substring(firstSize).split('')];
            }} else {{
                // 規則：2-8字，依要求拆分 (例如 5->3+2, 3->2+1)
                const firstSize = Math.ceil(len / 2);
                pages = [text.substring(0, firstSize).split(''), text.substring(firstSize).split('')];
            }}
            return pages;
        }}

        const msgPages = getMsgPages(rawText);
        // 關鍵：翻板總數由該次分頁中「字數最多的那一頁」決定
        const flapCount = Math.max(...msgPages.map(p => p.length));

        function performFlip(id, nVal, pVal) {{
            const el = document.getElementById(id);
            if(!el) return;
            
            // 修正 0 消失的邏輯：嚴格檢查字串化後的內容
            const n = (nVal !== undefined && nVal !== null && String(nVal) !== "") ? nVal : "&nbsp;";
            const p = (pVal !== undefined && pVal !== null && String(pVal) !== "") ? pVal : "&nbsp;";
            
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
            let tStr = (target === 0 || target === "0") ? "0" : (target ? String(target).toUpperCase() : " ");
            if (memory[id] === tStr || isBusy[id]) return;
            isBusy[id] = true;
            let curStr = (memory[id] === 0 || memory[id] === "0") ? "0" : (memory[id] || " ");

            if (mode === 'clock' && /^\d$/.test(tStr)) {{
                let curN = /^\d$/.test(curStr) ? parseInt(curStr) : 0;
                let tarN = parseInt(tStr);
                while (curN !== tarN) {{
                    let prev = String(curN); curN = (curN + 1) % 10;
                    performFlip(id, String(curN), prev);
                    await new Promise(r => setTimeout(r, 80));
                }}
            }} else {{
                performFlip(id, tStr, curStr);
            }}
            memory[id] = tStr; isBusy[id] = false;
        }}

        function tick() {{
            const n = new Date();
            const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
            const days = ["SUN","MON","TUE","WED","THU","FRI","SAT"];
            const dStr = months[n.getMonth()] + " " + String(n.getDate()).padStart(2,'0') + " " + days[n.getDay()];
            dStr.split('').forEach((c, i) => smartUpdate(`d${{i}}`, c, 'clock'));
            const hh = String(n.getHours()).padStart(2, '0'), mm = String(n.getMinutes()).padStart(2, '0'), ss = String(n.getSeconds()).padStart(2, '0');
            const fullClock = hh + mm + ss;
            ['h0','h1','tm0','tm1','ts0','ts1'].forEach((id, idx) => smartUpdate(id, fullClock[idx], 'clock'));
        }}

        window.onload = () => {{
            const board = document.querySelector('.acrylic-board');
            // 重新計算訊息翻板寬度
            const msgW = Math.min(110, Math.floor((board.offsetWidth - 100) / flapCount));
            document.documentElement.style.setProperty('--msg-w', msgW + 'px');
            
            // 動態生成 HTML 節點，不再固定 10 個
            document.getElementById('row-msg').innerHTML = Array.from({{length: flapCount}}, (_, i) => `<div class="card msg-unit" id="m${{i}}"></div>`).join('');
            document.getElementById('row-date').innerHTML = Array.from({{length: 11}}, (_, i) => `<div class="card small-unit" id="d${{i}}"></div>`).join('');
            document.getElementById('row-clock').innerHTML = `<div class="card small-unit" id="h0"></div><div class="card small-unit" id="h1"></div><div class="separator">:</div><div class="card small-unit" id="tm0"></div><div class="card small-unit" id="tm1"></div><div class="separator">:</div><div class="card small-unit" id="ts0"></div><div class="card small-unit" id="ts1"></div>`;
            
            let pIdx = 0;
            const rotateMsg = () => {{
                const currentPage = msgPages[pIdx];
                for(let i=0; i<flapCount; i++) {{
                    const char = currentPage[i] || " "; 
                    setTimeout(() => smartUpdate(`m${{i}}`, char, 'msg'), i * 80);
                }}
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
    components.iframe(f"data:text/html;base64,{b64_html}", height=1000, scrolling=False)
