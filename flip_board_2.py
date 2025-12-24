import streamlit.components.v1 as components
import json

def render_flip_board(news_list, stay_sec=7.0):
    bg_img = "https://upload.wikimedia.org/wikipedia/en/2/21/Girl_with_Balloon.jpg"
    js_data = json.dumps(news_list)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {{ box-sizing: border-box; }}
            html, body {{ height: 100vh; margin: 0; padding: 0; overflow: hidden; background: #dcdcdc; }}
            body {{ display: flex; flex-direction: column; align-items: center; justify-content: flex-start; font-family: "Impact", sans-serif; }}
            
            .board {{ 
                position: relative; width: 92vw; max-width: 850px; margin-top: 5vh; 
                padding: 40px 20px; background: rgba(255,255,255,0.2); backdrop-filter: blur(10px);
                border-radius: 20px; border: 1px solid rgba(255,255,255,0.3); z-index: 10;
                display: flex; flex-direction: column; align-items: center; gap: 15px;
                box-shadow: 0 20px 50px rgba(0,0,0,0.1);
            }}
            .row {{ display: flex; gap: 10px; justify-content: center; perspective: 1000px; }}
            
            /* 經典翻牌容器 */
            .card {{ 
                position: relative; width: 50px; height: 75px; 
                background: #1a1a1a; color: white; border-radius: 6px;
                font-size: 50px; text-align: center; line-height: 75px;
            }}
            
            /* 分割線 */
            .card::after {{
                content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 1px;
                background: rgba(0,0,0,0.6); z-index: 5;
            }}

            /* 翻轉動畫核心 */
            @keyframes flipDown {{
                0% {{ transform: rotateX(0deg); }}
                100% {{ transform: rotateX(-180deg); }}
            }}
            
            .flipping {{
                animation: flipDown 0.6s ease-in-out;
                transform-style: preserve-3d;
            }}

            .bg {{ position: fixed; bottom: 0; width: 100%; height: 50vh; background: url('{bg_img}') no-repeat center bottom; background-size: contain; z-index: 1; }}
            .time-unit {{ width: 35px; height: 50px; font-size: 30px; line-height: 50px; opacity: 0.8; }}
            .sep {{ font-size: 30px; color: #444; padding: 0 5px; line-height: 50px; }}
        </style>
    </head>
    <body>
        <div class="bg"></div>
        <div class="board">
            <div id="m-row" class="row"></div>
            <div id="t-row" class="row" style="margin-top:20px;"></div>
        </div>

        <script>
            const news = {js_data};
            let idx = 0;

            function createCard(char, isTime=false) {{
                const div = document.createElement("div");
                div.className = isTime ? "card time-unit" : "card";
                div.textContent = char;
                return div;
            }}

            function updateNews() {{
                const row = document.getElementById("m-row");
                const text = news[idx] || "";
                const chars = text.substring(0, 10).split(""); // 限制每行長度
                
                row.innerHTML = "";
                chars.forEach((c, i) => {{
                    const card = createCard(c);
                    row.appendChild(card);
                    // 延遲觸發翻轉動作，形成波浪感
                    setTimeout(() => {{
                        card.classList.add("flipping");
                    }}, i * 100);
                }});
                
                idx = (idx + 1) % news.length;
            }}

            function updateTime() {{
                const now = new Date();
                const timeStr = String(now.getHours()).padStart(2,'0') + ":" + 
                                String(now.getMinutes()).padStart(2,'0') + ":" + 
                                String(now.getSeconds()).padStart(2,'0');
                const tRow = document.getElementById("t-row");
                tRow.innerHTML = "";
                for(let c of timeStr) {{
                    if(c === ":") {{
                        const s = document.createElement("div"); s.className="sep"; s.textContent=":"; tRow.appendChild(s);
                    }} else {{
                        tRow.appendChild(createCard(c, true));
                    }}
                }}
            }}

            window.onload = () => {{
                updateNews();
                updateTime();
                setInterval(updateTime, 1000);
                setInterval(updateNews, {stay_sec * 1000});
            }};
        </script>
    </body>
    </html>
    """
    components.html(html_content, height=600)
