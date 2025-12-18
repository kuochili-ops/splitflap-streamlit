import streamlit as st
import streamlit.components.v1 as components
import requests
import json

# --- 1. 頁面設定 ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: #111 !important;}
    iframe {border: none; width: 100%; height: 100vh; overflow: hidden; margin-top: -50px;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 天氣數據 (多縣市輪播準備) ---
OWM_API_KEY = "Dcd113bba5675965ccf9e60a7e6d06e5"
CITY_LIST = {
    "台北": {"lat": 25.03, "lon": 121.56},
    "台中": {"lat": 24.14, "lon": 120.67},
    "高雄": {"lat": 22.61, "lon": 120.30},
    "台南": {"lat": 22.99, "lon": 120.21},
    "花蓮": {"lat": 23.97, "lon": 121.60}
}

def get_all_weather():
    results = {}
    for city, pos in CITY_LIST.items():
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={pos['lat']}&lon={pos['lon']}&appid={OWM_API_KEY}&units=metric&lang=zh_tw"
        try:
            res = requests.get(url, timeout=2).json()
            desc = res['weather'][0]['description']
            short_desc = "晴天" if "晴" in desc else "多雲" if "雲" in desc else "雨天" if "雨" in desc else desc[:2]
            results[city] = {"desc": short_desc, "temp": f"{round(res['main']['temp'])}°"}
        except: continue
    return results

weather_data_json = json.dumps(get_all_weather() or {"台北": {"desc": "多雲", "temp": "21°"}})

# --- 3. 核心 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    :root {{
        --flip-speed: 0.6s;
    }}
    
    /* Style 0: 純黑模式 */
    body.style-0 {{
        background: #151515;
        --card-bg: linear-gradient(180deg, #333 0%, #111 50%, #000 51%, #222 100%);
        --box-shadow: 0 10px 20px rgba(0,0,0,0.8);
        --blur: 0px;
    }}
    
    /* Style 1: 清水模模式 */
    body.style-1 {{
        background: url('https://images.unsplash.com/photo-1590333746437-12826767598c?q=80&w=2071&auto=format&fit=crop') no-repeat center center fixed;
        background-size: cover;
        --card-bg: rgba(30, 30, 30, 0.6);
        --box-shadow: 22px 22px 45px rgba(0,0,0,0.6), 5px 5px 15px rgba(0,0,0,0.3);
        --blur: 6px;
    }}

    /* 字體切換 */
    body.font-0 {{ --font-family: "PingFang TC", "Microsoft JhengHei", sans-serif; }}
    body.font-1 {{ --font-family: serif; }}
    body.font-2 {{ --font-family: cursive; }}

    body {{ 
        display: flex; flex-direction: column; align-items: center; height: 100vh; margin: 0; padding-top: 50px; gap: 18px; 
        transition: background 0.5s ease; overflow: hidden;
    }}

    .row {{ display: flex; gap: 8px; align-items: center; justify-content: center; }}
    
    .flap-unit {{ 
        position: relative; width: 46px; height: 70px; background: rgba(0,0,0,0.5); border-radius: 5px;
        font-family: var(--font-family); font-size: 48px; font-weight: 900; color: #fff;
        box-shadow: var(--box-shadow); transition: box-shadow 0.5s ease;
    }}
    
    .half {{ 
        position: absolute; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); backdrop-filter: blur(var(--blur));
        display: flex; justify-content: center; backface-visibility: hidden;
    }}
    
    .top {{ top: 0; align-items: flex-start; border-radius: 5px 5px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.5); }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 5px 5px; }}
    .text {{ height: 70px; line-height: 70px; }}

    .leaf {{ position: absolute; top: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }}
    .leaf-front {{ background: var(--card-bg); z-index: 12; border-radius: 5px 5px 0 0; }}
    .leaf-back {{ background: rgba(20,20,20,0.8); transform: rotateX(-180deg); z-index: 11; border-radius: 0 0 5px 5px; display: flex; align-items: flex-end; justify-content: center; }}
    .flipping {{ transform: rotateX(-180deg); }}

    .small .flap-unit {{ width: 34px; height: 52px; font-size: 28px; }}
    .small .text {{ height: 52px; line-height: 52px; }}

    /* 控制按鈕 */
    .btn {{
        position: fixed; width: 42px; height: 42px; border-radius: 50%; background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2); color: white; display: flex; align-items: center; justify-content: center;
        cursor: pointer; z-index: 100; font-family: sans-serif; transition: 0.3s;
    }}
    .btn:hover {{ background: rgba(255,255,255,0.2); }}
    #btn-font {{ left: 20px; bottom: 20px; }}
    #btn-style {{ left: 75px; bottom: 20px; }}
    .weather-trigger {{ cursor: pointer; padding: 5px; border-radius: 10px; transition: 0.3s; }}
    .weather-trigger:hover {{ background: rgba(255,255,255,0.05); }}
</style>
</head>
<body class="style-1 font-0">
    <div id="btn-font" class="btn">A</div>
    <div id="btn-style" class="btn">S</div>

    <div class="row" id="year"></div>
    <div class="row">
        <div id="month" class="row"></div>
        <div style="color:rgba(255,255,255,0.3); font-size:30px; font-weight:900">/</div>
        <div id="day" class="row"></div>
    </div>
    <div class="row small" id="lunar"></div>
    <div class="row small weather-trigger" id="weather-go">
        <div id="w-city" class="row"></div>
        <div id="w-desc" class="row" style="margin:0 6px"></div>
        <div id="w-temp" class="row"></div>
    </div>
    <div class="row" id="time"></div>

<script src="https://cdn.jsdelivr.net/npm/lunar-javascript/lunar.js"></script>
<script>
    const weatherData = {weather_data_json};
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

    function refreshWeather() {{
        const name = cities[cityIdx];
        const data = weatherData[name];
        update('w-city', name);
        update('w-desc', data.desc);
        update('w-temp', data.temp);
    }}

    function tick() {{
        const d = new Date(), l = Lunar.fromDate(d);
        update('year', d.getFullYear());
        update('month', d.getMonth()+1, 2);
        update('day', d.getDate(), 2);
        update('lunar', l.getMonthInChinese()+'月'+l.getDayInChinese()+'·'+(l.getJieQi()||l.getPrevJieQi().getName()));
        update('time', d.getHours().toString().padStart(2,'0')+d.getMinutes().toString().padStart(2,'0')+d.getSeconds().toString().padStart(2,'0'));
        refreshWeather();
    }}

    // 按鈕邏輯
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
        refreshWeather();
    }};

    setInterval(tick, 1000); tick();
</script>
</body>
</html>
"""
components.html(html_code, height=900)
