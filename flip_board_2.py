import streamlit.components.v1 as components
import json

def render_flip_board(news_list, stay_sec=7.0):
    bg_img = "https://upload.wikimedia.org/wikipedia/en/2/21/Girl_with_Balloon.jpg"
    js_data = json.dumps(news_list)
    
    # 使用 f-string，並將所有 JS 的 { } 寫成 {{ }} 以免 Python 報錯
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {{ box-sizing: border-box; }}
            html, body {{ height: 100vh; margin: 0; padding: 0; overflow: hidden; background: #dcdcdc; }}
            body {{ display: flex; flex-direction: column; align-items: center; justify-content: flex-start; font-family: sans-serif; }}
            
            .board {{ 
                position: relative; width: 90vw; max-width: 850px; margin-top: 30px; 
                padding: 40px 20px; background: rgba(255,255,255,0.2); backdrop-filter: blur(10px);
                border-radius: 20px; border: 1px solid rgba(255,255,255,0.3); z-index: 10;
                display: flex; flex-direction: column; align-items: center; gap: 10px;
            }}
            .row {{ display: flex; gap: 8px; justify-content: center; min-height: 80px; width: 100%; }}
            
            /* 基礎翻板樣式 */
            .card {{ 
                background: #1a1a1a; color: white; border-radius: 6px; 
                display: flex; align-items: center; justify-content: center;
                width: 45px; height: 65px; font-size: 40px; font-weight: bold;
                font-family: 'Courier New', Courier, monospace;
                border: 1px solid #333;
                box-shadow: 0 4px 8px rgba(0,0,0,0.5);
            }}

            /* 簡單跳動動畫 */
            @keyframes flipUpdate {{
                0% {{ transform: rotateX(0deg); background: #1a1a1a; }}
                50% {{ transform: rotateX(90deg); background: #333; }}
                100% {{ transform: rotateX(0deg); background: #1a1a1a; }}
            }}
            .anim {{ animation: flipUpdate 0.4s ease-in-out; }}

            .bg {{ position: fixed; bottom: 0; width: 100%; height: 50vh; background: url('{bg_img}') no-repeat center bottom; background-size: contain; z-index: 1; }}
            .time-row {{ margin-top: 20px; scale: 0.8; opacity: 0.8; }}
        </style>
    </head>
    <body>
        <div class="bg"></div>
        <div class="board">
            <div id="m-row" class="row"></div>
            <div id="t-row" class="row time-row"></div>
        </div>

        <script>
            const news = {js_data};
            let idx = 0;

            function drawText(text) {{
                const row = document.getElementById("m-row");
                row.innerHTML = "";
                
                // 限制最大顯示字數，避免爆框
                const safeText = text.substring(0, 12);
                
                for (let i = 0; i < safeText.length; i++) {{
                    const char = safeText[i];
                    const div = document.createElement("div");
                    div.className = "card anim"; // 每次更換文字都觸發一次動畫
                    div.textContent = char;
                    // 讓每個字稍微錯開一點點動畫時間
                    div.style.animationDelay = (i * 0.05) + "s";
                    row.appendChild(div);
                }}
            }}

            function updateTime() {{
                const now = new Date();
                const h = String(now.getHours()).padStart(2, '0');
                const m = String(now.getMinutes()).padStart(2, '0');
                const s = String(now.getSeconds()).padStart(2, '0');
                const tRow = document.getElementById("t-row");
                tRow.innerHTML = "";
                const timeStr = h + ":" + m + ":" + s;
                for (let c of timeStr) {{
                    const div = document.createElement("div");
                    div.className = "card";
                    div.style.width = "30px";
                    div.style.height = "45px";
                    div.style.fontSize = "24px";
                    div.textContent = c;
                    tRow.appendChild(div);
                }}
            }}

            function nextNews() {{
                drawText(news[idx]);
                idx = (idx + 1) % news.length;
            }}

            window.onload = () => {{
                nextNews();
                updateTime();
                setInterval(updateTime, 1000);
                setInterval(nextNews, {stay_sec * 1000});
            }};
        </script>
    </body>
    </html>
    """
    components.html(html_content, height=600)
