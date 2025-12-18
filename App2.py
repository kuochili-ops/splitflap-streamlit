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

# --- 2. 核心 HTML ---
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
        align-items: center; height: 100vh; margin: 0; overflow: hidden; gap: 10px;
        user-select: none; -webkit-user-select: none;
    }
    .row { display: flex; gap: 8px; align-items: center; justify-content: center; width: 100%; }
    .time-group { display: flex; gap: 4px; }
    .separator { font-family: var(--font-family); font-size: 20px; color: rgba(255,255,255,0.2); font-weight: 900; }
    
    /* 翻板基礎單位 */
    .flap-unit { 
        position: relative; width: 40px; height: 60px; 
        background: #000; border-radius: 4px; 
        font-family: var(--font-family); font-size: 40px; 
        font-weight: 900; color: #fff; 
        box-shadow: 0 8px 20px rgba(0,0,0,0.7);
    }
    .half { 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center; 
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }
    .top { top: 0; height: calc(50% + 0.5px); align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.8); }
    .bottom { bottom: 0; height: 50%; align-items: flex-end; border-radius: 0 0 4px 4px; background: linear-gradient(180deg, #151515 0%, #000 100%); }
    .text { height: 60px; width: 100%; text-align: center; position: absolute; left: 0; line-height: 60px; }
    .top .text { top: 0; }
    .bottom .text { bottom: 0; }
    .leaf { position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 15; transform-origin: bottom; transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }
    .leaf-front { z-index: 16; background: var(--card-bg); border-radius: 4px 4px 0 0; } 
    .leaf-back { transform: rotateX(-180deg); z-index: 15; background: #111; display: flex; justify-content: center; align-items: flex-end; overflow: hidden; border-radius: 0 0 4px 4px; }
    .flipping { transform: rotateX(-180deg); }
    .flap-unit::before { content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 1.5px; background: rgba(0,0,0,0.9); transform: translateY(-50%); z-index: 60; }

    /* 天氣專用小尺寸翻板 */
    .small-flap .flap-unit { width: 30px; height: 45px; font-size: 24px; }
    .small-flap .text { height: 45px; line-height: 45px; }

    .city-selector { 
        margin-top: 5px; cursor: pointer; color: #55acee; font-family: var(--font-family); 
        font-weight: bold; font-size: 18px; padding: 5px 15px; border: 1px solid rgba(85,172,238,0.3); border-radius: 20px;
    }
    .footer-note { margin-top: 5px; font-family: var(--font-family); font-size: 12px; color: rgba(255, 255, 255, 0.2); }
</style>
</head>
<body>
    <div class="row">
        <div class="time-group" id="year"></div>
        <div class="separator">/</div>
        <div class="time-group" id="dayOfWeek"></div>
    </div>
    
    <div class="row">
        <div class="time-group" id="date"></div>
    </div>
    
    <div class="row small-flap">
        <div id="weather-city" class="time-group"></div>
        <div style="width:10px"></div>
        <div id="weather-temp" class="time-group"></div>
    </div>
    <div class="city-selector" id="city-btn">📍 點擊切換縣市</div>

    <div class="row">
        <div class="time-group" id="hours"></div>
        <div class="separator">:</div>
        <div class="time-group" id="minutes"></div>
        <div class="separator">:</div>
        <div class="time-group" id="seconds"></div>
    </div>

    <div class="footer-note">𓃥白六全功能告示牌</div>

<script>
    const cities = ["台北", "台中", "高雄", "宜蘭", "花蓮", "台東", "台南", "新竹"];
    let cityIndex = 0;
    const weekDays = ["日", "一", "二", "三", "四", "五", "六"];

    function createFlapHTML(val) {
        return `<div class="flap-unit">
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
        el.innerHTML = Array(count).fill(0).map(() => createFlapHTML(' ')).join('');
    }

    function updateGroup(id, value) {
        const str = value.toString();
        const group = document.getElementById(id);
        const units = group.querySelectorAll('.flap-unit');
        
        // 如果翻板數量不夠，自動補齊
        if (units.length !== str.length) {
            group.innerHTML = str.split('').map(c => createFlapHTML(c)).join('');
            return;
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

    // 模擬天氣數據 (實際環境可介接 API)
    function updateWeather() {
        const mockTemps = {"台北":"22", "台中":"24", "高雄":"26", "宜蘭":"21", "花蓮":"22", "台東":"23", "台南":"25", "新竹":"22"};
        const cityName = cities[cityIndex];
        const temp = mockTemps[cityName] + "°";
        updateGroup('weather-city', cityName);
        updateGroup('weather-temp', temp);
    }

    function updateClock() {
        const now = new Date();
        updateGroup('year', now.getFullYear());
        updateGroup('dayOfWeek', weekDays[now.getDay()]);
        
        const mmdd = (now.getMonth() + 1).toString().padStart(2, '0') + 
                     now.getDate().toString().padStart(2, '0');
        updateGroup('date', mmdd);
        
        updateGroup('hours', now.getHours().toString().padStart(2, '0'));
        updateGroup('minutes', now.getMinutes().toString().padStart(2, '0'));
        updateGroup('seconds', now.getSeconds().toString().padStart(2, '0'));
    }

    window.onload = () => {
        initGroup('year', 4);
        initGroup('dayOfWeek', 1);
        initGroup('date', 4);
        initGroup('weather-city', 2);
        initGroup('weather-temp', 3);
        initGroup('hours', 2);
        initGroup('minutes', 2);
        initGroup('seconds', 2);
        
        setInterval(updateClock, 1000);
        updateClock();
        updateWeather();

        // 觸碰/點擊切換縣市
        const btn = document.getElementById('city-btn');
        const trigger = () => {
            cityIndex = (cityIndex + 1) % cities.length;
            updateWeather();
        };
        btn.addEventListener('click', trigger);
        btn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            trigger();
        });
    };
</script>
</body>
</html>
"""

components.html(html_code, height=800)
