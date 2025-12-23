import streamlit.components.v1 as components

def render_flip_board(text, stay_sec=4.0):
    # 確保參數是純粹的型別
    clean_text = str(text).upper()
    clean_stay = str(float(stay_sec))

    # 使用完全靜態的字串
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { background-color: #1a1a1a; margin: 0; padding: 20px; display: flex; justify-content: center; font-family: monospace; }
            .board-container {
                position: relative; background: #222; padding: 50px 30px; border-radius: 20px;
                border: 2px solid #333; box-shadow: 0 20px 50px rgba(0,0,0,0.5); text-align: center;
            }
            .card {
                background: #000; color: #fff; font-size: 45px; padding: 10px;
                margin: 3px; border-radius: 5px; display: inline-block; min-width: 45px;
                border: 1px solid #444;
            }
            .screw { position: absolute; width: 15px; height: 15px; background: #444; border-radius: 50%; }
            .tl { top: 15px; left: 15px; } .tr { top: 15px; right: 15px; }
            .bl { bottom: 15px; left: 15px; } .br { bottom: 15px; right: 15px; }
        </style>
    </head>
    <body>
        <div class="board-container">
            <div class="screw tl"></div><div class="screw tr"></div>
            <div class="screw bl"></div><div class="screw br"></div>
            <div id="display"></div>
        </div>
        <script>
            var content = "REPLACE_TEXT";
            var target = document.getElementById("display");
            var html = "";
            for(var i=0; i<content.length; i++) {
                var char = content[i] === " " ? "&nbsp;" : content[i];
                html += '<div class="card">' + char + '</div>';
            }
            target.innerHTML = html;
        </script>
    </body>
    </html>
    """
    
    # 進行最終取代
    final_render = html_code.replace("REPLACE_TEXT", clean_text)
    
    # 固定 Key 值，減少 Rerun 時的組件重建壓力
    components.html(final_render, height=350, scrolling=False, key="main_board_display")
