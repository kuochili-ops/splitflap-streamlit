import streamlit.components.v1 as components
import time

def render_flip_board(json_text_list, stay_sec=7.0):
    uid = int(time.time())
    html_code = f"""
    <div id="board-container-{uid}" style="width: 100%; display: flex; flex-direction: column; align-items: center; gap: 20px; padding-top: 20px;">
        <div id="row-msg-{uid}" class="row-container"></div>
        <div id="row-date-{uid}" class="row-container"></div>
        <div id="row-clock-{uid}" class="row-container"></div>
    </div>

    <style>
        * {{ box-sizing: border-box; }}
        body {{ background: transparent; margin: 0; font-family: "Impact", sans-serif; overflow: hidden; }}
        .row-container {{ display: flex; gap: 4px; perspective: 1000px; justify-content: center; width: 100%; min-height: 60px; }}
        .card {{ 
            background: #1a1a1a; border-radius: 4px; position: relative; color: white; 
            display: flex; align-items: center; justify-content: center;
            width: var(--card-w, 40px); height: calc(var(--card-w, 40px) * 1.4); 
            font-size: var(--font-sz, 30px); font-weight: bold; overflow: hidden;
        }}
        .small-card {{ width: 30px; height: 45px; font-size: 24px; }}
        .separator {{ font-size: 24px; color: #666; line-height: 45px; padding: 0 2px; }}
        
        /* 翻牌動畫核心 */
        .panel {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; }}
        .top-p {{ top: 0; border-bottom: 1px solid rgba(0,0,0,0.5); align-items: flex-end; }}
        .bottom-p {{ bottom: 0; align-items: flex-start; }}
        .text-node {{ position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 0; }}
        .top-p .text-node {{ bottom: -100%; }} .bottom-p .text-node {{ top: -100%; }}
        
        .leaf {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform 0.15s linear; transform-style: preserve-3d; }}
        .side {{ position: absolute; inset: 0; backface-visibility: hidden; background: #1a1a1a; display: flex; justify-content: center; overflow: hidden; }}
        .back {{ transform: rotateX(-180deg); }}
        .flip .leaf {{ transform: rotateX(-180deg); }}
    </style>

    <script>
    (function() {{
        const news = {json_text_list};
        let memory = {{}}, curIdx = 0;
        
        function flip(id, nVal, pVal) {{
            const el = document.getElementById(id); if(!el) return;
            el.classList.remove('flip');
            const n = nVal === " " ? "&nbsp;" : nVal, p = pVal === " " ? "&nbsp;" : pVal;
            el.innerHTML = `
                <div class="panel top-p"><div class="text-node">${{n}}</div></div>
                <div class="panel bottom-p"><div class="text-node">${{p}}</div></div>
                <div class="leaf">
                    <div class="side top-p"><div class="text-node">${{p}}</div></div>
                    <div class="side back bottom-p"><div class="text-node">${{n}}</div></div>
                </div>`;
            void el.offsetWidth; el.classList.add('flip');
        }}

        async function update(id, target) {{
            let cur = memory[id] || " ";
            const tar = String(target).toUpperCase();
            if (cur === tar) return;
            const pool = /[0-9]/.test(tar) ? " 0123456789".split("") : " ABCDEFGHIJKLMNOPQRSTUVWXYZ!?.+-%/".split("");
            
            // 逐步翻轉邏輯
            let idx = pool.indexOf(cur);
            if (idx === -1) idx = 0;
            while (cur !== tar) {{
                let prev = cur;
                idx = (idx + 1) % pool.length;
                cur = pool[idx];
                flip(id, cur, prev);
                await new Promise(r => setTimeout(r, 50));
            }}
            memory[id] = tar;
        }}

        function init() {{
            const rowMsg = document.getElementById("row-msg-{uid}");
            const rowDate = document.getElementById("row-date-{uid}");
            const rowClock = document.getElementById("row-clock-{uid}");
            
            // 初始化訊息欄 (12格)
            for(let i=0; i<12; i++) rowMsg.innerHTML += `<div class="card" id="m-{uid}-${{i}}"></div>`;
            // 初始化日期 (11格)
            for(let i=0; i<11; i++) rowDate.innerHTML += `<div class="card small-card" id="d-{uid}-${{i}}"></div>`;
            // 初始化時間 (ID 加上時鐘前綴，解決分鐘衝突)
            rowClock.innerHTML = `
                <div class="card small-card" id="c-h-{uid}-0"></div><div class="card small-card" id="c-h-{uid}-1"></div>
                <div class="separator">:</div>
                <div class="card small-card" id="c-m-{uid}-0"></div><div class="card small-card" id="c-m-{uid}-1"></div>
                <div class="separator">:</div>
                <div class="card small-card" id="c-s-{uid}-0"></div><div class="card small-card" id="c-s-{uid}-1"></div>`;
            
            showNext();
            setInterval(showNext, {stay_sec} * 1000);
            setInterval(tick, 1000);
        }}

        function showNext() {{
            const txt = news[curIdx].padEnd(12, " ").substring(0, 12);
            txt.split("").forEach((char, i) => setTimeout(() => update(`m-{uid}-${{i}}`, char), i * 80));
            curIdx = (curIdx + 1) % news.length;
        }}

        function tick() {{
            const now = new Date();
            const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
            const dStr = (months[now.getMonth()] + " " + String(now.getDate()).padStart(2,"0") + " " + ["SUN","MON","TUE","WED","THU","FRI","SAT"][now.getDay()]).toUpperCase();
            dStr.split("").forEach((c, i) => update(`d-{uid}-${{i}}`, c));
            
            const h = String(now.getHours()).padStart(2,"0"), m = String(now.getMinutes()).padStart(2,"0"), s = String(now.getSeconds()).padStart(2,"0");
            update(`c-h-{uid}-0`, h[0]); update(`c-h-{uid}-1`, h[1]);
            update(`c-m-{uid}-0`, m[0]); update(`c-m-{uid}-1`, m[1]);
            update(`c-s-{uid}-0`, s[0]); update(`c-s-{uid}-1`, s[1]);
        }}

        window.onload = init;
    }})();
    </script>
    """
    components.html(html_code, height=450)
