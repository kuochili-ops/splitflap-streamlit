import streamlit.components.v1 as components
import json
import time

def render_flip_board(json_text_list, stay_sec=7.0):
    if isinstance(json_text_list, list):
        json_text_list = json.dumps(json_text_list)
    
    # 建立一個隨機 ID 避免 Streamlit 快取舊的 JS 狀態
    uid = int(time.time())

    html_code = f"""
    <div class="viewport-wrapper" id="wrapper-{uid}">
        <div class="main-container">
            <div id="row-msg-{uid}" class="row-container"></div>
            <div id="row-date-{uid}" class="row-container" style="margin-top: 20px;"></div>
            <div id="row-clock-{uid}" class="row-container"></div>
        </div>
    </div>

    <style>
        * {{ box-sizing: border-box; }}
        body {{ background: transparent; margin: 0; display: flex; justify-content: center; font-family: "Impact", "Microsoft JhengHei", sans-serif; overflow: hidden; }}
        .viewport-wrapper {{ width: 100vw; display: flex; justify-content: center; padding: 10px; }}
        .main-container {{ width: 100%; max-width: 600px; display: flex; flex-direction: column; align-items: center; }}
        .row-container {{ display: flex; gap: 3px; perspective: 1000px; justify-content: center; width: 100%; min-height: 50px; }}
        
        .card {{ 
            background: #1a1a1a; border-radius: 4px; position: relative; overflow: hidden; color: white; 
            display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 5px rgba(0,0,0,0.5);
            width: var(--msg-w); height: calc(var(--msg-w) * 1.4); 
            font-size: var(--font-sz); font-weight: bold;
        }}
        
        .small-unit {{ width: 28px; height: 42px; font-size: 22px; --msg-w: 28px; --font-sz: 22px; }}
        .separator {{ font-size: 20px; color: #555; line-height: 42px; padding: 0 2px; }}

        .panel {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; }}
        .top-p {{ top: 0; border-bottom: 1px solid rgba(0,0,0,0.6); align-items: flex-end; }}
        .bottom-p {{ bottom: 0; align-items: flex-start; }}
        .text-node {{ position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 0; }}
        .top-p .text-node {{ bottom: -100%; }} .bottom-p .text-node {{ top: -100%; }}
        .leaf-node {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform 0.1s linear; transform-style: preserve-3d; }}
        .leaf-side {{ position: absolute; inset: 0; backface-visibility: hidden; background: #1a1a1a; display: flex; justify-content: center; overflow: hidden; }}
        .side-back {{ transform: rotateX(-180deg); }}
        .flipping .leaf-node {{ transform: rotateX(-180deg); }}
    </style>

    <script>
        (function() {{
            const newsArray = {json_text_list};
            const APP_NAME = "白六新聞/訊息告示牌";
            const NUM_POOL = "0123456789 ".split("");
            const EN_POOL = " ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
            let CN_POOL = [];
            let memory = {{}};
            let curNewsIdx = 0, curPageIdx = 0, pagesOfCurrentNews = [];

            function performFlip(id, nVal, pVal) {{
                const el = document.getElementById(id);
                if(!el) return;
                el.classList.remove('flipping');
                const n = nVal === " " ? "&nbsp;" : nVal;
                const p = pVal === " " ? "&nbsp;" : pVal;
                el.innerHTML = `<div class="panel top-p"><div class="text-node">${{n}}</div></div>
                               <div class="panel bottom-p"><div class="text-node">${{p}}</div></div>
                               <div class="leaf-node"><div class="leaf-side top-p"><div class="text-node">${{p}}</div></div>
                               <div class="leaf-side side-back bottom-p"><div class="text-node">${{n}}</div></div></div>`;
                void el.offsetWidth; el.classList.add('flipping');
            }}

            async function smartUpdate(id, target) {{
                const tStr = String(target).toUpperCase();
                let curVal = memory[id] || " ";
                if (curVal === tStr) return;

                let pool = (/[0-9]/.test(tStr)) ? NUM_POOL : (/[A-Z]/.test(tStr)) ? EN_POOL : (/[\\u4E00-\\u9FFF]/.test(tStr)) ? CN_POOL : [curVal, tStr];

                while (curVal !== tStr) {{
                    let prev = curVal;
                    curVal = pool[(pool.indexOf(curVal) + 1) % pool.length] || tStr;
                    performFlip(id, curVal, prev);
                    await new Promise(r => setTimeout(r, 60));
                }}
                memory[id] = tStr;
            }}

            function buildBoard(targetText, count) {{
                const availableWidth = Math.min(window.innerWidth, 600) - 40;
                const cardWidth = Math.floor(availableWidth / count) - 4;
                document.documentElement.style.setProperty('--msg-w', cardWidth + 'px');
                document.documentElement.style.setProperty('--font-sz', (cardWidth * 0.7) + 'px');

                const rowMsg = document.getElementById("row-msg-{uid}");
                rowMsg.innerHTML = "";
                memory = {{}}; 
                for(let i=0; i<count; i++) {{
                    rowMsg.innerHTML += `<div class="card" id="m-{uid}-${{i}}"></div>`;
                    memory[`m-{uid}-${{i}}`] = " "; // 強制初始化為空格
                }}
                const cnChars = targetText.split("").filter(c => /[\\u4E00-\\u9FFF]/.test(c));
                CN_POOL = targetText.includes(APP_NAME) ? APP_NAME.split("") : [...new Set([" ", ...cnChars])];
            }}

            async function startApp() {{
                // 初始化日期與時鐘
                const rowDate = document.getElementById("row-date-{uid}");
                for(let i=0; i<11; i++) rowDate.innerHTML += `<div class="card small-unit" id="d-{uid}-${{i}}"></div>`;
                document.getElementById("row-clock-{uid}").innerHTML = `<div class="card small-unit" id="h-{uid}-0"></div><div class="card small-unit" id="h-{uid}-1"></div><div class="separator">:</div><div class="card small-unit" id="m-{uid}-0"></div><div class="card small-unit" id="m-{uid}-1"></div><div class="separator">:</div><div class="card small-unit" id="s-{uid}-0"></div><div class="card small-unit" id="s-{uid}-1"></div>`;

                // 1. 開機序：顯示標題
                buildBoard(APP_NAME, 11);
                await new Promise(r => setTimeout(r, 500));
                APP_NAME.split("").forEach((c, i) => setTimeout(() => smartUpdate(`m-{uid}-${{i}}`, c), i * 100));

                // 2. 4秒後進入新聞
                setTimeout(() => {{
                    curNewsIdx = 0;
                    preparePages();
                    showNextPage();
                    setInterval(showNextPage, {stay_sec} * 1000);
                }}, 4000);

                setInterval(updateClock, 1000);
            }}

            function preparePages() {{
                const rawText = newsArray[curNewsIdx];
                const len = rawText.length;
                let fCount = (len <= 16) ? Math.max(Math.ceil(len / 2), 4) : 8;
                let pageData = [];
                if (len <= 16) {{
                    pageData.push(rawText.substring(0, fCount));
                    pageData.push(rawText.substring(fCount));
                }} else {{
                    for (let i = 0; i < len; i += 8) pageData.push(rawText.substring(i, i + 8));
                }}
                buildBoard(rawText, fCount);
                pagesOfCurrentNews = pageData;
                curPageIdx = 0;
            }}

            function showNextPage() {{
                if (curPageIdx >= pagesOfCurrentNews.length) {{
                    curNewsIdx = (curNewsIdx + 1) % newsArray.length;
                    preparePages();
                }}
                const text = pagesOfCurrentNews[curPageIdx];
                text.split("").forEach((char, i) => setTimeout(() => smartUpdate(`m-{uid}-${{i}}`, char), i * 120));
                curPageIdx++;
            }}

            function updateClock() {{
                const now = new Date();
                const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
                const dStr = months[now.getMonth()] + " " + String(now.getDate()).padStart(2,"0") + " " + ["SUN","MON","TUE","WED","THU","FRI","SAT"][now.getDay()];
                dStr.split("").forEach((c, i) => smartUpdate(`d-{uid}-${{i}}`, c));
                const h = now.getHours().toString().padStart(2,'0'), m = now.getMinutes().toString().padStart(2,'0'), s = now.getSeconds().toString().padStart(2,'0');
                smartUpdate(`h-{uid}-0`, h[0]); smartUpdate(`h-{uid}-1`, h[1]);
                smartUpdate(`m-{uid}-0`, m[0]); smartUpdate(`m-{uid}-1`, m[1]);
                smartUpdate(`s-{uid}-0`, s[0]); smartUpdate(`s-{uid}-1`, s[1]);
            }}

            startApp();
        }})();
    </script>
    """
    components.html(html_code, height=550)
