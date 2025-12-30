import streamlit.components.v1 as components
import time

def render_flip_board(json_text_list, stay_sec=7.0):
    uid = int(time.time())
    html_code = f"""
    <div id="board-container-{uid}" style="width: 100%; display: flex; flex-direction: column; align-items: center; gap: 20px;">
        <div id="row-msg-{uid}" class="row-container"></div>
        <div id="row-date-{uid}" class="row-container" style="margin-top: 20px;"></div>
        <div id="row-clock-{uid}" class="row-container"></div>
    </div>

    <style>
        * {{ box-sizing: border-box; }}
        body {{ background: transparent; margin: 0; font-family: "Impact", "Microsoft JhengHei", sans-serif; overflow: hidden; }}
        .row-container {{ display: flex; gap: 4px; perspective: 1000px; justify-content: center; width: 100%; min-height: 50px; }}
        .card {{ 
            background: #1a1a1a; border-radius: 4px; position: relative; color: white; 
            display: flex; align-items: center; justify-content: center;
            width: var(--card-w, 40px); height: calc(var(--card-w, 40px) * 1.4); 
            font-size: var(--font-sz, 30px); font-weight: bold; overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.5);
        }}
        .small-card {{ width: 28px; height: 42px; font-size: 22px; --card-w: 28px; --font-sz: 22px; }}
        .separator {{ font-size: 20px; color: #555; line-height: 42px; padding: 0 2px; }}
        
        .panel {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; }}
        .top-p {{ top: 0; border-bottom: 1px solid rgba(0,0,0,0.6); align-items: flex-end; }}
        .bottom-p {{ bottom: 0; align-items: flex-start; }}
        .text-node {{ position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 0; }}
        .top-p .text-node {{ bottom: -100%; }} .bottom-p .text-node {{ top: -100%; }}
        
        .leaf {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform 0.12s linear; transform-style: preserve-3d; }}
        .side {{ position: absolute; inset: 0; backface-visibility: hidden; background: #1a1a1a; display: flex; justify-content: center; overflow: hidden; }}
        .side-back {{ transform: rotateX(-180deg); }}
        .flipping .leaf {{ transform: rotateX(-180deg); }}
    </style>

    <script>
    (function() {{
        const news = {json_text_list};
        let memory = {{}}, curNIdx = 0, curPIdx = 0, pages = [];
        const pools = {{
            num: " 0123456789".split(""),
            en: " ABCDEFGHIJKLMNOPQRSTUVWXYZ!?.+-%".split("")
        }};

        function flip(id, n, p) {{
            const el = document.getElementById(id);
            if (!el) return;
            el.classList.remove('flipping');
            const nV = (n === " ") ? "&nbsp;" : n, pV = (p === " ") ? "&nbsp;" : p;
            el.innerHTML = `
                <div class="panel top-p"><div class="text-node">${{nV}}</div></div>
                <div class="panel bottom-p"><div class="text-node">${{pV}}</div></div>
                <div class="leaf"><div class="side top-p"><div class="text-node">${{pV}}</div></div><div class="side side-back bottom-p"><div class="text-node">${{nV}}</div></div></div>`;
            void el.offsetWidth;
            el.classList.add('flipping');
        }}

        async function update(id, tar) {{
            let cur = memory[id] || " ";
            const t = String(tar).toUpperCase();
            if (cur === t) return;
            let p = /[0-9]/.test(t) ? pools.num : pools.en;
            if (!p.includes(t)) p = [cur, t];
            let idx = p.indexOf(cur);
            while (cur !== t) {{
                let prev = cur;
                idx = (idx + 1) % p.length;
                cur = p[idx];
                flip(id, cur, prev);
                await new Promise(r => setTimeout(r, 60));
            }}
            memory[id] = t;
        }}

        function build(count) {{
            const row = document.getElementById("row-msg-{uid}");
            // 強制設定訊息欄位寬度（8板時會較寬，11板時較窄）
            const cardW = Math.floor((Math.min(window.innerWidth, 600) - 40) / count) - 4;
            row.style.setProperty('--card-w', cardW + 'px');
            row.style.setProperty('--font-sz', (cardW * 0.75) + 'px');
            row.innerHTML = "";
            for(let i=0; i<count; i++) {{
                const id = `msg-{uid}-${{i}}`;
                row.innerHTML += `<div class="card" id="${{id}}"></div>`;
                memory[id] = " ";
            }}
        }}

        function prepare() {{
            const t = news[curNIdx];
            // 標題 11 板，其餘訊息最多 8 板
            let count = (curNIdx === 0) ? 11 : 8;
            let pData = [];
            for (let i = 0; i < t.length; i += count) {{
                pData.push(t.substring(i, i + count).padEnd(count, " "));
            }}
            if (pData.length === 0) pData = [" ".repeat(count)];
            pages = pData;
            curPIdx = 0;
            build(count);
        }}

        async function tick() {{
            if (curPIdx >= pages.length) {{
                curNIdx = (curNIdx + 1) % news.length;
                prepare();
            }}
            const txt = pages[curPIdx];
            txt.split("").forEach((c, i) => setTimeout(() => update(`msg-{uid}-${{i}}`, c), i * 100));
            curPIdx++;
        }}

        window.onload = () => {{
            const rowD = document.getElementById("row-date-{uid}");
            for(let i=0; i<11; i++) rowD.innerHTML += `<div class="card small-card" id="d-{uid}-${{i}}"></div>`;
            
            document.getElementById("row-clock-{uid}").innerHTML = `
                <div class="card small-card" id="clk-h-{uid}-0"></div><div class="card small-card" id="clk-h-{uid}-1"></div>
                <div class="separator">:</div>
                <div class="card small-card" id="clk-m-{uid}-0"></div><div class="card small-card" id="clk-m-{uid}-1"></div>
                <div class="separator">:</div>
                <div class="card small-card" id="clk-s-{uid}-0"></div><div class="card small-card" id="clk-s-{uid}-1"></div>`;
            
            prepare(); tick();
            setInterval(tick, {stay_sec} * 1000);
            setInterval(() => {{
                const n = new Date();
                const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
                const dStr = (months[n.getMonth()] + " " + String(n.getDate()).padStart(2,"0") + " " + ["SUN","MON","TUE","WED","THU","FRI","SAT"][n.getDay()]).toUpperCase();
                dStr.split("").forEach((c, i) => update(`d-{uid}-${{i}}`, c));
                const h = String(n.getHours()).padStart(2,'0'), m = String(n.getMinutes()).padStart(2,'0'), s = String(n.getSeconds()).padStart(2,'0');
                update(`clk-h-{uid}-0`, h[0]); update(`clk-h-{uid}-1`, h[1]);
                update(`clk-m-{uid}-0`, m[0]); update(`clk-m-{uid}-1`, m[1]);
                update(`clk-s-{uid}-0`, s[0]); update(`clk-s-{uid}-1`, s[1]);
            }}, 1000);
        }};
    }})();
    </script>
    """
    components.html(html_code, height=520)
