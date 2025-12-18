import streamlit as st
import streamlit.components.v1 as components

# --- 1. 頁面設定 ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: transparent !important;}
    .stApp {background: transparent !important;}
    iframe {border: none; width: 100%; height: 100vh; overflow: hidden; margin-top: -50px;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心 HTML (包含三種字體風格切換) ---
html_code = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    :root {
        --font-family: "PingFang TC", "Microsoft JhengHei", sans-serif;
        --flip-speed: 0.6s;
        --card-bg: linear-gradient(180deg, #3a3a3a 0%, #1a1a1a 50%, #000 51%, #222 100%);
    }
    /* 字體風格定義 */
    body.font-style-0 { --font-family: "PingFang TC", "Microsoft JhengHei", sans-serif; }
    body.font-style-1 { --font-family: "Noto Serif TC", "PMingLiU", "Apple LiSung", serif; }
    body.font-style-2 { --font-family: "STKaiti", "BiauKai", "DFKai-SB", cursive; }

    body { 
        background: transparent; display: flex; flex-direction: column; 
        justify-content: flex-start; align-items: center; 
        height: 100vh; margin: 0; padding-top: 40px; 
        overflow: hidden; gap: 12px;
        user-select: none; -webkit-user-select: none;
    }
    .row { display: flex; gap: 6px; align-items: center; justify-content: center; width: 100%; }
    .time-group { display: flex; gap: 4px; }
    
    .date-separator { 
        font-family: var(--font-family); font-size: 32px; color: rgba(255,255,255,0.4); 
        font-weight: 900; padding: 0 2px;
    }
    .colon-separator { font-family: var(--font-family); font-size: 20px; color: rgba(255,255,255,0.15); font-weight: 900; }
    
    .flap-unit { 
        position: relative; width: 42px; height: 62px; 
        background: #000; border-radius: 5px; 
        font-family: var(--font-family); font-size: 42px; 
        font-weight: 900; color: #fff; 
        box-shadow: 0 8px 15px rgba(0,0,0,0.6);
    }
    .half { 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center; 
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }
    .top { top: 0; height: calc(50% + 0.5px); align-items: flex-start; border-radius: 5px 5px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.8); }
    .bottom { bottom: 0; height: 50%; align-items: flex-end; border-radius: 0 0 5px 5px; background: linear-gradient(180deg, #151515 0%, #000 100%); }
    .text { height: 62px; width: 100%; text-align: center; position: absolute; left: 0; line-height: 62px; }
    .top .text { top: 0; }
    .bottom .text { bottom: 0; }
    .leaf { position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 15; transform-origin: bottom; transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }
    .leaf-front { z-index: 16; background: var(--card-bg); border-radius: 5px 5px 0 0; } 
    .leaf-back { transform: rotateX(-180deg); z-index: 15; background: #111; display: flex; justify-content: center; align-items: flex-end; overflow: hidden; border-radius: 0 0 5px 5px; }
    .flipping { transform: rotateX(-180deg); }
    .flap-unit::before { content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px; background: rgba(0,0,0,0.95); transform: translateY(-50%); z-index: 60; }

    .small-row .flap-unit { width: 32px; height: 48px; font-size: 26px; }
    .small-row .text { height: 48px; line-height: 48px; }

    .weather-box { cursor: pointer; border-radius: 12px; padding: 5px; }

    #style-switcher {
        position: fixed; left: 20px; bottom: 20px; width: 40px; height: 40px;
        background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
        color: rgba(255,255,255,0.3); font-size: 18px; cursor: pointer; z-index: 100;
        transition: 0.3s;
    }
    #style-switcher:active { transform: scale(0.9); background: rgba(255,255,255,0.15); }

    .footer-note { margin-top: 20px; font-family: var(--font-family); font-size: 11px; color: rgba(255, 255, 255, 0.1); letter-spacing: 2px; }

    @media (max-width: 480px) {
        .flap-unit { width: 38px; height: 56px; font-size: 38px; }
        .text { height: 56px; line-height: 56px; }
    }
</style>
</head>
<body class="font-style-0">
    <div id="style-switcher">A</div>

    <div class="row">
        <div class="time-group" id="year"></div>
    </div>
    
    <div class="row">
        <div class="time-group" id="month"></div>
        <div class="date-separator">/</div>
        <div class="time-group" id="day"></div>
    </div>
    
    <div class="row small-row">
        <div class="time-group" id="lunar"></div>
        <div class="colon-separator">·</div>
        <div class="time-group" id="solar-term"></div>
    </div>

    <div class="row small-row weather-box" id="weather-trigger">
        <div class="time-group" id="weather-city"></div>
        <div style="width:4px"></div>
        <div class="time-group" id="weather-desc"></div>
        <div style="width:4px"></div>
        <div class="time-group" id="weather-temp"></div>
    </div>

    <div class="row">
        <div class="time-group" id="hours"></div>
        <div class="colon-separator">:</div>
        <div class="time-group" id="minutes"></div>
        <div class="colon-separator">:</div>
        <div class="time-group" id="seconds"></div>
    </div>

    <div class="footer-note">𓃥白六萬年曆</div>

<script src="https://cdn.jsdelivr.net/npm/lunar-javascript/lunar.js"></script>
<script>
    const cities = ["台北", "新北", "桃園", "新竹", "台中", "彰化", "嘉義", "台南", "高雄", "宜蘭", "花蓮", "台東"];
    const forecasts = ["晴天", "多雲", "陰天", "小雨", "雷雨", "大雨", "霧天"];
    let cityIdx = 0;
    let fontIdx = 0;

    function createFlap(val) {
        return `<div class="flap-unit">
            <div class="half top base-top"><div class="text">${val}</div></div>
            <div class="half bottom base-bottom"><div class="text">${val}</div></div>
            <div class="leaf">
                <div class="half top leaf-front"><div class="text">${val}</div></div>
                <div class="half bottom leaf-back"><div class="text">${val}</div></div>
            </div>
        </div>`;
    }

    function updateGroup(id, value, pad=0) {
        let str = value.toString();
        if(pad > 0) str = str.padStart(pad, '0');
        const group = document.getElementById(id);
        let units = group.querySelectorAll('.flap-unit');
        if (units.length !== str.length) {
            group.innerHTML = str.split('').map(c => createFlap(c)).join('');
            units = group.querySelectorAll('.flap-unit');
        }
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

    function refreshWeather() {
        const cityName = cities[cityIdx];
        const desc = forecasts[Math.floor(Math.random() * forecasts.length)];
        const temp = (18 + Math.floor(Math.random() * 10)) + "°";
        updateGroup('weather-city', cityName);
        updateGroup('weather-desc', desc);
        updateGroup('weather-temp', temp);
    }

    function tick() {
        const now = new Date();
        const lunar = Lunar.fromDate(now);
        updateGroup('year', now.getFullYear());
        updateGroup('month', (now.getMonth() + 1), 2);
        updateGroup('day', now.getDate(), 2);
        updateGroup('lunar', lunar.getMonthInChinese() + "月" + lunar.getDayInChinese());
        updateGroup('solar-term', lunar.getJieQi() || lunar.getPrevJieQi().getName());
        updateGroup('hours', now.getHours(), 2);
        updateGroup('minutes', now.getMinutes(), 2);
        updateGroup('seconds', now.getSeconds(), 2);
    }

    window.onload = () => {
        tick();
        refreshWeather();
        setInterval(tick, 1000);

        const wArea = document.getElementById('weather-trigger');
        const change = () => { cityIdx = (cityIdx + 1) % cities.length; refreshWeather(); };
        wArea.addEventListener('click', change);
        wArea.addEventListener('touchstart', (e) => { e.preventDefault(); change(); }, {passive: false});

        const styleBtn = document.getElementById('style-switcher');
        styleBtn.addEventListener('click', () => {
            document.body.classList.remove(`font-style-${fontIdx}`);
            fontIdx = (fontIdx + 1) % 3;
            document.body.classList.add(`font-style-${fontIdx}`);
        });
    };
</script>
</body>
</html>
"""

# --- 3. 渲染組件 ---
components.html(html_code, height=900)
