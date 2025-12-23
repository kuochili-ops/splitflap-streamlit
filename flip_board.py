import streamlit.components.v1 as components
import base64

def render_flip_board(text, stay_sec=4.0):
    t_val = str(text).upper()
    
    # 這裡放所有的 HTML/CSS/JS 邏輯
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ background: #1a1a1a; margin: 0; padding: 20px; display: flex; justify-content: center; font-family: monospace; overflow: hidden; }}
            .board {{
                position: relative; background: #222; padding: 40px; border-radius: 20px; 
                border: 2px solid #333; box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            }}
            .card {{ 
                background: #000; color: #fff; font-size: 40px; padding: 10px; 
                margin: 2px; border-radius: 5px; display: inline-block; 
                min-width: 40px; text-align: center; border: 1px solid #444; 
            }}
            .screw {{ position: absolute; width: 12px; height: 12px; background: #444; border-radius: 50%; }}
            .tl {{ top: 10px; left: 10px; }} .tr {{ top: 10px; right: 10px; }}
            .bl {{ bottom: 10px; left: 10px; }} .br {{ bottom: 10px; right: 10px; }}
        </style>
    </head>
    <body>
        <div class="board">
            <div class="screw tl"></div><div class="screw tr"></div>
            <div class="screw bl"></div><div class="screw br"></div>
            <div id="m"></div>
        </div>
        <script>
            var text = "{t_val}";
            var container = document.getElementById("m");
            var html = "";
            for(var i=0; i<text.length; i++) {{
                var c = text[i] === " " ? "&nbsp;" : text[i];
                html += '<div class="card">' + c + '</div>';
            }}
            container.innerHTML = html;
        </script>
    </body>
    </html>
    """
    
    # 將字串轉為 Base64 編碼，防止任何字元引起 Python 解析錯誤
    b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    data_uri = f"data:text/html;base64,{b64}"
    
    # 使用 iframe 載入 URI，這在 Python 3.13 是最穩定的方式
    components.iframe(data_uri, height=300, scrolling=False)
