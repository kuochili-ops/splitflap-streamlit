import streamlit.components.v1 as components
import time
import base64

def render_flip_board(text, stay_sec=4.0):
    # 參數清理
    t_val = str(text).upper()
    try:
        s_val = str(float(stay_sec))
    except:
        s_val = "4.0"

    # 定義純粹的 HTML 模板 (不使用 f-string，避免大括號衝突)
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { background: #1a1a1a; margin: 0; padding: 20px; display: flex; justify-content: center; font-family: sans-serif; overflow: hidden; }
        .board {
            position: relative; width: 92vw; max-width: 850px; padding: 60px 40px; 
            background: #222; border-radius: 30px; border: 1px solid #444;
            display: flex; flex-direction: column; align-items: center; gap: 20px;
            box-shadow: 0 40px 100px rgba(0,0,0,0.5);
        }
        /* 十字螺絲設計 */
        .screw { position: absolute; width: 16px; height: 16px; background: #555; border-radius: 50%; box-shadow: 1px 1px 3px rgba(0,0,0,0.5); }
        .screw::before { content: '+'; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #333; font-size: 14px; font-weight: bold; }
        .tl { top: 20px; left: 20px; } .tr { top: 20px; right: 20px; }
        .bl { bottom: 20px; left: 20px; } .br { bottom: 20px; right: 20px; }

        .row { display: flex; gap: 8px; justify-content: center; }
        .card { 
            background: #000; border-radius: 6px; color: #fff; 
            display: flex; align-items: center; justify-content: center; 
            width: var(--w); height: calc(var(--w) * 1.4); 
            font-size: calc(var(--w) * 0.9); font-weight: bold;
        }
        .small { width: 36px !important; height: 50px !important; font-size: 30px !important; }
        .sep { font-size: 30px; color: #555; line-height: 50px; }
    </style>
</head>
<body>
    <div class="board">
        <div class="screw tl"></div><div class="screw tr"></div>
        <div class="screw bl"></div><div class="screw br"></div>
        <div id="m-row" class="row"></div>
        <div id="d-row" class="row" style="margin-top:20px"></div>
        <div id="t-row" class="row" style="margin-top:10px"></div>
    </div>
    <script>
        var txt = "REPLACE_TEXT";
        var stay = REPLACE_STAY;
        var mem = {};

        function update(id, val) {
            var el = document.getElementById(id);
            if (!el || mem[id] === val) return;
            el.innerText = val === " " ? "\\u00A0" : val;
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
            var count = Math.max(8, Math.min(12, txt.length));
            document.documentElement.style.setProperty('--w', Math.floor(700/count) + 'px');
            
            document.getElementById('m-row').innerHTML = Array.from({length:count}, (_,i) => '<div class="card" id="m'+i+'"></div>').join('');
            document.getElementById('row-msg'); // 佔位
            document.getElementById('d-row').innerHTML = Array.from({length:11}, (_,i) => '<div class="card small" id="d'+i+'"></div>').join('');
            document.getElementById('t-row').innerHTML = '<div class="card small" id="t0"></div><div class="card small" id="t1"></div><div class="sep">:</div><div class="card small" id="t2"></div><div class="card small" id="t3"></div><div class="sep">:</div><div class="card small" id="t4"></div><div class="card small" id="t5"></div>';
            
            var pages = [];
            for (var k=0; k<txt.length; k+=count) pages.push(txt.substring(k, k+count).padEnd(count, ' '));
            
            var pIdx = 0;
            var rot = function() {
                if(pages.length > 0) {
                    pages[pIdx].split('').forEach((c, i) => update('m'+i, c));
                    pIdx = (pIdx + 1) % pages.length;
                }
            };
            rot(); tick(); setInterval(tick, 1000);
            if(pages.length > 1) setInterval(rot, stay * 1000);
        };
    </script>
</body>
</html>"""

    # 取代佔位符並編碼
    final_html = html_content.replace("REPLACE_TEXT", t_val).replace("REPLACE_STAY", s_val)
    b64_html = base64.b64encode(final_html.encode('utf-8')).decode('utf-8')
    data_uri = f"data:text/html;base64,{b64_html}"

    # 使用 iframe 渲染，避免 Streamlit 檢查內容字串
    components.iframe(data_uri, height=850, scrolling=False, key=f"f_{int(time.time())}")
