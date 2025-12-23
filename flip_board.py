import streamlit.components.v1 as components
import base64

def render_flip_board(text, stay_sec=4.0):
    t_val = str(text).upper()
    s_val = str(float(stay_sec))

    # 這裡使用更完整的 CSS 翻牌結構
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { background: #1a1a1a; margin: 0; padding: 20px; display: flex; justify-content: center; font-family: sans-serif; overflow: hidden; }
            .board {
                position: relative; background: #222; padding: 50px 30px; border-radius: 30px; 
                border: 2px solid #444; box-shadow: 0 40px 100px rgba(0,0,0,0.5);
                display: flex; flex-direction: column; align-items: center; gap: 15px;
            }
            .screw { position: absolute; width: 14px; height: 14px; background: #555; border-radius: 50%; box-shadow: 1px 1px 2px #000; }
            .screw::before { content: '+'; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #333; font-size: 12px; font-weight: bold; }
            .tl { top: 20px; left: 20px; } .tr { top: 20px; right: 20px; }
            .bl { bottom: 20px; left: 20px; } .br { bottom: 20px; right: 20px; }

            .row { display: flex; gap: 6px; perspective: 1000px; }
            .card { 
                background: #000; border-radius: 6px; color: #fff; position: relative;
                width: 50px; height: 75px; font-size: 50px; font-weight: bold;
                display: flex; align-items: center; justify-content: center;
                box-shadow: 0 5px 15px rgba(0,0,0,0.5);
                border: 1px solid #333;
            }
            .small { width: 35px; height: 50px; font-size: 30px; }
            .sep { color: #555; font-size: 30px; line-height: 50px; font-weight: bold; }
            
            /* 模擬翻牌動作的 CSS */
            .flip-anim { animation: flipEffect 0.5s cubic-bezier(0.4, 0, 0.2, 1); }
            @keyframes flipEffect {
                0% { transform: rotateX(0deg); filter: brightness(1); }
                50% { transform: rotateX(-90deg); filter: brightness(1.5); }
                100% { transform: rotateX(0deg); filter: brightness(1); }
            }
        </style>
    </head>
    <body>
        <div class="board">
            <div class="screw tl"></div><div class="screw tr"></div>
            <div class="screw bl"></div><div class="screw br"></div>
            <div id="m-row" class="row"></div>
            <div id="d-row" class="row" style="margin-top:10px"></div>
            <div id="c-row" class="row"></div>
        </div>
        <script>
            var msg = "REPLACE_TEXT";
            var stay = REPLACE_STAY;
            var mem = {};

            function update(id, val) {
                var el = document.getElementById(id);
                if (!el || mem[id] === val) return;
                el.classList.remove('flip-anim');
                void el.offsetWidth; 
                el.innerText = (val === " " ? "\\u00A0" : val);
                el.classList.add('flip-anim');
                mem[id] = val;
            }

            function tick() {
                var n = new Date();
                var dStr = n.toLocaleDateString('en-US', {month:'short', day:'2-digit', weekday:'short'}).toUpperCase().replace(/,/g,'');
                dStr.split('').forEach((c, i) => update('d'+i, c));
                var h = n.getHours().toString().padStart(2,'0'), m = n.getMinutes().toString().padStart(2,'0'), s = n.getSeconds().toString().padStart(2,'0');
                (h+m+s).split('').forEach((c, i) => update('t'+i, c));
            }

            window.onload = function() {
                var count = Math.max(8, msg.length);
                document.getElementById('m-row').innerHTML = Array.from({length:count}, (_,i) => '<div class="card" id="m'+i+'"></div>').join('');
                document.getElementById('d-row').innerHTML = Array.from({length:11}, (_,i) => '<div class="card small" id="d'+i+'"></div>').join('');
                document.getElementById('c-row').innerHTML = '<div class="card small" id="t0"></div><div class="card small" id="t1"></div><div class="sep">:</div><div class="card small" id="t2"></div><div class="card small" id="t3"></div><div class="sep">:</div><div class="card small" id="t4"></div><div class="card small" id="t5"></div>';
                
                var pages = [];
                for (var k=0; k<msg.length; k+=count) pages.push(msg.substring(k, k+count).padEnd(count, ' '));
                
                var pIdx = 0;
                var rotateMsg = function() {
                    pages[pIdx].split('').forEach((c, i) => setTimeout(() => update('m'+i, c), i*60));
                    pIdx = (pIdx + 1) % pages.length;
                };

                rotateMsg(); tick(); setInterval(tick, 1000);
                if(pages.length > 1) setInterval(rotateMsg, stay * 1000);
            };
        </script>
    </body>
    </html>
    """
    
    # 使用字串替換而非 f-string 注入，確保安全
    final_html = html_content.replace("REPLACE_TEXT", t_val).replace("REPLACE_STAY", s_val)
    b64 = base64.b64encode(final_html.encode('utf-8')).decode('utf-8')
    data_uri = "data:text/html;base64," + b64
    
    # 這裡的 key 改用純字串拼接，避開 Python 3.13 的格式化問題
    components.iframe(data_uri, height=480, scrolling=False, key="flip_board_final")
