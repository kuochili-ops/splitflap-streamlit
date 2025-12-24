import streamlit.components.v1 as components
import json

def render_flip_board(news_list, stay_sec=7.0):
    bg_img = "https://upload.wikimedia.org/wikipedia/en/2/21/Girl_with_Balloon.jpg"
    # 將 Python List 轉為 JS 認識的字串
    js_data = json.dumps(news_list)
    
    # 這裡使用最穩定的字串替換，並確保大括號轉義
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {{ box-sizing: border-box; }}
            html, body {{ height: 100vh; margin: 0; padding: 0; overflow: hidden; background: #dcdcdc; }}
            body {{ display: flex; flex-direction: column; align-items: center; justify-content: flex-start; }}
            
            .board {{ 
                position: relative; width: 90vw; max-width: 800px; margin-top: 20px; 
                padding: 40px; background: rgba(255,255,255,0.2); backdrop-filter: blur(10px);
                border-radius: 20px; border: 1px solid rgba(255,255,255,0.3); z-index: 10;
                display: flex; flex-direction: column; align-items: center; gap: 15px;
            }}
            .row {{ display: flex; gap: 10px; justify-content: center; }}
            .card {{ 
                background: #1a1a1a; color: white; border-radius: 6px; 
                display: flex; align-items: center; justify-content: center;
                width: var(--cw); height: calc(var(--cw) * 1.4); font-size: calc(var(--cw) * 0.9);
                font-family: Impact, sans-serif;
            }}
            .small {{ width: 30px; height: 45px; font-size: 28px; }}
            .sep {{ font-size: 28px; color: #444; font-weight: bold; line-height: 45px; }}
            .bg {{ position: fixed; bottom: 0; width: 100%; height: 50vh; background: url('{bg_img}') no-repeat center bottom; background-size: contain; z-index: 1; }}
        </style>
    </head>
    <body>
        <div class="bg"></div>
        <div class="board">
            <div id="m-row" class="row"></div>
            <div id="d-row" class="row"></div>
            <div id="t-row" class="row"></div>
        </div>
        <script>
            const news = {js_data};
            let idx = 0;
            
            function update() {{
                const text = news[idx];
                const row = document.getElementById("m-row");
                row.innerHTML = "";
                
                // 決定翻板數量：16字以內分兩頁，大於16字每頁8板
                let displayChars = "";
                if (text.length <= 16) {{
                    const half = Math.ceil(text.length / 2);
                    displayChars = text.substring(0, half); // 這裡簡化邏輯測試
                }} else {{
                    displayChars = text.substring(0, 8);
                }}

                document.documentElement.style.setProperty("--cw", Math.min(100, 600/displayChars.length) + "px");
                
                for(let c of displayChars.split("")) {{
                    const div = document.createElement("div");
                    div.className = "card";
                    div.textContent = c;
                    row.appendChild(div);
                }}
                idx = (idx + 1) % news.length;
            }}

            window.onload = () => {{
                // 初始化時間列 (靜態展示)
                document.getElementById("t-row").innerHTML = '<div class="card small">1</div><div class="card small">2</div><div class="sep">:</div><div class="card small">0</div><div class="card small">0</div>';
                update();
                setInterval(update, {stay_sec * 1000});
            }};
        </script>
    </body>
    </html>
    """
    components.html(html_content, height=600)
