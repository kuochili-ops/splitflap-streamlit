import streamlit as st
import streamlit.components.v1 as components
import base64
import os
from urllib.parse import urlencode

# --- 1. 頁面基礎設定 ---
st.set_page_config(layout="wide", page_title="Banksy Terminal V11.1")

# 設定樣式：完全隱藏側邊欄與頁首，並設計底部懸浮控制台
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: #1a1a1a !important;}
    .stApp {background-color: #1a1a1a !important;}
    [data-testid="stSidebar"] {display: none;}
    
    /* 底部懸浮控制台容器 */
    .floating-console {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        max-width: 800px;
        background: rgba(40, 40, 40, 0.9);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        z-index: 1000;
        box-shadow: 0 -10px 30px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 狀態管理 ---
if 'show_controls' not in st.session_state:
    st.session_state.show_controls = True

# --- 3. 參數處理 ---
query_params = st.query_params
init_text = query_params.get("text", "EVERYTHING IS FINE")
init_stay = float(query_params.get("stay", 4.0))
init_speed = int(query_params.get("speed", 80))

# --- 4. 底部懸浮輸入與分享區 ---
if st.session_state.show_controls:
    with st.container():
        st.markdown('<div class="floating-console">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            user_text = st.text_input("訊息內容", value=init_text, label_visibility="collapsed", placeholder="輸入想說的話...")
        with col2:
            user_stay = st.number_input("停頓(秒)", 2.0, 10.0, init_stay, 0.5, label_visibility="collapsed")
        with col3:
            if st.button("🚀 開始播放", use_container_width=True):
                st.session_state.show_controls = False
                st.rerun()

        # 分享功能區
        params = {"text": user_text, "stay": user_stay, "speed": init_speed}
        share_url = f"https://share.streamlit.io/your-app?{urlencode(params)}"
        
        scol1, scol2 = st.columns([3, 1])
        with scol1:
            st.code(share_url, wrap_lines=False)
        with scol2:
            if st.button("🔗 分享", use_container_width=True):
                st.toast("連結已生成，請長按上方代碼複製！")
        
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # 隱藏時顯示一個小小的「編輯」按鈕在角落
    if st.button("⚙️", help="點擊開啟設定"):
        st.session_state.show_controls = True
        st.rerun()

# --- 5. 核心 HTML 與 JS (維持翻牌邏輯，修正 0 顯示) ---
# 圖片處理
img_filename = "banksy-girl-with-balloon-logo-png_seeklogo-621871.png"
img_data = "https://upload.wikimedia.org/wikipedia/en/2/21/Girl_with_Balloon.jpg"
if os.path.exists(img_filename):
    with open(img_filename, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
        img_data = f"data:image/png;base64,{img_b64}"

html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    * {{ box-sizing: border-box; }}
    body {{ 
        background-color: #dcdcdc; 
        background-image: url("{img_data}");
        background-repeat: no-repeat;
        background-position: right 10% bottom 35%; 
        background-size: auto 30vh;
        display: flex; justify-content: center; align-items: flex-start; 
        height: 100vh; margin: 0; overflow: hidden;
        font-family: "Impact", "Microsoft JhengHei", sans-serif;
    }}
    .acrylic-board {{
        position: relative; width: 90vw; max-width: 820px;
        margin-top: 5vh; padding: 50px 30px;
        background: rgba(255, 255, 255, 0.08); 
        backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); 
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 25px; box-shadow: 0 15px 40px rgba(0,0,0,0.08);
        display: flex; flex-direction: column; align-items: center; gap: 20px; z-index: 10;
    }}
    .row-container {{ display: flex; gap: 6px; perspective: 1000px; justify-content: center; width: 100%; }}
    .card {{ background: #1a1a1a; border-radius: 4px; position: relative; overflow: hidden; color: white; display: flex; align-items: center; justify-content: center; }}
    .msg-unit {{ width: var(--msg-w); height: calc(var(--msg-w) * 1.35); font-size: calc(var(--msg-w) * 0.85); }}
    .small-unit {{ width: 34px; height: 50px; font-size: 30px; }}
    .separator {{ font-size: 32px; color: #444; font-weight: bold; align-self: center; line-height: 50px; padding: 0 2px; }}
    .panel {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; }}
    .top-p {{ top: 0; border-bottom: 1px solid rgba(0,0,0,0.5); align-items: flex-end; }}
    .bottom-p {{ bottom: 0; align-items: flex-start; }}
    .text-node {{ position: absolute; width: 100%; height: 200%; display: flex; align-items: center; justify-content: center; line-height: 0; }}
    .top-p .text-node {{ bottom: -100%; }} .bottom-p .text-node {{ top: -100%; }}
    .leaf-node {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform 0.3s ease-in; transform-style: preserve-3d; }}
    .leaf-side {{ position: absolute; inset: 0; backface-visibility: hidden; background: #1a1a1a; display: flex; justify-content: center; overflow: hidden; }}
    .side-back {{ transform: rotateX(-180deg); }}
    .flipping .leaf-node {{ transform: rotateX(-180deg); }}
</style>
</head>
<body>
    <div class="acrylic-board">
        <div id="row-msg" class="row-container"></div>
        <div id="row-info" style="display: flex; flex-direction: column; gap: 10px; width: 100%; align-items: center;">
            <div id="row-date" class="row-container"></div>
            <div id="row-clock" class="row-container"></div>
        </div>
    </div>
<script>
    const fullText = "{user_text.upper()}";
    const baseSpeed = {init_speed};
    const flapCount = Math.min(10, Math.floor(fullText.length / 2) || 4);
    const charPool = Array.from(new Set(fullText.replace(/\\s/g, '').split('')));
    
    let memory = {{}};
    let isBusy = {{}};

    function performFlip(id, nextVal, prevVal) {{
        const el = document.getElementById(id);
        if(!el) return;
        const n = String(nextVal);
        const p = String(prevVal);
        el.innerHTML = "";
        el.classList.remove('flipping');
        el.innerHTML = `<div class="panel top-p"><div class="text-node">${{n}}</div></div>
                        <div class="panel bottom-p"><div class="text-node">${{p}}</div></div>
                        <div class="leaf-node">
                            <div class="leaf-side top-p"><div class="text-node">${{p}}</div></div>
                            <div class="leaf-side side-back bottom-p"><div class="text-node">${{n}}</div></div>
                        </div>`;
        requestAnimationFrame(() => {{ void el.offsetWidth; el.classList.add('flipping'); }});
    }}

    async function smartUpdate(id, target, isInitial = false) {{
        const tStr = (target === undefined || target === null) ? " " : String(target).toUpperCase();
        if (memory[id] === tStr || isBusy[id]) return;
        isBusy[id] = true;
        let oldStr = (memory[id] === undefined) ? " " : String(memory[id]);
        
        if (/^[0-9]$/.test(tStr)) {{
            let curN = /^[0-9]$/.test(oldStr) ? parseInt(oldStr) : 0;
            while (String(curN) !== tStr) {{
                let prev = String(curN);
                curN = (curN + 1) % 10;
                performFlip(id, String(curN), prev);
                await new Promise(r => setTimeout(r, baseSpeed * 0.8));
            }}
        } else {{
            const steps = isInitial ? 8 : 4; 
            for (let i = 0; i < steps; i++) {{
                let randChar = charPool.length > 0 ? charPool[Math.floor(Math.random() * charPool.length)] : "X";
                performFlip(id, randChar, oldStr);
                oldStr = randChar;
                await new Promise(r => setTimeout(r, baseSpeed));
            }}
            performFlip(id, tStr, oldStr);
        }}
        memory[id] = tStr; 
        isBusy[id] = false;
    }}

    function init() {{
        const board = document.querySelector('.acrylic-board');
        const msgW = Math.min(80, Math.floor((board.offsetWidth - 60) / flapCount));
        document.documentElement.style.setProperty('--msg-w', msgW + 'px');
        document.getElementById('row-msg').innerHTML = Array.from({{length: flapCount}}, (_, i) => `<div class="card msg-unit" id="m${{i}}"></div>`).join('');
        document.getElementById('row-date').innerHTML = Array.from({{length: 10}}, (_, i) => `<div class="card small-unit" id="d${{i}}"></div>`).join('');
        document.getElementById('row-clock').innerHTML = `<div class="card small-unit" id="h0"></div><div class="card small-unit" id="h1"></div><div class="separator">:</div><div class="card small-unit" id="tm0"></div><div class="card small-unit" id="tm1"></div><div class="separator">:</div><div class="card small-unit" id="ts0"></div><div class="card small-unit" id="ts1"></div>`;
    }}

    function tick() {{
        const n = new Date();
        const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
        const days = ["SUN","MON","TUE","WED","THU","FRI","SAT"];
        const dStr = months[n.getMonth()] + " " + String(n.getDate()).padStart(2,'0') + " " + days[n.getDay()];
        dStr.split('').forEach((c, i) => smartUpdate(`d${{i}}`, c));
        const hh = String(n.getHours()).padStart(2, '0').split('');
        const mm = String(n.getMinutes()).padStart(2, '0').split('');
        const ss = String(n.getSeconds()).padStart(2, '0').split('');
        smartUpdate('h0', hh[0]); smartUpdate('h1', hh[1]);
        smartUpdate('tm0', mm[0]); smartUpdate('tm1', mm[1]);
        smartUpdate('ts0', ss[0]); smartUpdate('ts1', ss[1]);
    }}

    window.onload = () => {{
        init();
        const msgPages = [];
        for (let i = 0; i < fullText.length; i += flapCount) {{
            msgPages.push(fullText.substring(i, i + flapCount).padEnd(flapCount, ' ').split(''));
        }}
        let pIdx = 0;
        const rotateMsg = (isFirst = false) => {{
            if(msgPages.length === 0) return;
            msgPages[pIdx].forEach((c, i) => {{ setTimeout(() => smartUpdate(`m${{i}}`, c, isFirst), i * (baseSpeed * 1.5)); }});
            pIdx = (pIdx + 1) % msgPages.length;
        }};
        setTimeout(() => rotateMsg(true), 500); 
        tick(); setInterval(tick, 1000);
        if (msgPages.length > 1) setInterval(() => rotateMsg(false), {user_stay} * 1000);
    }};
</script>
</body>
</html>
"""

components.html(html_code, height=850, scrolling=False)
