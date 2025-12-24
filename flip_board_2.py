import streamlit.components.v1 as components
import json

def render_flip_board(json_text_list, stay_sec=7.0):
    if isinstance(json_text_list, list):
        json_text_list = json.dumps(json_text_list)

    html_code = f"""
    <div class="main-container">
        <div id="row-msg" class="row-container"></div>
        <div id="row-date" class="row-container" style="margin-top: 25px;"></div>
        <div id="row-clock" class="row-container"></div>
    </div>

    <style>
        * {{ box-sizing: border-box; }}
        body {{ 
            background: transparent; margin: 0; display: flex; justify-content: center; 
            font-family: "Impact", "Microsoft JhengHei", sans-serif; overflow: hidden; 
        }}
        .main-container {{
            width: 100%; max-width: 950px; display: flex; flex-direction: column; 
            align-items: center; padding: 20px;
        }}
        .row-container {{ display: flex; gap: 8px; perspective: 1000px; justify-content: center; width: 100%; }}
        
        .card {{ 
            background: #1a1a1a; border-radius: 6px; position: relative; 
            overflow: hidden; color: white; display: flex; align-items: center; justify-content: center; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.7);
        }}
        .msg-unit {{ width: 65px; height: 95px; font-size: 55px; font-weight: bold; }}
        .small-unit {{ width: 32px; height: 48px; font-size: 26px; }}
        .separator {{ font-size: 30px; color: #555; line-height: 48px; padding: 0 4px; font-weight: bold; }}

        /* 擬真翻頁動畫 */
        .panel {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; }}
        .top-p {{ top: 0; border-bottom: 1px solid rgba(0,0,0,0.6); align-items: flex-end; border-radius: 6px 6px 0 0; }}
        .bottom-p {{ bottom: 0; align-items: flex-start; border-radius: 0 0 6px 6px; }}
        .text-node {{ position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 0; }}
        .top-p .text-node {{ bottom: -100%; }} .bottom-p .text-node {{ top: -100%; }}
        
        .leaf-node {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform 0.12s linear; transform-style: preserve-3d; }}
        .leaf-side {{ position: absolute; inset: 0; backface-visibility: hidden; background: #1a1a1a; display: flex; justify-content: center; overflow: hidden; }}
        .side-back {{ transform: rotateX(-180deg); }}
        .flipping .leaf-node {{ transform: rotateX(-180deg); }}
    </style>

    <script>
        const newsArray = {json_text_list};
        const NUM_POOL = "0123456789 ".split("");
        const EN_POOL = " ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
        let CN_POOL = []; // 動態中文字池
        
        let curNewsIdx = 0;
        let memory = {{}};
        let isBusy = {{}};

        // 洗牌函式：讓中文過場看起來是隨機跳動
        function shuffle(array) {{
            return array.sort(() => Math.random() - 0.5);
        }}

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
            
            void el.offsetWidth;
            el.classList.add('flipping');
        }}

        async function smartUpdate(id, target) {{
            const tStr = String(target).toUpperCase();
            if (memory[id] === tStr || isBusy[id]) return;
            isBusy[id] = true;

            let curVal = memory[id] || " ";
            let pool = [];

            // 判斷該使用哪個字元池
            if (/[0-9]/.test(tStr)) pool = NUM_POOL;
            else if (/[A-Z]/.test(tStr)) pool = EN_POOL;
            else if (/[\\u4E00-\\u9FFF]/.test(tStr)) pool = CN_POOL;
            else pool = [curVal, tStr]; // 其他符號直接翻

            if (pool.length > 0) {{
                let curIdx = pool.indexOf(curVal);
                if (curIdx === -1) curIdx = 0;

                // 尋字翻動動畫
                while (curVal !== tStr) {{
                    let prev = curVal;
                    curIdx = (curIdx + 1) % pool.length;
                    curVal = pool[curIdx];
                    performFlip(id, curVal, prev);
                    await new Promise(r => setTimeout(r, 80)); 
                }}
            }}

            memory[id] = tStr;
            isBusy[id] = false;
        }}

        function updateNews() {{
            const rawText = newsArray[curNewsIdx];
            
            // 挑出目前訊息中的所有中文字，建立隨機候選池
            const chars = rawText.split("");
            const chineseChars = chars.filter(c => /[\\u4E00-\\u9FFF]/.test(c));
            CN_POOL = shuffle([...new Set([" ", ...chineseChars])]);

            const text = rawText.padEnd(12, " ").substring(0, 12);
            text.split("").forEach((char, i) => {{
                // 階梯式啟動，增加機械層次感
                setTimeout(() => smartUpdate("m" + i, char), i * 150);
            }});
            curNewsIdx = (curNewsIdx + 1) % newsArray.length;
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
            const rowMsg = document.getElementById("row-msg");
            for(let i=0; i<12; i++) rowMsg.innerHTML += `<div class="card msg-unit" id="m${{i}}"></div>`;
            const rowDate = document.getElementById("row-date");
            for(let i=0; i<11; i++) rowDate.innerHTML += `<div class="card small-unit" id="d${{i}}"></div>`;
            document.getElementById("row-clock").innerHTML = `
                <div class="card small-unit" id="h0"></div><div class="card small-unit" id="h1"></div>
                <div class="separator">:</div>
                <div class="card small-unit" id="tm0"></div><div class="card small-unit" id="tm1"></div>
                <div class="separator">:</div>
                <div class="card small-unit" id="ts0"></div><div class="card small-unit" id="ts1"></div>`;

            updateNews();
            setInterval(updateNews, {stay_sec} * 1000);
            setInterval(updateClock, 1000);
        }};
    </script>
    """
    components.html(html_code, height=650)
