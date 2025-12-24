import streamlit.components.v1 as components
import json

def render_flip_board(json_text_list, stay_sec=7.0):
    bg_img = "https://upload.wikimedia.org/wikipedia/en/2/21/Girl_with_Balloon.jpg"
    
    # 這裡將資料轉換為 JSON 字串，安全注入 JavaScript
    js_data = json.dumps(json_text_list)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <style>
            * {{ box-sizing: border-box; }}
            html, body {{ 
                height: 100vh; width: 100vw; margin: 0; padding: 0; 
                overflow: hidden; background-color: #dcdcdc; 
                display: flex; justify-content: center; align-items: flex-start;
                font-family: "Impact", "Microsoft JhengHei", sans-serif;
            }}
            .graffiti-wall {{ 
                position: fixed; bottom: 0; left: 0; width: 100%; height: 50vh; 
                background-image: url('{bg_img}'); background-repeat: no-repeat; 
                background-position: center bottom; background-size: contain; z-index: 1; 
            }}
            .acrylic-board {{ 
                position: relative; width: 92vw; max-width: 900px; margin-top: 3vh; padding: 40px 20px; 
                background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(12px); 
                border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 20px; 
                display: flex; flex-direction: column; align-items: center; gap: 15px; 
                box-shadow: 0 20px 50px rgba(0,0,0,0.15); z-index: 10; 
            }}
            .row-container {{ display: flex; gap: 12px; perspective: 1000px; justify-content: center; width: 100%; }}
            .card {{ background: #1a1a1a; border-radius: 6px; position: relative; overflow: hidden; color: white; display: flex; align-items: center; justify-content: center; }}
            .msg-unit {{ width: var(--msg-w); height: calc(var(--msg-w) * 1.4); font-size: calc(var(--msg-w) * 0.9); }}
            .small-unit {{ width: 34px; height: 50px; font-size: 30px; }}
            .separator {{ font-size: 30px; color: #444; font-weight: bold; line-height: 50px; padding: 0 2px; }}
            .panel {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; }}
            .top-p {{ top: 0; border-bottom: 1px solid rgba(0,0,0,0.6); align-items: flex-end; }}
            .bottom-p {{ bottom: 0; align-items: flex-start; }}
            .text-node {{ position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 1; }}
            .top-p .text-node {{ bottom: -100%; }} .bottom-p .text-node {{ top: -100%; }}
            .leaf-node {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 20; transform-origin: bottom; transition: transform 0.1s linear; transform-style: preserve-3d; }}
            .leaf-side {{ position: absolute; inset: 0; backface-visibility: hidden; background: #1a1a1a; display: flex; justify-content: center; overflow: hidden; }}
            .side-back {{ transform: rotateX(-180deg); }}
            .flipping .leaf-node {{ transform: rotateX(-180deg); }}
            .screw {{ position: absolute; width: 14px; height: 14px; background: radial-gradient(circle at 30% 30%, #eee, #444); border-radius: 50%; border: 1px solid #333; }}
            .s-tl {{ top: 12px; left: 12px; }} .s-tr {{ top: 12px; right: 12px; }} .s-bl {{ bottom: 12px; left: 12px; }} .s-br {{ bottom: 12px; right: 12px; }}
        </style>
    </head>
    <body>
        <div class="graffiti-wall"></div>
        <div class="acrylic-board">
            <div class="screw s-tl"></div><div class="screw s-tr"></div>
            <div id="row-msg" class="row-container"></div>
            <div id="row-date" class="row-container" style="margin-top: 5px;"></div>
            <div id="row-clock" class="row-container"></div>
            <div class="screw s-bl"></div><div class="screw s-br"></div>
        </div>
        <script>
            const newsArray = JSON.parse('{js_data}');
            let currentNewsIdx = 0, currentPageIdx = -1, currentPages = [], currentFlapCount = 0;
            let CN_POOL = [], AZ_POOL = " ABCDEFGHIJKLMNOPQRSTUVWXYZ".split(""), NUM_POOL = "0123456789".split("");
            let memory = {{}}, isBusy = {{}};

            function getMsgPages(text) {{
                const len = text.length;
                if (len <= 16) {{
                    const flapCount = Math.ceil(len / 2);
                    return [text.substring(0, flapCount).split(""), text.substring(flapCount).split("")];
                }}
                let p = [];
                for (let i = 0; i < len; i += 8) {{ p.push(text.substring(i, i + 8).split("")); }}
                return p;
            }}

            function updateLayout(flapCount) {{
                const board = document.querySelector(".acrylic-board");
                const calculatedW = Math.min(180, Math.floor((board.offsetWidth - 100) / flapCount) - 10);
                document.documentElement.style.setProperty("--msg-w", calculatedW + "px");
                const msgRow = document.getElementById("row-msg");
                msgRow.innerHTML = "";
                for(let i=0; i<flapCount; i++) {{
                    const div = document.createElement("div");
                    div.className = "card msg-unit"; div.id = "m" + i;
                    msgRow.appendChild(div);
                }}
                memory = {{}};
            }}

            function performFlip(id, nVal, pVal) {{
                const el = document.getElementById(id); if(!el) return;
                const n = nVal || "&nbsp;", p = pVal || "&nbsp;";
                el.classList.remove("flipping");
                el.innerHTML = `<div class="panel top-p"><div class="text-node">${{n}}</div></div>` +
                               `<div class="panel bottom-p"><div class="text-node">${{p}}</div></div>` +
                               `<div class="leaf-node"><div class="leaf-side top-p"><div class="text-node">${{p}}</div></div>` +
                               `<div class="leaf-side side-back bottom-p"><div class="text-node">${{n}}</div></div></div>`;
                void el.offsetWidth; el.classList.add("flipping");
            }}

            async function smartUpdate(id, target) {{
                let tStr = String(target); if (memory[id] === tStr || isBusy[id]) return;
                isBusy[id] = true;
                let curStr = memory[id] || " ", pool = AZ_POOL;
                if (/[0-9]/.test(tStr)) pool = NUM_POOL;
                else if (/[\\u4E00-\\u9FFF]/.test(tStr)) pool = CN_POOL;
                let curIdx = pool.indexOf(curStr); if (curIdx === -1) curIdx = 0;
                while (curStr !== tStr) {{
                    let prev = curStr; curIdx = (curIdx + 1) % pool.length; curStr = pool[curIdx];
                    performFlip(id, curStr, prev); await new Promise(r => setTimeout(r, 70));
                }}
                memory[id] = tStr; isBusy[id] = false;
            }}

            const rotateLogic = () => {{
                if (currentPageIdx < currentPages.length - 1) {{ currentPageIdx++; }} 
                else {{
                    currentNewsIdx = (currentNewsIdx + 1) % newsArray.length;
                    currentPageIdx = 0;
                    const fullText = newsArray[currentNewsIdx];
                    currentPages = getMsgPages(fullText);
                    const newFlapCount = Math.max(...currentPages.map(p => p.length));
                    if (newFlapCount !== currentFlapCount) {{ currentFlapCount = newFlapCount; updateLayout(currentFlapCount); }}
                    CN_POOL = [...new Set(fullText.replace(/[A-Z0-9\\s]/g, "").split(""))];
                }}
                const page = currentPages[currentPageIdx];
                for(let i=0; i < currentFlapCount; i++) {{ setTimeout(() => smartUpdate("m" + i, page[i] || " "), i * 100); }}
            }};

            window.onload = () => {{
                const dateRow = document.getElementById("row-date");
                for(let i=0; i<11; i++) {{
                    const div = document.createElement("div"); div.className = "card small-unit"; div.id = "d" + i;
                    dateRow.appendChild(div);
                }}
                document.getElementById("row-clock").innerHTML = '<div class="card small-unit" id="h0"></div><div class="card small-unit" id="h1"></div><div class="separator">:</div><div class="card small-unit" id="tm0"></div><div class="card small-unit" id="tm1"></div><div class="separator">:</div><div class="card small-unit" id="ts0"></div><div class="card small-unit" id="ts1"></div>';
                rotateLogic();
                setInterval(() => {{
                    const n = new Date();
                    const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"], days = ["SUN","MON","TUE","WED","THU","FRI","SAT"];
                    const dStr = months[n.getMonth()] + " " + String(n.getDate()).padStart(2,"0") + " " + days[n.getDay()];
                    dStr.split("").forEach((c, i) => smartUpdate("d" + i, c));
                    const time = String(n.getHours()).padStart(2,"0") + String(n.getMinutes()).padStart(2,"0") + String(n.getSeconds()).padStart(2,"0");
                    ["h0","h1","tm0","tm1","ts0","ts1"].forEach((id, i) => smartUpdate(id, time[i]));
                }}, 1000);
                setInterval(rotateLogic, {stay_sec * 1000});
            }};
        </script>
    </body>
    </html>
    """
    # 使用 components.html 代替 iframe
    components.html(html_content, height=800, scrolling=False)
