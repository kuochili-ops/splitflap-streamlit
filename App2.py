import streamlit as st
import streamlit.components.v1 as components
import requests
import json

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

# --- 2. OpenWeatherMap 數據處理 ---
OWM_API_KEY = "Dcd113bba5675965ccf9e60a7e6d06e5"

# 定義台灣主要城市的經緯度
CITY_LIST = {
    "台北": {"lat": 25.03, "lon": 121.56},
    "台中": {"lat": 24.14, "lon": 120.67},
    "高雄": {"lat": 22.61, "lon": 120.30},
    "台南": {"lat": 22.99, "lon": 120.21},
    "桃園": {"lat": 24.99, "lon": 121.31},
    "新竹": {"lat": 24.81, "lon": 120.96},
    "宜蘭": {"lat": 24.70, "lon": 121.76},
    "花蓮": {"lat": 23.97, "lon": 121.60}
}

def get_real_weather():
    weather_results = {}
    for city, pos in CITY_LIST.items():
        # 使用 units=metric 取得攝氏溫度，lang=zh_tw 取得中文描述
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={pos['lat']}&lon={pos['lon']}&appid={OWM_API_KEY}&units=metric&lang=zh_tw"
        try:
            res = requests.get(url, timeout=3)
            data = res.json()
            # 取得描述並修剪為兩個字
            raw_desc = data['weather'][0]['description']
            if "晴" in raw_desc: short_desc = "晴天"
            elif "雲" in raw_desc: short_desc = "多雲"
            elif "雨" in raw_desc: short_desc = "雨天"
            elif "陰" in raw_desc: short_desc = "陰天"
            else: short_desc = raw_desc[:2]
            
            temp = f"{round(data['main']['temp'])}°"
            weather_results[city] = {"desc": short_desc, "temp": temp}
        except:
            continue
    return weather_results

# 預先抓取資料
current_weather = get_real_weather()
# 若 API 尚未啟用或失敗，提供保險數據
if not current_weather:
    current_weather = {"台北": {"desc": "連線", "temp": "中"}}

weather_json = json.dumps(current_weather)

# --- 3. 核心 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    :root {{
        --font-family: "PingFang TC", "Microsoft JhengHei", sans-serif;
        --flip-speed: 0.6s;
        --card-bg: linear-gradient(180deg, #3a3a3a 0%, #1a1a1a 50%, #000 51%, #222 100%);
    }}
    body.font-style-0 {{ --font-family: "PingFang TC", "Microsoft JhengHei", sans-serif; }}
    body.font-style-1 {{ --font-family: "Noto Serif TC", "PMingLiU", serif; }}
    body.font-style-2 {{ --font-family: "STKaiti", "BiauKai", "DFKai-SB", cursive; }}

    body {{ 
        background: transparent; display: flex; flex-direction: column; 
        justify-content: flex-start; align-items: center; 
        height: 100vh; margin: 0; padding-top: 40px; 
        overflow: hidden; gap: 12px;
        user-select: none;
    }}
    .row {{ display: flex; gap: 6px; align-items: center; justify-content: center; width: 100%; }}
    .time-group {{ display: flex; gap: 4px; }}
    .date-separator {{ font-family: var(--font-family); font-size: 32px; color: rgba(255,255,255,0.4); font-weight: 900; }}
    .colon-separator {{ font-family: var(--font-family); font-size: 20px; color: rgba(255,255,255,0.15); font-weight: 900; }}
    
    .flap-unit {{ 
        position: relative; width: 42px; height: 62px; 
        background: #000; border-radius: 5px; 
        font-family: var(--font-family); font-size: 42px; 
        font-weight: 900; color: #fff; 
        box-shadow: 0 8px 15px rgba(0,0,0,0.6);
    }}
    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center; 
        backface-visibility: hidden;
    }}
    .top {{ top: 0; height: calc(50% + 0.5px); align-items: flex-start; border-radius: 5px 5px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.8); }}
    .bottom {{ bottom: 0; height: 50%; align-items: flex-end; border-radius: 0 0 5px 5px; background: linear-gradient(180deg, #151515 0%, #000 100%); }}
    .text {{ height: 62px; width: 100%; text-align: center; position: absolute; left: 0; line-height: 62px; }}
    .top .text {{ top: 0; }}
    .bottom .text {{ bottom: 0; }}
    .leaf {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 15; transform-origin: bottom; transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }}
    .leaf-front {{ z-index: 16; background: var(--card-bg); border-radius: 5px 5px 0 0; }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #111; display: flex; justify-content: center; align-items: flex-end; overflow: hidden; border-radius: 0 0 5px 5px; }}
    .flipping {{ transform: rotateX(-180deg); }}
    .flap-unit::before {{ content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px; background: rgba(0,0,0,0.95); transform: translateY(-50%); z-index: 60; }}

    .small-row .flap-unit {{ width: 32px; height: 48px; font-size: 26px; }}
    .small-row .text {{ height: 48px; line-height: 48px; }}

    .weather-box {{ cursor: pointer; border-radius: 12px; padding: 5px; }}

    #style-switcher {{
        position: fixed; left: 20px; bottom: 20px; width: 40px; height: 40px;
        background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
        color: rgba(255,255,255,0.3); font-size: 18px; cursor: pointer; z-index: 100;
    }}

    @media (max-width: 480px) {{
        .flap-unit {{ width: 38px; height: 56px; font-size: 38px; }}
        .text {{ height: 56px; line-height: 56px; }}
    }}
</style>
</head>
<body class="font-style-0">
    <div id="style-switcher">A</div>

    <div class="row"><div class="time-group" id="year"></div></div>
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

<script src="https://cdn.jsdelivr.net/npm/lunar-javascript/lunar.js"></script>
<script>
    const weatherData = {weather_json};
    const cities = Object.keys(weatherData).length > 0 ? Object.keys(weatherData) : ["台北"];
    let cityIdx = 0;
    let fontIdx = 0;

    function createFlap(val) {{
        return `<div class="flap-unit">
            <div class="half top base-top"><div class="text">${{val}}</div></div>
            <div class="half bottom base-bottom"><div class="text">${{val}}</div></div>
            <div class="leaf">
                <div class="half top leaf-front"><div class="text">${{val}}</div></div>
                <div class="half bottom leaf-back"><div class="text">${{val}}</div></div>
            </div>
        </div>`;
    }}

    function updateGroup(id, value, pad=0) {{
        let str = value.toString();
        if(pad > 0) str = str.padStart(pad, '0');
        const group = document.getElementById(id);
        let units = group.querySelectorAll('.flap-unit');
        if (units.length !== str.length) {{
            group.innerHTML = str.split('').map(c => createFlap(c)).join('');
            units = group.querySelectorAll('.flap-unit');
        }}
        str.split('').forEach((num, i) => {{
            const unit = units[i];
            const currentNum = unit.querySelector('.base-top .text').innerText;
            if (num !== currentNum) {{
                const leaf = unit.querySelector('.leaf');
                unit.querySelector('.leaf-back .text').innerText = num;
                leaf.classList.add('flipping');
                setTimeout(() => {{
                    unit.querySelector('.base-top .text').innerText = num;
                    unit.querySelector('.base-bottom .text').innerText = num;
                }}, 300);
                leaf.addEventListener('transitionend', () => {{
                    unit.querySelector('.leaf-front .text').innerText = num;
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    leaf.offsetHeight;
                    leaf.style.transition = '';
                }}, {{once: true}});
            }}
        }});
    }}

    function refreshWeather() {{
        const cityName = cities[cityIdx];
        const data = weatherData[cityName] || {{desc: "--", temp: "--°"}};
        updateGroup('weather-city', cityName);
        updateGroup('weather-desc', data.desc);
        updateGroup('weather-temp', data.temp);
    }}

    function tick() {{
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
    }}

    window.onload = () => {{
        tick();
        refreshWeather();
        setInterval(tick, 1000);
        
        document.getElementById('weather-trigger').onclick = () => {{
            cityIdx = (cityIdx + 1) % cities.length;
            refreshWeather();
        }};
        
        document.getElementById('style-switcher').onclick = () => {{
            document.body.classList.remove(`font-style-${{fontIdx}}`);
            fontIdx = (fontIdx + 1) % 3;
            document.body.classList.add(`font-style-${{fontIdx}}`);
        }};
    }};
</script>
</body>
</html>
"""

components.html(html_code, height=900)
