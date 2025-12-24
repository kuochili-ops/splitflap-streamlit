import streamlit.components.v1 as components
import json

def render_flip_board(news_list, stay_sec=8.0):
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
                position: relative; width: 95vw; max-width: 900px; margin-top: 40px; 
                padding: 40px 20px; background: rgba(255,255,255,0.2); backdrop-filter: blur(10px);
                border-radius: 20px; border: 1px solid rgba(255,255,255,0.3); z-index: 10;
                display: flex; flex-direction: column; align-items: center; gap: 15px;
            }}
            .row {{ display: flex; gap: 6px; justify-content: center; perspective: 1000px; }}
            
            /* 機械翻牌核心樣式 */
            .card {{ 
                position: relative; width: 45px; height: 70px; 
                background: #1a1a1a; color: white; border-radius: 4px;
                font-size: 45px; font-weight: bold;
            }}

            .panel {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; }}
            .top-p {{ top: 0; border-bottom: 1px solid rgba(0,0,0,0.5); align-items: flex-end; border-radius: 4px 4px 0 0; }}
            .bottom-p {{ bottom: 0; align-items: flex-start; border-radius: 0 0 4px 4px; }}
            
            .text-node {{ position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 0; }}
            .top-p .text-node {{ bottom: -100%; }} 
            .bottom-p .text-node {{ top: -100%; }}

            /* 翻轉葉片 */
            .leaf-node {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform 0.4s ease-in; transform-style: preserve-3d; }}
            .leaf-side {{ position: absolute; inset: 0; backface-visibility: hidden; background: #1a1a1a; display: flex; justify-content: center; overflow: hidden; }}
            .side-back {{ transform: rotateX(-180deg); }}
            .flipping .leaf-node {{ transform: rotateX(-180deg); }}

            .bg {{ position: fixed; bottom: 0; width: 100%; height: 50vh; background: url('{bg_img}') no-repeat center bottom; background-size: contain; z-index: 1; }}
        </style>
    </head>
    <body>
        <div class="bg"></div>
        <div class="board">
            <div id="m-row" class="row"></div>
        </div>

        <script>
            const news = {js_data};
            let idx = 0;
            let currentText = "";

            function performFlip(el, nextChar, prevChar) {{
                if (!el) return;
                el.classList.remove('flipping');
                const n = nextChar || " ", p = prevChar || " ";
                
                el.innerHTML = `
                    <div class="panel top-p"><div class="text-node">${{n}}</div></div>
                    <div class="panel bottom-p"><div class="text-node">${{p}}</div></div>
                    <div class="leaf-node">
                        <div class="leaf-side top-p"><div class="text-node">${{p}}</div></div>
                        <div class="leaf-side side-back bottom-p"><div class="text-node">${{n}}</div></div>
                    </div>`;
                
                requestAnimationFrame(() => {{
                    void el.offsetWidth;
                    el.classList.add('flipping');
                }});
            }}

            async function updateNews() {{
                const row = document.getElementById("m-row");
                const nextText = (news[idx] || "").substring(0, 15).padEnd(15, " ");
                const oldText = currentText.padEnd(15, " ");
                
                // 初始化容器
                if (row.innerHTML === "") {{
                    for(let i=0; i<15; i++) {{
                        const div = document.createElement("div");
                        div.className = "card";
                        div.id = "c-" + i;
                        row.appendChild(div);
                    }}
                }}

                // 逐字翻轉
                for (let i = 0; i < 15; i++) {{
                    if (nextText[i] !== oldText[i]) {{
                        const el = document.getElementById("c-" + i);
                        performFlip(el, nextText[i], oldText[i]);
                        await new Promise(r => setTimeout(r, 80)); // 刷刷刷的延遲感
                    }}
                }}

                currentText = nextText;
                idx = (idx + 1) % news.length;
            }}

            window.onload = () => {{
                updateNews();
                setInterval(updateNews, {stay_sec * 1000});
            }};
        </script>
    </body>
    </html>
    """
    components.html(html_content, height=600)
