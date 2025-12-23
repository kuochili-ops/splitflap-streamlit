import streamlit.components.v1 as components
import time

def render_flip_board(text, stay_sec=4.0):
    # 確保 text 為字串
    safe_text = str(text).upper()
    try:
        safe_stay = float(stay_sec)
    except:
        safe_stay = 4.0

    # 使用多行字串，不使用 f-string 以免大括號衝突
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; }
        body { 
            background-color: #1a1a1a; margin: 0; padding: 20px;
            display: flex; justify-content: center; overflow: hidden;
            font-family: "Impact", "Arial Black", sans-serif;
        }
        .acrylic-board {
            position: relative; width: 92vw; max-width: 850px;
            padding: 60px 40px; background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 30px; display: flex; flex-direction: column; align-items: center; gap: 20px;
            box-shadow: 0 40px 100px rgba(0,0,0,0.5), inset 0 0 20px rgba(255,255,255,0.05);
        }
        /* 十字螺絲細節 */
        .screw {
            position: absolute; width: 18px; height: 18px;
            background: radial-gradient(circle at 30% 30%, #999, #444);
            border-radius: 50%; box-shadow: 2px 2px 5px rgba(0,0,0,0.6);
        }
        .screw::before, .screw::after {
            content: ''; position: absolute; top: 50%; left: 50%;
            background: rgba(0,0,0,0.4); transform: translate(-50%, -50%);
        }
        .screw::before { width: 10px; height: 2px; }
        .screw::after { width: 2px; height: 10px; }
        .tl { top: 20px; left: 20px; transform: rotate(15deg); }
        .tr { top: 20px; right: 20px; transform: rotate(-10deg); }
        .bl { bottom: 20px; left: 20px; transform: rotate(-20deg); }
        .br { bottom: 20px; right: 20px; transform: rotate(45deg); }

        .row-container { display: flex; gap: 8px; perspective: 1000px; justify-content: center; }
        .card { 
            background: #050505; border-radius: 6px; position: relative; 
            color: white; display: flex; align-items: center; justify-content: center;
            box-shadow: 0 10px 20px rgba(0,0,0,0.5);
        }
        .msg-unit { width: var(--msg-w); height: calc(var(--msg-w) * 1.4); font-size: calc(var(--msg-w) * 0.9); }
        .small-unit { width: 36px; height: 55px; font-size: 34px; }
        .separator { font-size: 34px; color: #444; line-height: 55px; padding: 0 4px; }
        
        .panel { position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; display: flex; justify-content: center; }
        .top-p { top: 0; background: linear-gradient(180deg, #222, #181818); border-bottom: 1px solid #000; align-items: flex-end; border-radius: 6px 6px 0 0; }
        .bottom-p { bottom: 0; background: linear-gradient(180deg, #151515, #000); align-items: flex-start; border-radius: 0 0 6px 6px; }
        .text-node { position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 1; }
        .top-p .text-node { bottom: -100%; } .bottom-p .text-node { top: -100%; }
        
        .leaf-node { position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }
        .leaf-side { position: absolute; inset: 0; backface-visibility: hidden; display: flex; justify-content: center; overflow: hidden; }
        .side-back { transform: rotateX(-180deg); background: #111; }
        .flipping .leaf-node { transform: rotateX(-180deg); }
    </style>
    </head>
    <body>
        <div class="acrylic-board">
            <div class="screw tl"></div><div class="screw tr"></div>
            <div class="screw bl"></div><div class="screw br"></div>
            <div id="row-msg" class="row-container"></div>
            <div id="row-date" class="row-container" style="margin-top:20px"></div>
            <div id="row-clock" class="row-container" style="margin-top:10px"></div>
        </div>
    <script>
        const fullText = "REPLACE_TEXT";
        const stayTime = REPLACE_STAY;
        let memory = {};
        
        function performFlip(id, nV, pV) {
            const el = document.getElementById(id);
            if(!el) return;
            const n = (nV === " " || !nV) ? "&nbsp;" : nV;
            const p = (pV === " " || !pV) ? "&nbsp;" : pV;
            el.innerHTML = `<div class="panel top-p"><div class="text-node">${n}</div></div>
                            <div class="panel bottom-p"><div class="text-node">${p}</div></div>
                            <div class="leaf-node">
                                <div class="leaf-side top-p"><div class="text-node">${p}</div></div>
                                <div class="leaf-side side-back bottom-p"><div class="text-node">${n}</div></div>
                            </div>`;
            el.classList.remove('flipping');
            void el.offsetWidth;
            el.classList.add('flipping');
        }

        async function smartUpdate(id, target) {
            if (memory[id] === target) return;
            const old = memory[id] || " ";
            performFlip(id, target, old);
            memory[id] = target;
        }

        function tick() {
            const n = new Date();
            const dStr = n.toLocaleDateString('en-US', {month:'short', day:'2-digit', weekday:'short'}).toUpperCase().replace(/,/g,'');
            dStr.split('').forEach((c, i) => smartUpdate(`d${i}`, c));
            const timeStr = n.getHours().toString().padStart(2,'0') + n.getMinutes().toString().padStart(2,'0') + n.getSeconds().toString().padStart(2,'0');
            ['h0','h1','tm0','tm1','ts0','ts1'].forEach((id, i) => smartUpdate(id, timeStr[i]));
        }

        window.onload = () => {
            const flapCount = Math.max(8, Math.min(12, fullText.length));
            const msgW = Math.floor((document.querySelector('.acrylic-board').offsetWidth - 100) / flapCount);
            document.documentElement.style.setProperty('--msg-w', msgW + 'px');
            
            document.getElementById('row-msg').innerHTML = Array.from({length: flapCount}, (_, i) => `<div class="card msg-unit" id="m${i}"></div>`).join('');
            document.getElementById('row-date').innerHTML = Array.from({length: 11}, (_, i) => `<div class="card small-unit" id="d${i}"></div>`).join('');
            document.getElementById('row-clock').innerHTML = `
                <div class="card small-unit" id="h0"></div><div class="card small-unit" id="h1"></div><div class="separator">:</div>
                <div class="card small-unit" id="tm0"></div><div class="card small-unit" id="tm1"></div><div class="separator">:</div>
                <div class="card small-unit" id="ts0"></div><div class="card small-unit" id="ts1"></div>`;
            
            const pages = [];
            for (let i = 0; i < fullText.length; i += flapCount) pages.push(fullText.substring(i, i + flapCount).padEnd(flapCount, ' '));
            if(pages.length===0) pages.push(" ".repeat(flapCount));

            let pIdx = 0;
            const rotate = () => {
                pages[pIdx].split('').forEach((c, i) => setTimeout(() => smartUpdate(`m${i}`, c), i * 50));
                pIdx = (pIdx + 1) % pages.length;
            };
            rotate(); setInterval(tick, 1000);
            if(pages.length > 1) setInterval(rotate, stayTime * 1000);
        };
    </script>
    </body>
    </html>
    """
    
    # 使用取代方式，避免 Python f-string 誤判 JavaScript 的大括號
    final_html = html_template.replace("REPLACE_TEXT", safe_text).replace("REPLACE_STAY", str(safe_stay))
    
    # 確保 Key 也是乾淨的字串
    comp_key = f"v12_{int(time.time())}"
    components.html(final_html, height=850, scrolling=False, key=comp_key)
