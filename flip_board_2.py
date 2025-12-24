import streamlit.components.v1 as components
import json

def render_flip_board(json_text_list, stay_sec=7.0):
    if isinstance(json_text_list, list):
        json_text_list = json.dumps(json_text_list)

    html_code = f"""
    <div class="viewport-wrapper">
        <div class="main-container">
            <div id="row-msg" class="row-container"></div>
            <div id="row-date" class="row-container" style="margin-top: 15px;"></div>
            <div id="row-clock" class="row-container"></div>
        </div>
    </div>

    <style>
        * {{ box-sizing: border-box; }}
        body {{ 
            background: transparent; margin: 0; display: flex; justify-content: center; 
            font-family: "Impact", "Microsoft JhengHei", sans-serif; overflow-x: hidden; 
        }}
        .viewport-wrapper {{ width: 100vw; display: flex; justify-content: center; padding: 10px; }}
        .main-container {{ 
            width: 100%; max-width: 600px; display: flex; flex-direction: column; 
            align-items: center; 
        }}
        .row-container {{ 
            display: flex; gap: 4px; perspective: 1000px; 
            justify-content: center; width: 100%; flex-wrap: nowrap;
        }}
        
        .card {{ 
            background: #1a1a1a; border-radius: 4px; position: relative; 
            overflow: hidden; color: white; display: flex; align-items: center; justify-content: center; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.5);
            width: var(--msg-w); 
            height: calc(var(--msg-w) * 1.4); 
            font-size: calc(var(--msg-w) * 0.9);
        }}
        
        .small-unit {{ width: 28px; height: 40px; font-size: 22px; }}
        .separator {{ font-size: 20px; color: #555; line-height: 40px; padding: 0 2px; }}

        .panel {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; }}
        .top-p {{ top: 0; border-bottom: 1px solid rgba(0,0,0,0.6); align-items: flex-end; }}
        .bottom-p {{ bottom: 0; align-items: flex-start; }}
        .text-node {{ position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 0; }}
        .top-p .text-node {{ bottom: -100%; }} .bottom-p .text-node {{ top: -100%; }}
        .leaf-node {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform 0.12s linear; transform-style: preserve-3d; }}
        .leaf-side {{ position: absolute; inset: 0; backface-visibility: hidden; background: #1a1a1a; display: flex; justify-content: center; overflow: hidden; }}
        .side-back {{ transform: rotateX(-180deg); }}
        .flipping .leaf-node {{ transform: rotateX(-180deg); }}
    </style>

    <script>
        const newsArray = {json_text_list};
        const APP_NAME = "白六新聞/訊息告示牌";
        const NUM_POOL = "0123456789 ".split("");
        const EN_POOL = " ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
        let CN_POOL = [];
        
        let curNewsIdx = 0;
        let curPageIdx = 0;
        let pagesOfCurrentNews = [];
        let memory = {{}};
        let isBusy = {{}};

        function shuffle(array) {{ return array.sort(() => Math.random() - 0.5); }}

        function performFlip(id, nVal, pVal) {{
            const el = document.getElementById(id);
            if(!el) return;
            el.classList.remove('flipping');
            const n = nVal === " " ? "&nbsp;" : nVal;
            const p = pVal === " " ? "&nbsp;" : pVal;
            el.innerHTML = `
                <div class="panel top-p"><div class="text-node">${{n}}</div></div>
                <div class="panel bottom-p"><div class="text-node">${{p}}</div></div>
                <div class="leaf-node">
                    <div class="leaf-side top-p"><div class="text-node">${{p}}</div></div>
                    <div class="leaf-side side-back bottom-p"><div class="text-node">${{n}}</div></div>
                </div>`;
            void el.offsetWidth; el.classList.add('flipping');
        }}

        async function smartUpdate(id, target) {{
            const tStr = String(target).toUpperCase();
            if (memory[id] === tStr || isBusy[id]) return;
            isBusy[id] = true;
            let curVal = memory[id] || " ";
            let pool = (/[0-9]/.test(tStr)) ? NUM_POOL : (/[A-Z]/.test(tStr)) ? EN_POOL : (/[\\u4E00-\\u9FFF]/.test(tStr)) ? CN_POOL : [curVal, tStr];

            while (curVal !== tStr) {{
                let prev = curVal;
                let curIdx = pool.indexOf(curVal);
                curVal = pool[(curIdx + 1) % pool.length] || tStr;
                performFlip(id, curVal, prev);
                await new Promise(r => setTimeout(r, 70)); 
            }}
            memory[id] = tStr; isBusy[id] = false;
        }}

        // 修改布局邏輯以適應開場文字或新聞
        function buildBoard(targetText, customFlapCount = null) {{
            const len = targetText.length;
            let flapCount = customFlapCount;
            
            if (!flapCount) {{
                if (len <= 16) {{
                    flapCount = Math.floor(len / 2) + (len % 2 !== 0 ? 1 : 0);
                }} else {{
                    flapCount = 8;
                }}
            }}

            const cnChars = targetText.split("").filter(c => /[\\u4E00-\\u9FFF]/.test(c));
            CN_POOL = shuffle([...new Set([" ", ...cnChars])]);

            const availableWidth = Math.min(window.innerWidth, 600) - 40;
            const cardWidth = Math.floor(availableWidth / flapCount) - 4;
            document.documentElement.style.setProperty('--msg-w', cardWidth + 'px');

            const rowMsg = document.getElementById("row-msg");
            rowMsg.innerHTML = "";
            memory = {{}}; 
            for(let i=0; i<flapCount; i++) {{
                rowMsg.innerHTML += `<div class="card" id="m${{i}}"></div>`;
            }}
            return flapCount;
        }}

        async function bootSequence() {{
            // 1. 顯示 APP 名稱 (固定 11 板適配名稱長度)
            const fCount = buildBoard(APP_NAME, 11);
            APP_NAME.split("").forEach((char, i) => {{
                setTimeout(() => smartUpdate("m" + i, char), i * 120);
            }});

            // 2. 停留 4 秒後開始新聞輪播
            setTimeout(() => {{
                preparePages();
                showNextPage();
                setInterval(showNextPage, {stay_sec} * 1000);
            }}, 4000);
        }}

        function preparePages() {{
            const rawText = newsArray[curNewsIdx];
            const len = rawText.length;
            let pageData = [];
            let flapCount = (len <= 16) ? Math.floor(len / 2) + (len % 2 !== 0 ? 1 : 0) : 8;

            if (len <= 16) {{
                pageData.push(rawText.substring(0, flapCount));
                pageData.push(rawText.substring(flapCount));
            }} else {{
                for (let i = 0; i < len; i += 8) {{
                    pageData.push(rawText.substring(i, i + 8));
                }}
            }}
            
            buildBoard(rawText, flapCount);
            pagesOfCurrentNews = pageData;
            curPageIdx = 0;
        }}

        function showNextPage() {{
            if (curPageIdx >= pagesOfCurrentNews.length) {{
                curNewsIdx = (curNewsIdx + 1) % newsArray.length;
                preparePages();
            }}
            const text = pagesOfCurrentNews[curPageIdx].padEnd(8, " ");
            text.split("").forEach((char, i) => {{
                setTimeout(() => smartUpdate("m" + i, char), i * 120);
            }});
            curPageIdx++;
        }}

        function updateClock() {{
            const now = new Date();
            const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
            const dStr = months[now.getMonth()] + " " + String(now.getDate()).padStart(2,"0") + " " + ["SUN","MON","TUE","WED","THU","FRI","SAT"][now.getDay()];
            dStr.split("").forEach((c, i) => smartUpdate("d" + i, c));
            const timeStr = now.getHours().toString().padStart(2,'0') + now.getMinutes().toString().padStart(2,'0') + now.getSeconds().toString().padStart(2,'0');
            ["h0","h1","tm0","tm1","ts0","ts1"].forEach((id, i) => smartUpdate(id, timeStr[i]));
        }}

        window.onload = () => {{
            const rowDate = document.getElementById("row-date");
            for(let i=0; i<11; i++) rowDate.innerHTML += `<div class="card small-unit" id="d${{i}}"></div>`;
            document.getElementById("row-clock").innerHTML = `
                <div class="card small-unit" id="h0"></div><div class="card small-unit" id="h1"></div>
                <div class="separator">:</div>
                <div class="card small-unit" id="tm0"></div><div class="card small-unit" id="tm1"></div>
                <div class="separator">:</div>
                <div class="card small-unit" id="ts0"></div><div class="card small-unit" id="ts1"></div>`;

            bootSequence(); // 啟動開場序
            setInterval(updateClock, 1000);
        }};
    </script>
    """
    components.html(html_code, height=500)
