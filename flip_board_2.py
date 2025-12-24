import streamlit.components.v1 as components
import base64
import json

def render_flip_board(json_text_list, stay_sec=7.0):
    bg_img = "https://upload.wikimedia.org/wikipedia/en/2/21/Girl_with_Balloon.jpg"
    
    # 這裡使用普通的 """ (非 f-string) 避開 Python 對大括號的解析
    # 改用 .replace() 手動替換變數，這是最安全、不會報 SyntaxError 的做法
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * { box-sizing: border-box; }
            html, body { height: 100vh; margin: 0; padding: 0; overflow: hidden; background-color: #dcdcdc; }
            body { display: flex; justify-content: center; align-items: flex-start; font-family: "Impact", sans-serif; }
            
            .graffiti-wall { 
                position: fixed; bottom: 0; left: 0; width: 100%; height: 50vh; 
                background-image: url("BG_URL_PLACEHOLDER"); background-repeat: no-repeat; 
                background-position: center bottom; background-size: contain; z-index: 1; 
            }
            
            .acrylic-board { 
                position: relative; width: 95vw; max-width: 900px; margin-top: 5vh; padding: 45px 25px; 
                background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px); 
                border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 20px; 
                display: flex; flex-direction: column; align-items: center; gap: 20px; 
                box-shadow: 0 30px 60px rgba(0,0,0,0.2); z-index: 10; 
            }

            .row-container { display: flex; gap: 15px; perspective: 1000px; justify-content: center; width: 100%; flex-wrap: nowrap; }
            .card { background: #1a1a1a; border-radius: 8px; position: relative; overflow: hidden; color: white; display: flex; align-items: center; justify-content: center; }
            .msg-unit { width: var(--msg-w); height: calc(var(--msg-w) * 1.4); font-size: calc(var(--msg-w) * 0.9); transition: width 0.3s ease; }
            .small-unit { width: 34px; height: 50px; font-size: 30px; }
            .separator { font-size: 30px; color: #444; font-weight: bold; line-height: 50px; padding: 0 3px; }
            
            .panel { position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; }
            .top-p { top: 0; border-bottom: 1px solid rgba(0,0,0,0.6); align-items: flex-end; }
            .bottom-p { bottom: 0; align-items: flex-start; }
            .text-node { position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 1; }
            .top-p .text-node { bottom: -100%; } .bottom-p .text-node { top: -100%; }
            
            .leaf-node { position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 20; transform-origin: bottom; transition: transform 0.08s linear; transform-style: preserve-3d; }
            .leaf-side { position: absolute; inset: 0; backface-visibility: hidden; background: #1a1a1a; display: flex; justify-content: center; overflow: hidden; }
            .side-back { transform: rotateX(-180deg); }
            .flipping .leaf-node { transform: rotateX(-180deg); }
            
            .screw { position: absolute; width: 16px; height: 16px; background: radial-gradient(circle at 30% 30%, #eee, #444); border-radius: 50%; border: 1px solid #333; }
            .s-tl { top: 15px; left: 15px; } .s-tr { top: 15px; right: 15px; } .s-bl { bottom: 15px; left: 15px; } .s-br { bottom: 15px; right: 15px; }
        </style>
    </head>
    <body>
        <div class="graffiti-wall"></div>
        <div class="acrylic-board">
            <div class="screw s-tl"></div><div class="screw s-tr"></div>
            <div id="row-msg" class="row-container"></div>
            <div id="row-date" class="row-container" style="margin-top: 10px;"></div>
            <div id="row-clock" class="row-container"></div>
            <div class="screw s-bl"></div><div class="screw s-br"></div>
        </div>

    <script>
        const newsArray = JSON.parse('JSON_DATA_PLACEHOLDER');
        let currentNewsIdx = 0;
        let currentPageIdx = -1;
        let currentPages = [];
        let currentFlapCount = 0; 
        let CN_POOL = [];
        const AZ_POOL = " ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
        const NUM_POOL = "0123456789".split("");
        
        let memory = {}; 
        let isBusy = {};

        function getMsgPages(text) {
            const len = text.length;
            if (len <= 16) {
                const flapCount = Math.ceil(len / 2);
                let p1 = text.substring(0, flapCount).split("");
                let p2 = text.substring(flapCount).split("");
                return [p1, p2];
            }
            let p = [];
            for (let i = 0; i < len; i += 8) {
                p.push(text.substring(i, i + 8).split(""));
            }
            return p;
        }

        function updateLayout(flapCount) {
            const board = document.querySelector(".acrylic-board");
            const availableWidth = board.offsetWidth - 120;
            const calculatedW = Math.min(180, Math.floor(availableWidth / flapCount) - 10);
            document.documentElement.style.setProperty("--msg-w", calculatedW + "px");
            
            const msgRow = document.getElementById("row-msg");
            msgRow.innerHTML = "";
            for(let i=0; i<flapCount; i++) {
                const div = document.createElement("div");
                div.className = "card msg-unit";
                div.id = "m" + i;
                msgRow.appendChild(div);
            }
            memory = {}; 
        }

        function performFlip(id, nVal, pVal) {
            const el = document.getElementById(id);
            if(!el) return;
            const n = nVal || "&nbsp;";
            const p = pVal || "&nbsp;";
            el.classList.remove("flipping");
            el.innerHTML = `<div class="panel top-p"><div class="text-node">${n}</div></div>` +
                           `<div class="panel bottom-p"><div class="text-node">${p}</div></div>` +
                           `<div class="leaf-node"><div class="leaf-side top-p"><div class="text-node">${p}</div></div>` +
                           `<div class="leaf-side side-back bottom-p"><div class="text-node">${n}</div></div></div>`;
            void el.offsetWidth; el.classList.add("flipping");
        }

        async function smartUpdate(id, target) {
            let tStr = String(target);
            if (memory[id] === tStr || isBusy[id]) return;
            isBusy[id] = true;
            let curStr = memory[id] || " ";
            let pool = AZ_POOL;
            if (/[0-9]/.test(tStr)) pool = NUM_POOL;
            else if (/[\\u4E00-\\u9FFF]/.test(tStr)) pool = CN_POOL;

            let curIdx = pool.indexOf(curStr);
            if (curIdx === -1) curIdx = 0;
            let tarIdx = pool.indexOf(tStr);

            if (tarIdx === -1) {
                performFlip(id, tStr, curStr);
            } else {
                while (curStr !== tStr) {
                    let prev = curStr;
                    curIdx = (curIdx + 1) % pool.length;
                    curStr = pool[curIdx];
                    performFlip(id, curStr, prev);
                    await new Promise(r => setTimeout(r, 90));
                }
            }
            memory[id] = tStr; isBusy[id] = false;
        }

        const rotateLogic = () => {
            if (currentPageIdx < currentPages.length - 1) {
                currentPageIdx++;
            } else {
                currentNewsIdx = (currentNewsIdx + 1) % newsArray.length;
                currentPageIdx = 0;
                const fullText = newsArray[currentNewsIdx];
                currentPages = getMsgPages(fullText);
                const newFlapCount = Math.max(...currentPages.map(p => p.length));
                if (newFlapCount !== currentFlapCount) {
                    currentFlapCount = newFlapCount;
                    updateLayout(currentFlapCount);
                }
                CN_POOL = [...new Set(fullText.replace(/[A-Z0-9\\s]/g, "").split(""))];
            }
            const page = currentPages[currentPageIdx];
            for(let i=0; i < currentFlapCount; i++) {
                const char = page[i] || " ";
                setTimeout(() => smartUpdate("m" + i, char), i * 150);
            }
        };

        window.onload = () => {
            const dateRow = document.getElementById("row-date");
            dateRow.innerHTML = "";
            for(let i=0; i<11; i++) {
                const div = document.createElement("div");
                div.className = "card small-unit";
                div.id = "d" + i;
                dateRow.appendChild(div);
            }
            document.getElementById("row-clock").innerHTML = `<div class="card small-unit" id="h0"></div><div class="card small-unit" id="h1"></div><div class="separator">:</div><div class="card small-unit" id="tm0"></div><div class="card small-unit" id="tm1"></div><div class="separator">:</div><div class="card small-unit" id="ts0"></div><div class="card small-unit" id="ts1"></div>`;
            rotateLogic(); 
            setInterval(() => {
                const n = new Date();
                const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
                const days = ["SUN","MON","TUE","WED","THU","FRI","SAT"];
                const dStr = months[n.getMonth()] + " " + String(n.getDate()).padStart(2,"0") + " " + days[n.getDay()];
                dStr.split("").forEach((c, i) => smartUpdate("d" + i, c));
                const time = String(n.getHours()).padStart(2,"0") + String(n.getMinutes()).padStart(2,"0") + String(n.getSeconds()).padStart(2,"0");
                ["h0","h1","tm0","tm1","ts0","ts1"].forEach((id, i) => smartUpdate(id, time[i]));
            }, 1000);
            setInterval(rotateLogic, STAY_SEC_PLACEHOLDER * 1000);
        };
    </script>
    </body>
    </html>
    """
    # 使用 .replace() 進行手動替換，避開 f-string 的語法衝突
    final_html = html_template.replace("BG_URL_PLACEHOLDER", bg_img) \
                               .replace("JSON_DATA_PLACEHOLDER", json_text_list) \
                               .replace("STAY_SEC_PLACEHOLDER", str(stay_sec))
    
    b64_html = base64.b64encode(final_html.encode("utf-8")).decode("utf-8")
    components.iframe(f"data:text/html;base64,{b64_html}", height=1000, scrolling=False)
