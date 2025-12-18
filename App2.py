import streamlit as st
import streamlit.components.v1 as components
import requests
import json

# --- 1. 頁面設定 ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: #222 !important;}
    iframe {border: none; width: 100%; height: 100vh; overflow: hidden; margin-top: -50px;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 天氣數據 ---
OWM_API_KEY = "Dcd113bba5675965ccf9e60a7e6d06e5"
CITY_LIST = {"台北": {"lat": 25.03, "lon": 121.56}, "台中": {"lat": 24.14, "lon": 120.67}, "高雄": {"lat": 22.61, "lon": 120.30}}

def get_all_weather():
    results = {}
    for city, pos in CITY_LIST.items():
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={pos['lat']}&lon={pos['lon']}&appid={OWM_API_KEY}&units=metric&lang=zh_tw"
        try:
            res = requests.get(url, timeout=2).json()
            results[city] = {"desc": res['weather'][0]['description'][:2], "temp": f"{round(res['main']['temp'])}°"}
        except: continue
    return results

weather_json = json.dumps(get_all_weather() or {"台北": {"desc": "多雲", "temp": "21°"}})

# --- 3. 核心 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    :root {{ --flip-speed: 0.6s; }}
    
    /* Style 1: 強制清水模背景 (Concrete Wall) */
    body.style-1 {{
        background: url('https://www.transparenttextures.com/patterns/concrete-wall.png'), #999; 
        background-color: #888;
        background-image: url('https://images.unsplash.com/photo-1523712999610-f77fbcfc3843?q=80&w=2070&auto=format&fit=crop'); /* 真實水泥牆圖 */
        background-size: cover;
        --card-bg: rgba(40, 40, 40, 0.6);
        --shadow: 20px 20px 40px rgba(0,0,0,0.5), 5px 5px 15px rgba(0,0,0,0.2);
    }}
    
    /* Style 0: 純黑模式 */
    body.style-0 {{
        background: #111;
        --card-bg: #222;
        --shadow: 0 10px 20px rgba(0,0,0,0.8);
    }}

    body.font-0 {{ --font-family: sans-serif; }}
    body.font-1 {{ --font-family: serif; }}
    body.font-2 {{ --font-family: cursive; }}

    body {{ 
        display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
        height: 100vh; margin: 0; padding-top: 60px; gap: 20px; transition: 0.5s; overflow: hidden;
    }}

    .row {{ display: flex; gap: 8px; align-items: center; }}
    .flap-unit {{ 
        position: relative; width: 46px; height: 70px; background: #111; border-radius: 6px;
        font-family: var(--font-family); font-size: 48px; font-weight: 900; color: #fff;
        box-shadow: var(--shadow);
    }}
    
    .half {{ 
        position: absolute; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); backdrop-filter: blur(5px);
        display: flex; justify-content: center; backface-visibility: hidden;
    }}
    
    .top {{ top: 0; align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.5); }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 6px 6px; }}
    .text {{ height: 70px; line-height: 70px; }}

    .leaf {{ position: absolute; top: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }}
    .leaf-front {{ background: var(--card-bg); z-index: 12; border-radius: 6px 6px 0 0; }}
    .leaf-back {{ background: #111; transform: rotateX(-180deg); z-index: 11; border-radius: 0 0 6px 6px; display: flex; align-items: flex-end; justify-content: center; }}
    .flipping {{ transform: rotateX(-180deg); }}

    .small .flap-unit {{ width: 34px; height: 52px; font-size: 28px; }}
    .small .text {{ height: 52px; line-height: 52px; }}

    /* 控制鈕設計 */
    .controls {{ position: fixed; left: 20px; bottom: 20px; display: flex; gap: 10px; }}
    .btn {{
        width: 45px; height: 45px; border-radius: 50%; background: rgba(0,0,0,0.5);
        border: 2px solid #fff; color: white; display: flex; align-items: center; justify-content: center;
        cursor: pointer; font-weight: bold; font-family: sans-serif;
    }}
    .weather-trigger {{ cursor: pointer; }}
</style>
</head>
<body class="style-1 font-0">
    <div class="controls">
        <div id="btn-font" class="btn">A</div>
        <div id="btn-style" class="btn">S</div>
    </div>

    <div class="row" id="year"></div>
    <div class="row"><div id="month" class="row"></div><div style="color:white;opacity:0.3;font-size:30px">/</div><div id="day" class="row"></div></div>
    <div class="row small" id="lunar"></div>
    <div class="row small weather-trigger" id="weather-go">
        <div id="w-city" class="row"></div>
        <div id="w-desc" class="row" style="margin:0 6px"></div>
        <div id="w-temp" class="row"></div>
    </div>
    <div class="row" id="time"></div>

<script src="https://cdn.jsdelivr.net/npm/lunar-javascript/lunar.js"></script>
<script>
    const weatherData = {weather_json};
    const cities = Object.keys(weatherData);
    let cityIdx = 0, fontIdx = 0, styleIdx = 1;

    function createUnit(v) {{
        return `<div class="flap-unit">
            <div class="half top base-top"><div class="text">${{v}}</div></div>
            <div class="half bottom base-bottom"><div class="text">${{v}}</div></div>
            <div class="leaf">
                <div class="half top leaf-front"><div class="text">${{v}}</div></div>
                <div class="half bottom leaf-back"><div class="text">${{v}}</div></div>
            </div>
        </div>`;
    }}

    function update(id, val, pad=0) {{
        let s = val.toString(); if(pad) s = s.padStart(pad,'0');
        const container = document.getElementById(id);
        if(container.children.length !== s.length) container.innerHTML = s.split('').map(c=>createUnit(c)).join('');
        [...s].forEach((n, i) => {{
            const unit = container.children[i];
            const currentVal = unit.querySelector('.base-top .text').innerText;
            if(n !== currentVal) {{
                const leaf = unit.querySelector('.leaf');
                unit.querySelector('.leaf-back .text').innerText = n;
                leaf.classList.add('flipping');
                setTimeout(() => {{
                    unit.querySelector('.base-top .text').innerText = n;
                    unit.querySelector('.base-bottom .text').innerText = n;
                }}, 300);
                leaf.addEventListener('transitionend', () => {{
                    unit.querySelector('.leaf-front .text').innerText = n;
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    leaf.offsetHeight;
                    leaf.style.transition = '';
                }}, {{once: true}});
            }}
        }});
    }}

    function tick() {{
        const d = new Date(), l = Lunar.fromDate(d);
        update('year', d.getFullYear());
        update('month', d.getMonth()+1, 2);
        update('day', d.getDate(), 2);
        update('lunar', l.getMonthInChinese()+'月'+l.getDayInChinese()+'·'+(l.getJieQi()||l.getPrevJieQi().getName()));
        update('time', d.getHours().toString().padStart(2,'0')+d.getMinutes().toString().padStart(2,'0')+d.getSeconds().toString().padStart(2,'0'));
        const city = cities[cityIdx];
        update('w-city', city); update('w-desc', weatherData[city].desc); update('w-temp', weatherData[city].temp);
    }}

    document.getElementById('btn-font').onclick = () => {{
        document.body.classList.remove('font-'+fontIdx);
        fontIdx = (fontIdx + 1) % 3;
        document.body.classList.add('font-'+fontIdx);
    }};
    document.getElementById('btn-style').onclick = () => {{
        document.body.classList.remove('style-'+styleIdx);
        styleIdx = (styleIdx + 1) % 2;
        document.body.classList.add('style-'+styleIdx);
    }};
    document.getElementById('weather-go').onclick = () => {{
        cityIdx = (cityIdx + 1) % cities.length;
        tick();
    }};

    setInterval(tick, 1000); tick();
</script>
</body>
</html>
"""
components.html(html_code, height=900)
