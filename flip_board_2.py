import streamlit.components.v1 as components
import json

def render_flip_board(json_text_list, stay_sec=7.0):
    if isinstance(json_text_list, list):
        json_text_list = json.dumps(json_text_list)

    html_code = f"""
    <div class="main-container">
        <div id="row-msg" class="row-container"></div>
        <div id="row-date" class="row-container" style="margin-top: 20px;"></div>
        <div id="row-clock" class="row-container"></div>
    </div>

    <style>
        * {{ box-sizing: border-box; }}
        body {{ 
            background: transparent; margin: 0; display: flex; justify-content: center; 
            font-family: "Impact", "Microsoft JhengHei", sans-serif; overflow: hidden; 
        }}
        .main-container {{
            width: 100%; max-width: 900px; display: flex; flex-direction: column; 
            align-items: center; padding: 20px;
        }}
        .row-container {{ display: flex; gap: 8px; perspective: 1000px; justify-content: center; width: 100%; }}
        
        .card {{ 
            background: #1a1a1a; border-radius: 6px; position: relative; 
            overflow: hidden; color: white; display: flex; align-items: center; justify-content: center; 
            box-shadow: 0 4px 8px rgba(0,0,0,0.5);
        }}
        .msg-unit {{ width: 60px; height: 90px; font-size: 55px; }}
        .small-unit {{ width: 30px; height: 45px; font-size: 24px; }}
        .separator {{ font-size: 30px; color: #666; line-height: 45px; padding: 0 4px; }}

        /* 翻牌過場動畫核心 */
        .panel {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; }}
        .top-p {{ top: 0; border-bottom: 1px solid rgba(0,0,0,0.6); align-items: flex-end; border-radius: 6px 6px 0 0; }}
        .bottom-p {{ bottom: 0; align-items: flex-start; border-radius: 0 0 6px 6px; }}
        .text-node {{ position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 0; }}
        .top-p .text-node {{ bottom: -100%; }} .bottom-p .text-node {{ top: -100%; }}
        
        .leaf-node {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform 0.15s ease-in; transform-style: preserve-3d; }}
        .leaf-side {{ position: absolute; inset: 0; backface-visibility: hidden; background: #1a1a1a; display: flex; justify-content: center; overflow: hidden; }}
        .side-back {{ transform: rotateX(-180deg); }}
        .flipping .leaf-node {{ transform: rotateX(-180deg); }}
    </style>

    <script>
        const newsArray = {json_text_list};
        const AZ_POOL = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789".split("");
        let curNewsIdx = 0;
        let memory = {{}};
        let isBusy = {{}};

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
            
            requestAnimationFrame(() => {{
                void el.offsetWidth;
                requestAnimationFrame(() => el.classList.add('flipping'));
            }});
        }}

        async function smartUpdate(id, target) {{
            const tStr = String(target).toUpperCase();
            if (memory[id] === tStr || isBusy[id]) return;
            isBusy[id] = true;

            let curVal = memory[id] || " ";
            
            // 尋字動畫邏輯
            if (AZ_POOL.includes(tStr) && AZ_POOL.includes(curVal)) {{
                let curIdx = AZ_POOL.indexOf(curVal);
                let tarIdx = AZ_POOL.indexOf(tStr);
                
                // 如果目標在後面，就一格格翻過去
                while (curVal !== tStr) {{
                    let prev = curVal;
                    curIdx = (curIdx + 1) % AZ_POOL.length;
                    curVal = AZ_POOL[curIdx];
                    performFlip(id, curVal, prev);
                    // 翻轉速度，越小越快
                    await new Promise(r => setTimeout(r, 100)); 
                }}
            }} else {{
                // 中文或其他字元直接翻轉
                performFlip(id, tStr, curVal);
            }}

            memory[id] = tStr;
            isBusy[id] = false;
        }}

        function updateNews() {{
            const text = newsArray[curNewsIdx].padEnd(12, " ").substring(0, 12);
            text.split("").forEach((char, i) => {{
                // 稍微錯開每格開始翻轉的時間，更有機械感
                setTimeout(() => smartUpdate("m" + i, char), i * 100);
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
    components.html(html_code, height=600)
