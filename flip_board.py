import streamlit.components.v1 as components

def render_flip_board(text, stay_sec=4.0):
    # 確保輸入是標準字串
    t_val = str(text).upper()
    
    # 使用最基礎的 HTML 結構，減少解析壓力
    # 我們將 CSS 和 JS 分開處理
    css = """
    <style>
        body { background: #1a1a1a; color: white; font-family: monospace; display: flex; justify-content: center; margin: 0; padding: 20px; }
        .board { background: #222; padding: 40px; border-radius: 20px; border: 2px solid #333; position: relative; }
        .card { background: #000; color: #fff; font-size: 40px; padding: 10px; margin: 2px; border-radius: 5px; display: inline-block; min-width: 40px; text-align: center; border: 1px solid #444; }
        .screw { position: absolute; width: 12px; height: 12px; background: #444; border-radius: 50%; }
        .tl { top: 10px; left: 10px; } .tr { top: 10px; right: 10px; }
        .bl { bottom: 10px; left: 10px; } .br { bottom: 10px; right: 10px; }
    </style>
    """
    
    # JS 部分：直接在 JavaScript 內部處理文字，避免 Python 替換大括號出錯
    js_code = f"""
    <script>
        window.onload = function() {{
            var text = "{t_val}";
            var container = document.getElementById("m");
            var html = "";
            for(var i=0; i<text.length; i++) {{
                var c = text[i] === " " ? "&nbsp;" : text[i];
                html += '<div class="card">' + c + '</div>';
            }}
            container.innerHTML = html;
        }};
    </script>
    """
    
    full_html = f"""
    <html>
    <head>{css}</head>
    <body>
        <div class="board">
            <div class="screw tl"></div><div class="screw tr"></div>
            <div class="screw bl"></div><div class="screw br"></div>
            <div id="m"></div>
        </div>
        {js_code}
    </body>
    </html>
    """
    
    # 這裡使用固定的 key，防止重新渲染時重複創建 iframe
    components.html(full_html, height=300, key="flip_stable_v1")
