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

# --- 2. 核心 HTML (翻板時鐘邏輯) ---
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
        align-items: center; height: 100vh; margin: 0; overflow: hidden; 
    }
    .clock-container { display: flex; gap: 15px; align-items: center; }
    .time-group { display: flex; gap: 5px; }
    .separator { font-family: var(--font-family); font-size: 40px; color: rgba(255,255,255,0.3); font-weight: 900; padding-bottom: 10px; }
    
    .flap-unit { 
        position: relative; width: 60px; height: 90px; 
        background: #000; border-radius: 6px; 
        font-family: var(--font-family); font-size: 65px; 
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
    .text { height: 90px; width: 100%; text-align: center; position: absolute; left: 0; line-height: 90px; }
    .top .text { top: 0; }
    .bottom .text { bottom: 0; }
    .leaf { position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 15; transform-origin: bottom; transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }
    .leaf-front { z-index: 16; background: var(--card-bg); border-radius: 6px 6px 0 0; } 
    .leaf-back { transform: rotateX(-180deg); z-index: 15; background: #111; display: flex; justify-content: center; align-items: flex-end; overflow: hidden; border-radius: 0 0 6px 6px; }
    .flipping { transform: rotateX(-180deg); }
    .flap-unit::before { content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px; background: rgba(0,0,0,0.9); transform: translateY(-50%); z-index: 60; }

    .footer-note { margin-top: 30px; font-family: var(--font-family); font-size: 14px; color: rgba(255, 255, 255, 0.3); letter-spacing: 2px; }

    @media (max-width: 480px) {
        .flap-unit { width: 40px; height: 60px; font-size: 40px; }
        .text { height: 60px; line-height: 60px; }
        .clock-container { gap: 8px; }
    }
</style>
</head>
<body>
    <div class="clock-container">
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

    function initGroup(id) {
        const el = document.getElementById(id);
        el.innerHTML = createFlapHTML('0') + createFlapHTML('0');
    }

    function updateGroup(id, value) {
        const str = value.toString().padStart(2, '0');
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
        updateGroup('hours', now.getHours());
        updateGroup('minutes', now.getMinutes());
        updateGroup('seconds', now.getSeconds());
    }

    window.onload = () => {
        initGroup('hours');
        initGroup('minutes');
        initGroup('seconds');
        setInterval(updateClock, 1000);
        updateClock();
    };
</script>
</body>
</html>
"""

components.html(html_code, height=600)
