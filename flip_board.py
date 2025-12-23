import streamlit.components.v1 as components
import time

def render_flip_board(text, stay_sec=4.0):
    t_val = str(text).upper()
    try:
        s_val = float(stay_sec)
    except:
        s_val = 4.0

    # 螺絲與金屬質感的 CSS
    css_code = """
    <style>
        * { box-sizing: border-box; }
        body { 
            background: radial-gradient(circle at center, #2a2a2a 0%, #121212 100%);
            margin: 0; padding: 20px; display: flex; justify-content: center; overflow: hidden; 
        }
        .acrylic-board {
            position: relative; width: 92vw; max-width: 850px; padding: 60px 40px; 
            background: linear-gradient(135deg, rgba(60,60,60,0.4) 0%, rgba(20,20,20,0.6) 100%);
            backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.1); border-radius: 30px; 
            display: flex; flex-direction: column; align-items: center; gap: 20px;
            box-shadow: 0 50px 100px rgba(0,0,0,0.8), inset 0 0 40px rgba(0,0,0,0.5);
        }
        /* 十字螺絲：增加光澤與深度 */
        .screw { 
            position: absolute; width: 18px; height: 18px; 
            background: radial-gradient(circle at 30% 30%, #eee 0%, #666 50%, #333 100%);
            border-radius: 50%; box-shadow: 2px 4px 8px rgba(0,0,0,0.6);
        }
        .screw::before, .screw::after { 
            content: ''; position: absolute; top: 50%; left: 50%; 
            background: rgba(0,0,0,0.6); transform: translate(-50%, -50%); 
        }
        .screw::before { width: 11px; height: 2px; } .screw::after { width: 2px; height: 11px; }
        .tl { top: 25px; left: 25px; rotate: 12deg; } .tr { top: 25px; right: 25px; rotate: -8deg; }
        .bl { bottom: 25px; left: 25px; rotate: -22deg; } .br { bottom: 25px; right: 25px; rotate: 35deg; }

        .row-container { display: flex; gap: 8px; perspective: 1000px; justify-content: center; }
        .card { 
            background: #080808; border-radius: 6px; position: relative; color: white; 
            display: flex; align-items: center; justify-content: center; 
            width: var(--msg-w); height: calc(var(--msg-w) * 1.45); 
            font-size: calc(var(--msg-w) * 0.95); font-weight: bold; font-family: sans-serif;
            box-shadow: 0 8px 15px rgba(0,0,0,0.5);
        }
        .small-unit { width: 38px !important; height: 58px !important; font-size: 36px !important; }
        .separator { font-size: 36px; color: #555; line-height: 58px; padding: 0 4px; text-shadow: 0 0 10px rgba(0,0,0,1); }
        
        .panel { position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; display: flex; justify-content: center; background: linear-gradient(180deg, #222 0%, #111 100%); }
        .top-p { top: 0; border-bottom: 1px solid #000; align-items: flex-end; border-radius: 6px 6px 0 0; }
        .bottom-p { bottom: 0; align-items: flex-start; border-radius: 0 0 6px 6px; background: linear-gradient(180deg, #111 0%, #050505 100%); }
        .text-node { position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 1; }
        .top-p .text-node { bottom: -100%; } .bottom-p .text-node { top: -100%; }
        
        .leaf-node { position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }
        .leaf-side { position: absolute; inset: 0; backface-visibility: hidden; display: flex; justify-content: center; overflow: hidden; }
        .side-back { transform: rotateX(-180deg); background: #111; }
        .flipping .leaf-node { transform: rotateX(-180deg); }
    </style>
    """

    # 避開 ${} 的傳統 JS
    js_logic = """
    <script>
        var fullText = "REPLACE_TEXT";
        var stayTime = REPLACE_STAY;
        var memory = {};
        
        function flip(id, nV, pV) {
            var el = document.getElementById(id);
            if(!el) return;
            var n = (nV === " " || !nV) ? "&nbsp;" : nV;
            var p = (pV === " " || !pV) ? "&nbsp;" : pV;
            
            // 修正：手動相加字串，避免使用反引號內的變數插槽，減少解析錯誤
            var html = '<div class="panel top-p"><div class="text-node">' + n + '</div></div>' +
                       '<div class="panel bottom-p"><div class="text-node">' + p + '</div></div>' +
                       '<div class="leaf-node">' +
                         '<div class="leaf-side top-p"><div class="text-node">' + p + '</div></div>' +
                         '<div class="leaf-side side-back bottom-p"><div class="text-node">' + n + '</div></div>' +
                       '</div>';
            
            el.innerHTML = html;
            el.classList.remove('flipping');
            void el.offsetWidth;
            el.classList.add('flipping');
        }

        function update(id, target) {
            if (memory[id] === target) return;
            var old = memory[id] || " ";
            flip(id, target, old);
            memory[id] = target;
        }

        function tick() {
            var n = new Date();
            var dStr = n.toLocaleDateString('en-US', {month:'short', day:'2-digit', weekday:'short'}).toUpperCase().replace(/,/g,'');
            dStr.split('').forEach(function(c, i) { update('d' + i, c); });
            
            var h = n.getHours().toString().padStart(2,'0');
            var m = n.getMinutes().toString().padStart(2,'0');
            var s = n.getSeconds().toString().padStart(2,'0');
            var timeStr = h + m + s;
            ['h0','h1','tm0','tm1','ts0','ts1'].forEach(function(id, i) { update(id, timeStr[i]); });
        }

        window.onload = function() {
            var board = document.querySelector('.acrylic-board');
            var fCount = Math.max(8, Math.min(12, fullText.length));
            var msgW = Math.floor((board.offsetWidth - 110) / fCount);
            document.documentElement.style.setProperty('--msg-w', msgW + 'px');
            
            var msgHtml = "";
            for(var i=0; i<fCount; i++) { msgHtml += '<div class="card" id="m' + i + '"></div>'; }
            document.getElementById('row-msg').innerHTML = msgHtml;
            
            var dateHtml = "";
            for(var j=0; j<11; j++) { dateHtml += '<div class="card small-unit" id="d' + j + '"></div>'; }
            document.getElementById('row-date').innerHTML = dateHtml;

            document.getElementById('row-clock').innerHTML = 
                '<div class="card small-unit" id="h0"></div><div class="card small-unit" id="h1"></div><div class="separator">:</div>' +
                '<div class="card small-unit" id="tm0"></div><div class="card small-unit" id="tm1"></div><div class="separator">:</div>' +
                '<div class="card small-unit" id="ts0"></div><div class="card small-unit" id="ts1"></div>';
            
            var pages = [];
            for (var k = 0; k < fullText.length; k += fCount) {
                pages.push(fullText.substring(k, k + fCount).padEnd(fCount, ' '));
            }
            if(pages.length === 0) pages.push(" ".repeat(fCount));

            var pIdx = 0;
            var rot = function() {
                pages[pIdx].split('').forEach(function(c, i) { 
                    setTimeout(function(){ update('m' + i, c); }, i * 50); 
                });
                pIdx = (pIdx + 1) % pages.length;
            };
            rot(); tick(); setInterval(tick, 1000);
            if(pages.length > 1) setInterval(rot, stayTime * 1000);
        };
    </script>
    """

    final_html = f"""
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
        {js_logic.replace("REPLACE_TEXT", t_val).replace("REPLACE_STAY", str(s_val))}
    </body>
    </html>
    """
    
    components.html(final_html, height=850, scrolling=False, key=f"board_{int(time.time())}")
