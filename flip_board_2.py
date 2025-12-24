import streamlit.components.v1 as components
import base64
import json

def render_flip_board(json_text_list, stay_sec=7.0):
    bg_img = "https://upload.wikimedia.org/wikipedia/en/2/21/Girl_with_Balloon.jpg"
    
    # 這裡加入 key 確保 Streamlit 內部緩存穩定
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            html, body { height: 100vh; overflow: hidden; background-color: #dcdcdc; }
            body { display: flex; justify-content: center; align-items: flex-start; font-family: "Impact", "Microsoft JhengHei", sans-serif; }
            
            /* 背景圖層固定，避免跳動 */
            .graffiti-wall { 
                position: fixed; bottom: 0; left: 0; width: 100%; height: 50vh; 
                background-image: url("BG_URL_PLACEHOLDER"); background-repeat: no-repeat; 
                background-position: center bottom; background-size: contain; z-index: 1;
                pointer-events: none;
            }
            
            .acrylic-board { 
                position: relative; width: 95vw; max-width: 900px; margin-top: 5vh; padding: 45px 25px; 
                background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px); 
                border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 20px; 
                display: flex; flex-direction: column; align-items: center; gap: 20px; 
                box-shadow: 0 30px 60px rgba(0,0,0,0.1); z-index: 10; 
            }

            .row-container { display: flex; gap: 8px; perspective: 1000px; justify-content: center; width: 100%; }
            .card { background: #1a1a1a; border-radius: 6px; position: relative; overflow: hidden; color: white; display: flex; align-items: center; justify-content: center; }
            .msg-unit { width: var(--msg-w); height: calc(var(--msg-w) * 1.4); font-size: calc(var(--msg-w) * 0.95); }
            
            /* 讓翻轉更平穩：增加時間與使用 ease-in-out */
            .panel { position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; }
            .top-p { top: 0; border-bottom: 1px solid rgba(0,0,0,0.5); align-items: flex-end; }
            .bottom-p { bottom: 0; align-items: flex-start; }
            .text-node { position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 1; }
            .top-p .text-node { bottom: -100%; } .bottom-p .text-node { top: -100%; }
            
            .leaf-node { position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 20; transform-origin: bottom; transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }
            .leaf-side { position: absolute; inset: 0; backface-visibility: hidden; background: #1a1a1a; display: flex; justify-content: center; overflow: hidden; }
            .side-back { transform: rotateX(-180deg); }
            .flipping .leaf-node { transform: rotateX(-180deg); }
        </style>
    </head>
    <body>
        <div class="graffiti-wall"></div>
        <div class="acrylic-board">
            <div id="row-msg" class="row-container"></div>
            <div id="row-date" class="row-container" style="margin-top: 10px;"></div>
            <div id="row-clock" class="row-container"></div>
        </div>

    <script>
        const newsArray = JSON.parse('JSON_DATA_PLACEHOLDER');
        let currentNewsIdx = 0;
        let currentPageIdx = -1;
        let currentPages = [];
        let currentFlapCount = 0;
        let memory = {};
        let isBusy = {};

        function performFlip(id, nVal, pVal) {
            const el = document.getElementById(id);
            if(!el) return;
            const n = nVal === " " ? "&nbsp;" : nVal;
            const p = pVal === " " ? "&nbsp;" : pVal;
            el.classList.remove("flipping");
            el.innerHTML = `<div class="panel top-p"><div class="text-node">${n}</div></div>` +
                           `<div class="panel bottom-p"><div class="text-node">${p}</div></div>` +
                           `<div class="leaf-node"><div class="leaf-side top-p"><div class="text-node">${p}</div></div>` +
                           `<div class="leaf-side side-back bottom-p"><div class="text-node">${n}</div></div></div>`;
            void el.offsetWidth; 
            el.classList.add("flipping");
        }

        async function smartUpdate(id, target) {
            let tStr = String(target);
            if (memory[id] === tStr) return;
            let oldStr = memory[id] || " ";
            memory[id] = tStr;
            performFlip(id, tStr, oldStr);
        }

        const rotateLogic = () => {
            if (currentPageIdx < currentPages.length - 1) {
                currentPageIdx++;
            } else {
                currentNewsIdx = (currentNewsIdx + 1) % newsArray.length;
                currentPageIdx = 0;
                const fullText = newsArray[currentNewsIdx];
                // 固定分頁邏輯，減少 DOM 結構變動導致的閃爍
                const flapCount = 12; 
                currentPages = [fullText.padEnd(flapCount, " ").substring(0, flapCount).split("")];
                if (currentFlapCount !== flapCount) {
                    currentFlapCount = flapCount;
                    updateLayout(flapCount);
                }
            }
            const page = currentPages[currentPageIdx];
            page.forEach((char, i) => {
                setTimeout(() => smartUpdate("m" + i, char), i * 50);
            });
        };

        function updateLayout(flapCount) {
            const board = document.querySelector(".acrylic-board");
            const calculatedW = Math.min(60, Math.floor((board.offsetWidth - 100) / flapCount));
            document.documentElement.style.setProperty("--msg-w", calculatedW + "px");
            const msgRow = document.getElementById("row-msg");
            msgRow.innerHTML = "";
            for(let i=0; i<flapCount; i++) {
                const div = document.createElement("div");
                div.className = "card msg-unit"; div.id = "m" + i;
                msgRow.appendChild(div);
            }
        }

        window.onload = () => {
            // 初始化時鐘結構
            document.getElementById("row-date").innerHTML = Array.from({length: 11}, (_, i) => `<div class="card small-unit" style="width:30px;height:45px;font-size:24px" id="d${i}"></div>`).join("");
            document.getElementById("row-clock").innerHTML = `<div class="card small-unit" style="width:30px;height:45px;font-size:24px" id="h0"></div><div class="card small-unit" style="width:30px;height:45px;font-size:24px" id="h1"></div><div style="line-height:45px;color:#666">:</div><div class="card small-unit" style="width:30px;height:45px;font-size:24px" id="tm0"></div><div class="card small-unit" style="width:30px;height:45px;font-size:24px" id="tm1"></div><div style="line-height:45px;color:#666">:</div><div class="card small-unit" style="width:30px;height:45px;font-size:24px" id="ts0"></div><div class="card small-unit" style="width:30px;height:45px;font-size:24px" id="ts1"></div>`;
            
            rotateLogic();
            setInterval(rotateLogic, STAY_SEC_PLACEHOLDER * 1000);
            setInterval(() => {
                const n = new Date();
                const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
                const dStr = months[n.getMonth()] + " " + String(n.getDate()).padStart(2,"0") + " " + ["SUN","MON","TUE","WED","THU","FRI","SAT"][n.getDay()];
                dStr.split("").forEach((c, i) => smartUpdate("d" + i, c));
                const time = String(n.getHours()).padStart(2,"0") + String(n.getMinutes()).padStart(2,"0") + String(n.getSeconds()).padStart(2,"0");
                ["h0","h1","tm0","tm1","ts0","ts1"].forEach((id, i) => smartUpdate(id, time[i]));
            }, 1000);
        };
    </script>
    </body>
    </html>
    """
    final_html = html_template.replace("BG_URL_PLACEHOLDER", bg_img) \
                               .replace("JSON_DATA_PLACEHOLDER", json_text_list) \
                               .replace("STAY_SEC_PLACEHOLDER", str(stay_sec))
    
    b64_html = base64.b64encode(final_html.encode("utf-8")).decode("utf-8")
    # 使用固定 key 避免每次 render 都重新載入整個 iframe
    components.iframe(f"data:text/html;base64,{b64_html}", height=800, scrolling=False)
