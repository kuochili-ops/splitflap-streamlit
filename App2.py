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

# --- 2. 核心 HTML (包含農曆與天氣邏輯) ---
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
    body { 
        background: transparent; display: flex; flex-direction: column; justify-content: center; 
        align-items: center; height: 100vh; margin: 0; overflow: hidden; gap: 8px;
        user-select: none; -webkit-user-select: none;
    }
    .row { display: flex; gap: 6px; align-items: center; justify-content: center; width: 100%; }
    .time-group { display: flex; gap: 3px; }
    .separator { font-family: var(--font-family); font-size: 18px; color: rgba(255,255,255,0.15); font-weight: 900; }
    
    /* 翻板基礎單位 */
    .flap-unit { 
        position: relative; width: 38px; height: 55px; 
        background: #000; border-radius: 4px; 
        font-family: var(--font-family); font-size: 38px; 
        font-weight: 900; color: #fff; 
        box-shadow: 0 6px 15px rgba(0,0,0,0.6);
    }
    .half { 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center; 
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }
    .top { top: 0; height: calc(50% + 0.5px); align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.8); }
    .bottom { bottom: 0; height: 50%; align-items: flex-end; border-radius: 0 0 4px 4px; background: linear-gradient(180deg, #151515 0%, #000 100%); }
    .text { height: 55px; width: 100%; text-align: center; position: absolute; left: 0; line-height: 55px; }
    .top .text { top: 0; }
    .bottom .text { bottom: 0; }
    .leaf { position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 15; transform-origin: bottom; transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }
    .leaf-front { z-index: 16; background: var(--card-bg); border-radius: 4px 4px 0 0; } 
    .leaf-back { transform: rotateX(-180deg); z-index: 15; background: #111; display: flex; justify-content: center; align-items: flex-end; overflow: hidden; border-radius: 0 0 4px 4px; }
    .flipping { transform: rotateX(-180deg); }
    .flap-unit::before { content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 1.5px; background: rgba(0,0,0,0.9); transform: translateY(-50%); z-index: 60; }

    /* 輔助資訊列 (農曆/星期/節氣) */
    .small-flap .flap-unit { width: 30px; height: 42px; font-size: 24px; }
    .small-flap .text { height: 42px; line-height: 42px; }

    /* 天氣列觸碰區域 */
    .weather-active-area { cursor: pointer; padding: 5px; border-radius: 12px; transition: 0.2s; }
    .weather-active-area:active { transform: scale(0.98); background: rgba(255,255,255,0.05); }

    .footer-note { margin-top: 10px; font-family: var(--font-family); font-size: 11px; color: rgba(255, 255, 255, 0.15); letter-spacing: 1px; }
</style>
</head>
<body>
    <div class="row small-flap">
        <div class="time-group" id="year"></div>
        <div class="separator">/</div>
        <div class="time-group" id="dayOfWeek"></div>
    </div>
    
    <div class="row small-flap">
        <div class="time-group" id="lunar-date"></div>
        <div class="separator">·</div>
        <div class="time-group" id="solar-term"></div>
    </div>

    <div class="row">
        <div class="time-group" id="date"></div>
    </div>
    
    <div class="row small-flap weather-active-area" id="weather-trigger">
        <div id="weather-city" class="time-group"></div>
        <div style="width:5px"></div>
        <div id="weather-desc" class="time-group"></div>
        <div style="width:5px"></div>
        <div id="weather-temp" class="time-group"></div>
    </div>

    <div class="row">
        <div class="time-group" id="hours"></div>
        <div class="separator">:</div>
        <div class="time-group" id="minutes"></div>
        <div class="separator">:</div>
        <div class="time-group" id="seconds"></div>
    </div>

    <div class="footer-note">𓃥白六萬年曆時鐘</div>

<script src="https://cdn.jsdelivr.net/npm/lunar-javascript/lunar.js"></script>
<script>
    const cities = ["台北", "新北", "桃園", "新竹", "台中", "彰化", "嘉義", "台南", "高雄", "宜蘭", "花蓮", "台東"];
    const weatherStates = ["晴", "雲", "陰", "雨"];
    let cityIndex = 0;

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

    function updateGroup(id, value) {
        let str = value.toString();
        const group = document.getElementById(id);
        let units = group.querySelectorAll('.flap-unit');
        
        if (units.length !== str.length) {
            group.innerHTML = str.split('').map(c => createFlapHTML(c)).join('');
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

    function updateWeather() {
        const cityName = cities[cityIndex];
        // 隨機生成氣候與溫度（真實應用可介接 API）
        const desc = weatherStates[Math.floor(Math.random() * weatherStates.length)];
        const temp = (20 + (cityIndex % 5)) + "°";
        
        updateGroup('weather-city', cityName);
        updateGroup('weather-desc', desc);
        updateGroup('weather-temp', temp);
    }

    function updateClock() {
        const now = new Date();
        const lunar = Lunar.fromDate(now);
        
        // 年 & 星期
        updateGroup('year', now.getFullYear());
        updateGroup('dayOfWeek', "週" + "日一二三四五六"[now.getDay()]);
        
        // 農曆 (取月日，例如 十一廿八)
        const lunarStr = lunar.getMonthInChinese() + "月" + lunar.getDayInChinese();
        updateGroup('lunar-date', lunarStr);
        
        // 節氣 (若當天無節氣則顯示當月節氣)
        const term = lunar.getJieQi() || lunar.getPrevJieQi().getName();
        updateGroup('solar-term', term);
        
        // 西曆月日
        const mmdd = (now.getMonth() + 1).toString().padStart(2, '0') + 
                     now.getDate().toString().padStart(2, '0');
        updateGroup('date', mmdd);
        
        // 時間
        updateGroup('hours', now.getHours().toString().padStart(2, '0'));
        updateGroup('minutes', now.getMinutes().toString().padStart(2, '0'));
        updateGroup('seconds', now.getSeconds().toString().padStart(2, '0'));
    }

    window.onload = () => {
        updateClock();
        updateWeather();
        setInterval(updateClock, 1000);

        const weatherArea = document.getElementById('weather-trigger');
        const trigger = () => {
            cityIndex = (cityIndex + 1) % cities.length;
            updateWeather();
        };
        weatherArea.addEventListener('click', trigger);
        weatherArea.addEventListener('touchstart', (e) => {
            e.preventDefault();
            trigger();
        }, {passive: false});
    };
</script>
</body>
</html>
"""

components.html(html_code, height=850)
