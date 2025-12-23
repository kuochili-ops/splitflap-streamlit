import streamlit.components.v1 as components
import base64

def render_flip_board(text, stay_sec=4.0):
    t_val = str(text).upper()
    try:
        s_val = str(float(stay_sec))
    except:
        s_val = "4.0"

    # 完整的 HTML/CSS/JS 程式碼，包含翻牌動畫與時鐘
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ background: #1a1a1a; margin: 0; padding: 20px; display: flex; justify-content: center; font-family: sans-serif; overflow: hidden; }}
            .board {{
                position: relative; background: #222; padding: 50px 30px; border-radius: 30px; 
                border: 2px solid #444; box-shadow: 0 40px 100px rgba(0,0,0,0.5);
                display: flex; flex-direction: column; align-items: center; gap: 20px;
            }}
            /* 十字螺絲 */
            .screw {{ position: absolute; width: 14px; height: 14px; background: #555; border-radius: 50%; }}
            .screw::before {{ content: '+'; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #333; font-size: 12px; font-weight: bold; }}
            .tl {{ top: 20px; left: 20px; }} .tr {{ top: 20px; right: 20px; }}
            .bl {{ bottom: 20px; left: 20px; }} .br {{ bottom: 20px; right: 20px; }}

            .row {{ display: flex; gap: 6px; perspective: 1000px; }}
            .card {{ 
                background: #000; border-radius: 6px; color: #fff; position: relative;
                width: 50px; height: 70px; font-size: 45px; font-weight: bold;
                display: flex; align-items: center; justify-content: center;
                box-shadow: 0 5px 15px rgba(0,0,0,0.3); overflow: hidden;
            }}
            .small {{ width: 35px; height: 50px; font-size: 30px; }}
            .sep {{ color: #555; font-size: 30px; line-height: 50px; font-weight: bold; }}
            
            /* 翻牌過渡動畫 */
            .flip-up {{ animation: flip 0.4s ease-in; }}
            @keyframes flip {{
                0% {{ transform: rotateX(0deg); }}
                100% {{ transform: rotateX(-180deg); }}
            }}
        </style>
    </head>
    <body>
        <div class="board">
            <div class="screw tl"></div><div class="screw tr"></div>
            <div class="screw bl"></div><div class="screw br"></div>
            <div id="msg-row" class="row"></div>
            <div id="date-row" class="row" style="margin-top:10px"></div>
            <div id="clock-row" class="row"></div>
        </div>
        <script>
            var fullText = "{t_val}";
            var stayTime = {s_val};
            var mem = {{}};

            function updateCard(id, val) {{
                var el = document.getElementById(id);
                if (!el || mem[id] === val) return;
                
                // 動畫效果：移除並重新加上動畫類名
                el.classList.remove('flip-up');
                void el.offsetWidth; 
                el.innerText = (val === " " ? "\\u00A0" : val);
                el.classList.add('flip-up');
                mem[id] = val;
            }}

            function tick() {{
                var n = new Date();
                // 日期更新
                var dStr = n.toLocaleDateString('en-US', {{month:'short', day:'2-digit', weekday:'short'}}).toUpperCase().replace(/,/g,'');
                dStr.split('').forEach((c, i) => updateCard('d'+i, c));
                // 時間更新
                var h = n.getHours().toString().padStart(2,'0'), m = n.getMinutes().toString().padStart(2,'0'), s = n.getSeconds().toString().padStart(2,'0');
                (h+m+s).split('').forEach((c, i) => updateCard('t'+i, c));
            }}

            window.onload = function() {{
                // 初始化容器
                var count = Math.max(8, fullText.length);
                document.getElementById('msg-row').innerHTML = Array.from({{length:count}}, (_,i) => '<div class="card" id="m'+i+'"></div>').join('');
                document.getElementById('date-row').innerHTML = Array.from({{length:11}}, (_,i) => '<div class="card small" id="d'+i+'"></div>').join('');
                document.getElementById('clock-row').innerHTML = '<div class="card small" id="t0"></div><div class="card small" id="t1"></div><div class="sep">:</div><div class="card small" id="t2"></div><div class="card small" id="t3"></div><div class="sep">:</div><div class="card small" id="t4"></div><div class="card small" id="t5"></div>';
                
                // 訊息翻轉邏輯
                var pages = [];
                for (var k=0; k<fullText.length; k+=count) pages.push(fullText.substring(k, k+count).padEnd(count, ' '));
                if(pages.length === 0) pages.push(" ".repeat(count));

                var pIdx = 0;
                var rotateMsg = function() {{
                    pages[pIdx].split('').forEach((c, i) => setTimeout(() => updateCard('m'+i, c), i*50));
                    pIdx = (pIdx + 1) % pages.length;
                }};

                rotateMsg(); 
                tick(); 
                setInterval(tick, 1000);
                if(pages.length > 1) setInterval(rotateMsg, stayTime * 1000);
            }};
        </script>
    </body>
    </html>
    """
    
    # 進行 Base64 編碼隔離
    b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    data_uri = f"data:text/html;base64,{{b64}}"
    
    # 使用 iframe 渲染
    components.iframe(data_uri, height=450, scrolling=False, key=f"flip_active_{{t_val[:3]}}")
