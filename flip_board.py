import streamlit.components.v1 as components

def render_flip_board(text, stay_sec=4.0):
    # 1. 確保傳入值為純淨的字串與浮點數
    clean_text = str(text).upper()
    try:
        clean_stay = str(float(stay_sec))
    except:
        clean_stay = "4.0"

    # 2. 定義 HTML 模板 (使用 REPLACE_ 標記，避開 Python 的 {} 語法)
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { 
                background-color: #1a1a1a; 
                margin: 0; 
                padding: 20px; 
                display: flex; 
                justify-content: center; 
                font-family: "Courier New", Courier, monospace;
            }
            .board-frame {
                position: relative; 
                background: linear-gradient(145deg, #222, #111);
                padding: 60px 40px; 
                border-radius: 25px;
                border: 2px solid #333; 
                box-shadow: 0 30px 60px rgba(0,0,0,0.7); 
                text-align: center;
                max-width: 90vw;
            }
            /* 工業風螺絲 */
            .screw { 
                position: absolute; width: 14px; height: 14px; 
                background: radial-gradient(circle at 30% 30%, #555, #222); 
                border-radius: 50%; box-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            }
            .screw::before { 
                content: '+'; position: absolute; top: 50%; left: 50%; 
                transform: translate(-50%, -50%); color: rgba(0,0,0,0.5); 
                font-size: 12px; font-weight: bold; 
            }
            .tl { top: 15px; left: 15px; } .tr { top: 15px; right: 15px; }
            .bl { bottom: 15px; left: 15px; } .br { bottom: 15px; right: 15px; }

            .card-row { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; }
            .card {
                background: #050505; color: #ffffff; font-size: 48px; 
                font-weight: bold; width: 50px; height: 70px;
                line-height: 70px; border-radius: 6px; 
                border: 1px solid #333; box-shadow: inset 0 0 10px rgba(255,255,255,0.05);
            }
        </style>
    </head>
    <body>
        <div class="board-frame">
            <div class="screw tl"></div><div class="screw tr"></div>
            <div class="screw bl"></div><div class="screw br"></div>
            <div id="display" class="card-row"></div>
        </div>
        <script>
            var content = "REPLACE_TEXT";
            var container = document.getElementById("display");
            var output = "";
            for(var i=0; i<content.length; i++) {
                var c = content[i] === " " ? "&nbsp;" : content[i];
                output += '<div class="card">' + c + '</div>';
            }
            container.innerHTML = output;
        </script>
    </body>
    </html>
    """
    
    # 3. 執行字串替換
    final_render = html_template.replace("REPLACE_TEXT", clean_text)
    
    # 4. 固定高寬與 Key
    components.html(final_render, height=350, scrolling=False, key="flip_v5_stable")
