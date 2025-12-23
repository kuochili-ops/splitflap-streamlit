import streamlit.components.v1 as components
import time

def render_flip_board(text, stay_sec=4.0):
    t_val = str(text).upper()
    try:
        s_val = str(float(stay_sec))
    except:
        s_val = "4.0"

    # 使用最單純的字串定義，確保不含任何會觸發 TypeError 的二進位或隱藏字元
    css = ".board { position: relative; background: #222; border-radius: 20px; padding: 40px; border: 1px solid #444; text-align: center; }"
    css += ".card { background: #000; color: #fff; padding: 10px; border-radius: 4px; display: inline-block; margin: 2px; font-family: monospace; font-size: 40px; min-width: 40px; }"
    css += ".screw { position: absolute; width: 12px; height: 12px; background: #555; border-radius: 50%; }"
    css += ".tl { top: 10px; left: 10px; } .tr { top: 10px; right: 10px; } .bl { bottom: 10px; left: 10px; } .br { bottom: 10px; right: 10px; }"
    
    html_template = """
    <html>
    <head>
        <style>
            body { background: #1a1a1a; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            REPLACE_CSS
        </style>
    </head>
    <body>
        <div class="board">
            <div class="screw tl"></div><div class="screw tr"></div>
            <div class="screw bl"></div><div class="screw br"></div>
            <div id="m"></div>
        </div>
        <script>
            var t = "REPLACE_TEXT";
            var container = document.getElementById("m");
            function draw() {
                var h = "";
                for(var i=0; i<t.length; i++) {
                    h += '<div class="card">' + (t[i] === " " ? "&nbsp;" : t[i]) + '</div>';
                }
                container.innerHTML = h;
            }
            draw();
        </script>
    </body>
    </html>
    """
    
    final_html = html_template.replace("REPLACE_CSS", css).replace("REPLACE_TEXT", t_val)
    
    # 這裡的 key 必須是穩定的字串，不要每次 rerun 都變動
    components.html(final_html, height=400, scrolling=False, key="static_board_v1")
