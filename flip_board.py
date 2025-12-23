import streamlit.components.v1 as components
import time

def render_flip_board(text, stay_sec=4.0):
    # 基礎參數清洗
    t_val = str(text).upper()
    try:
        s_val = float(stay_sec)
    except:
        s_val = 4.0

    # 分段定義：CSS
    css_code = """
    <style>
        * { box-sizing: border-box; }
        body { background-color: #1a1a1a; margin: 0; padding: 20px; display: flex; justify-content: center; overflow: hidden; font-family: sans-serif; }
        .acrylic-board {
            position: relative; width: 92vw; max-width: 850px; padding: 60px 40px; 
            background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(15px); 
            border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 30px; 
            display: flex; flex-direction: column; align-items: center; gap: 20px;
            box-shadow: 0 40px 100px rgba(0,0,0,0.5);
        }
        /* 十字螺絲 CSS */
        .screw { position: absolute; width: 18px; height: 18px; background: radial-gradient(circle at 30% 30%, #999, #444); border-radius: 50%; }
        .screw::before, .screw::after { content: ''; position: absolute; top: 50%; left: 50%; background: rgba(0,0,0,0.4); transform: translate(-50%, -50%); }
        .screw::before { width: 10px; height: 2px; } .screw::after { width: 2px; height: 10px; }
        .tl { top: 20px; left: 20px; rotate: 15deg; } .tr { top: 20px; right: 20px; rotate: -10deg; }
        .bl { bottom: 20px; left: 20px; rotate: -20deg; } .br { bottom: 20px; right: 20px; rotate: 45deg; }

        .row-container { display: flex; gap: 8px; perspective: 1000px; justify-content: center; }
        .card { background: #050505; border-radius: 6px; position: relative; color: white; display: flex; align-items: center; justify-content: center; width: var(--msg-w); height: calc(var(--msg-w) * 1.4); font-size: calc(var(--msg-w) * 0.9); font-weight: bold; }
        .small-unit { width: 36px !important; height: 55px !important; font-size: 34px !important; }
        .separator { font-size: 34px; color: #444; line-height: 55px; padding: 0 4px; }
        
        .panel { position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; display: flex; justify-content: center; background: #111; }
        .top-p { top: 0; border-bottom: 1px solid #000; align-items: flex-end; border-radius: 6px 6px 0 0; }
        .bottom-p { bottom: 0; align-items: flex-start; border-radius: 0 0 6px 6px; }
        .text-node { position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 1; }
        .top-p .text-node { bottom: -100%; } .bottom-p .text-node { top: -100%; }
        
        .leaf-node { position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform 0.4s; transform-style: preserve-3d; }
        .leaf-side { position: absolute; inset: 0; backface-visibility: hidden; display: flex; justify-content: center; overflow: hidden; }
        .side-back { transform: rotateX(-180deg); background: #111; }
        .flipping .leaf-node { transform: rotateX(-180deg); }
    </style>
    """

    # 分段定義：JavaScript
    js_template = """
    <script>
        const fullText = "REPLACE_TEXT";
        const stayTime = REPLACE_STAY;
        let memory = {};
        
        function flip(id, nV, pV) {
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

        function update(id, target) {
            if (memory[id] === target) return;
            const old = memory[id] || " ";
            flip(id, target, old);
            memory[id] = target;
        }

        function tick() {
            const n = new Date();
            const dStr = n.toLocaleDateString('en-US', {month:'short', day:'2-digit', weekday:'short'}).toUpperCase().replace(/,/g,'');
            dStr.split('').forEach((c, i) => update(`d${i}`, c));
            const timeStr = n.getHours().toString().padStart(2,'0') + n.getMinutes().toString().padStart(2,'0') + n.getSeconds().toString().padStart(2,'0');
            ['h0','h1','tm0','tm1','ts0','ts1'].forEach((id, i) => update(id, timeStr[i]));
        }

        window.onload = () => {
            const board = document.querySelector('.acrylic-board');
            const fCount = Math.max(8, Math.min(12, fullText.length));
            const msgW = Math.floor((board.offsetWidth - 100) / fCount);
            document.documentElement.style.setProperty('--msg-w', msgW + 'px');
            
            document.getElementById('row-msg').innerHTML = Array.from({length: fCount}, (_, i) => `<div class="card" id="m${i}"></div>`).join('');
            document.getElementById('row-date').innerHTML = Array.from({length: 11}, (_, i) => `<div class="card small-unit" id="d${i}"></div>`).join('');
            document.getElementById('row-clock').innerHTML = `
                <div class="card small-unit" id="h0"></div><div class="card small-unit" id="h1"></div><div class="separator">:</div>
                <div class="card small-unit" id="tm0"></div><div class="card small-unit" id="tm1"></div><div class="separator">:</div>
                <div class="card small-unit" id="ts0"></div><div class="card small-unit" id="ts1"></div>`;
            
            const pages = [];
            for (let i = 0; i < fullText.length; i += fCount) pages.push(fullText.substring(i, i + fCount).padEnd(fCount, ' '));
            if(pages.length===0) pages.push(" ".repeat(fCount));

            let pIdx = 0;
            const rot = () => {
                pages[pIdx].split('').forEach((c, i) => setTimeout(() => update(`m${i}`, c), i * 50));
                pIdx = (pIdx + 1) % pages.length;
            };
            rot(); setInterval(tick, 1000);
            if(pages.length > 1) setInterval(rot, stayTime * 1000);
        };
    </script>
    """

    # 組合 HTML
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8">{css_code}</head>
    <body>
        <div class="acrylic-board">
            <div class="screw tl"></div><div class="screw tr"></div>
            <div class="screw bl"></div><div class="screw br"></div>
            <div id="row-msg" class="row-container"></div>
            <div id="row-date" class="row-container" style="margin-top:20px"></div>
            <div id="row-clock" class="row-container" style="margin-top:10px"></div>
        </div>
        {js_template.replace("REPLACE_TEXT", t_val).replace("REPLACE_STAY", str(s_val))}
    </body>
    </html>
    """
    
    # 這裡是最核心的修正：確保 key 是乾淨的，並將 html_body 包裝在 str() 中
    k = f"board_{int(time.time())}"
    components.html(html_body, height=850, scrolling=False, key=k)
