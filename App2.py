import streamlit as st
import streamlit.components.v1 as components

# --- 1. 頁面設定 ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: transparent !important;}
    .stApp {background: transparent !important;}
    iframe {border: none; width: 100%; height: 100vh; overflow: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心 HTML (包含日期與時間的翻板邏輯) ---
html_code = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {
        --font-family: "PingFang TC", "Microsoft JhengHei", sans-serif;
        --flip-speed: 0.6s;
        --card-bg: linear-gradient(180deg, #3a3a3a 0%, #1a1a1a 50%, #000 51%, #222 100%);
    }
    body { 
        background: transparent; display: flex; flex-direction: column; justify-content: center; 
        align-items: center; height: 100vh; margin: 0; overflow: hidden; gap: 20px;
    }
    .row { display: flex; gap: 15px; align-items: center; }
    .time-group { display: flex; gap: 5px; }
    .separator { font-family: var(--font-family); font-size: 30px; color: rgba(255,255,255,0.2); font-weight: 900; }
    
    .flap-unit { 
        position: relative; width: 50px; height: 75px; 
        background: #000; border-radius: 6px; 
        font-family: var(--font-family); font-size: 50px; 
        font-weight: 900; color: #fff; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.7);
    }
    .half { 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center; 
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }
    .top { top: 0; height: calc(50% + 0.5px); align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.8); box-shadow: inset 0 1px 2px rgba(255,255,255,0.1); }
    .bottom { bottom: 0; height: 50%; align-items: flex-end; border-radius: 0 0 6px 6px; background: linear-gradient(180deg, #151515 0%, #000 100%); }
    .text { height: 75px; width: 100%; text-align: center; position: absolute; left: 0; line-height: 75px; }
    .top .text { top: 0; }
    .bottom .text { bottom: 0; }
    .leaf { position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 15; transform-origin: bottom; transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }
    .leaf-front { z-index: 16; background: var(--card-bg); border-radius: 6px 6px 0 0; } 
    .leaf-back { transform: rotateX(-180deg); z-index: 15; background: #111; display: flex; justify-content: center; align-items: flex-end; overflow: hidden; border-radius: 0 0 6px 6px; }
    .flipping { transform: rotateX(-180deg); }
    .flap-unit::before { content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px; background: rgba(0,0,0,0.9); transform: translateY(-50%); z-index: 60; }

    .footer-note { margin-top: 10px; font-family: var(--font-family); font-size: 14px; color: rgba(255, 255, 255, 0.3); letter-spacing: 2px; }

    @media (max-width: 480px) {
        .flap-unit { width: 32px; height: 48px; font-size: 30px; border-radius: 4px; }
        .text { height: 48px; line-height: 48px; }
        .row { gap: 8px; }
        .separator { font-size: 20px; }
    }
</style>
</head>
<body>
    <div class="row">
        <div class="time-group" id="year"></div>
        <div style="width: 10px;"></div> <div class="time-group" id="date"></div>
    </div>
    
    <div class="row">
        <div class="time-group" id="hours"></div>
        <div class="separator">:</div>
        <div class="time-group" id="minutes"></div>
        <div class="separator">:</div>
        <div class="time-group" id="seconds"></div>
    </div>

    <div class="footer-note">𓃥白六時鐘告示牌</div>

<script>
    function createFlapHTML(val) {
        return `
            <div class="flap-unit">
                <div class="half top base-top"><div class="text">${val}</div></div>
                <div class="half bottom base-bottom"><div class="text">${val}</div></div>
                <div class="leaf">
                    <div class="half top leaf-front"><div class="text">${val}</div></div>
                    <div class="half bottom leaf-back"><div class="text">${val}</div></div>
                </div>
            </div>`;
    }

    function initGroup(id, count) {
        const el = document.getElementById(id);
        let html = "";
        for(let i=0; i<count; i++) html += createFlapHTML('0');
        el.innerHTML = html;
    }

    function updateGroup(id, value, count) {
        const str = value.toString().padStart(count, '0');
        const group = document.getElementById(id);
        const units = group.querySelectorAll('.flap-unit');
        
        str.split('').forEach((num, i) => {
            const unit = units[i];
            const currentNum = unit.querySelector('.base-top .text').innerText;
            if (num !== currentNum) {
                const leaf = unit.querySelector('.leaf');
                unit.querySelector('.leaf-back .text').innerText = num;
                leaf.classList.add('flipping');
                
                setTimeout(() => {
                    unit.querySelector('.base-top .text').innerText = num;
                    unit.querySelector('.base-bottom .text').innerText = num;
                }, 300);

                leaf.addEventListener('transitionend', () => {
                    unit.querySelector('.leaf-front .text').innerText = num;
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    leaf.offsetHeight;
                    leaf.style.transition = '';
                }, {once: true});
            }
        });
    }

    function updateClock() {
        const now = new Date();
        // 更新年份 (4位)
        updateGroup('year', now.getFullYear(), 4);
        // 更新月日 (4位)
        const mmdd = (now.getMonth() + 1).toString().padStart(2, '0') + 
                     now.getDate().toString().padStart(2, '0');
        updateGroup('date', mmdd, 4);
        // 更新時間 (各2位)
        updateGroup('hours', now.getHours(), 2);
        updateGroup('minutes', now.getMinutes(), 2);
        updateGroup('seconds', now.getSeconds(), 2);
    }

    window.onload = () => {
        initGroup('year', 4);
        initGroup('date', 4);
        initGroup('hours', 2);
        initGroup('minutes', 2);
        initGroup('seconds', 2);
        setInterval(updateClock, 1000);
        updateClock();
    };
</script>
</body>
</html>
"""

components.html(html_code, height=600)
