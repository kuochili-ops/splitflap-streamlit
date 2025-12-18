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
    .stApp {background-color: #111 !important;}
    iframe {border: none; width: 100%; height: 100vh; overflow: hidden; margin-top: -50px;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 天氣數據 (OpenWeather) ---
OWM_API_KEY = "Dcd113bba5675965ccf9e60a7e6d06e5"
CITY_LIST = {"台北": {"lat": 25.03, "lon": 121.56}, "台中": {"lat": 24.14, "lon": 120.67}, "高雄": {"lat": 22.61, "lon": 120.30}}

def get_real_weather():
    results = {}
    for city, pos in CITY_LIST.items():
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={pos['lat']}&lon={pos['lon']}&appid={OWM_API_KEY}&units=metric&lang=zh_tw"
        try:
            res = requests.get(url, timeout=3).json()
            desc = res['weather'][0]['description']
            short_desc = "晴天" if "晴" in desc else "多雲" if "雲" in desc else "雨天" if "雨" in desc else desc[:2]
            results[city] = {"desc": short_desc, "temp": f"{round(res['main']['temp'])}°"}
        except: continue
    return results

weather_json = json.dumps(get_real_weather() or {"台北": {"desc": "多雲", "temp": "21°"}})

# --- 3. 核心 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    :root {{
        --font-family: "PingFang TC", sans-serif;
        --flip-speed: 0.6s;
    }}
    /* Style 0: 純黑沉浸 */
    body.style-0 {{
        background-color: #1a1a1a;
        --card-bg: linear-gradient(180deg, #333 0%, #111 50%, #000 51%, #222 100%);
        --text-color: #fff;
        --unit-shadow: 0 10px 20px rgba(0,0,0,0.8);
        --split-line: #000;
    }}
    /* Style 1: 清水模工業風 */
    body.style-1 {{
        background: url('https://images.unsplash.com/photo-1544161513-0179fe746fd5?q=80&w=2070&auto=format&fit=crop') no-repeat center center fixed;
        background-size: cover;
        --card-bg: rgba(20, 20, 20, 0.65); /* 半透明 */
        --text-color: #f0f0f0;
        --unit-shadow: 15px 15px 35px rgba(0,0,0,0.6), -5px -5px 15px rgba(255,255,255,0.05); /* 強陰影 */
        --split-line: rgba(255,255,255,0.1);
    }}

    body.font-style-0 {{ --font-family: "PingFang TC", "Microsoft JhengHei", sans-serif; }}
    body.font-style-1 {{ --font-family: serif; }}
    body.font-style-2 {{ --font-family: cursive; }}

    body {{ 
        display: flex; flex-direction: column; align-items: center; height: 100vh; margin: 0; padding-top: 60px; gap: 15px;
        transition: 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .row {{ display: flex; gap: 8px; justify-content: center; }}
    .flap-unit {{ 
        position: relative; width: 45px; height: 68px; background: #000; border-radius: 6px; 
        font-family: var(--font-family); font-size: 46px; font-weight: 900; color: var(--text-color); 
        box-shadow: var(--unit-shadow);
    }}
    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center; backface-visibility: hidden;
        backdrop-filter: blur(4px); /* 半透明磨砂感 */
    }}
    .top {{ top: 0; align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.5); }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 6px 6px; }}
    .text {{ height: 68px; line-height: 68px; }}
    .leaf {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform var(--flip-speed); transform-style: preserve-3d; }}
    .flipping {{ transform: rotateX(-180deg); }}
    .flap-unit::before {{ content: ""; position: absolute; top: 50%; width: 100%; height: 1.5px; background: var(--split-line); z-index: 20; transform: translateY(-50%); }}

    .small .flap-unit {{ width: 34px; height: 50px; font-size: 28px; }}
    .small .text {{ height: 50px; line-height: 50px; }}

    /* 控制按鈕 */
    .btn {{
        position: fixed; width: 44px; height: 44px; border-radius: 50%; background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2); color: #fff; display: flex; align-items: center; justify-content: center;
        cursor: pointer; z-index: 100; font-family: sans-serif;
    }}
    #btn-font {{ left: 20px; bottom: 20px; }}
    #btn-bg {{ right: 20px; bottom: 20px; }}
</style>
</head>
<body class="style-0 font-style-0">
    <div id="btn-font" class="btn">A</div>
    <div id="btn-bg" class="btn">S</div>

    <div class="row"><div id="year" class="row"></div></div>
    <div class="row"><div id="month" class="row"></div><div style="color:rgba(255,255,255,0.5);font-size:30px">/</div><div id="day" class="row"></div></div>
    <div class="row small"><div id="lunar" class="row"></div></div>
    <div class="row small"><div id="weather-city" class="row"></div><div id="weather-desc" class="row"></div><div id="weather-temp" class="row"></div></div>
    <div class="row"><div id="hours" class="row"></div><div id="minutes" class="row"></div><div id="seconds" class="row"></div></div>

<script src="https://cdn.jsdelivr.net/npm/lunar-javascript/lunar.js"></script>
<script>
    const weatherData = {weather_json};
    let fontIdx = 0, bgIdx = 0;

    function createFlap(v) {{
        return `<div class="flap-unit">
            <div class="half top"><div class="text">${{v}}</div></div>
            <div class="half bottom"><div class="text">${{v}}</div></div>
            <div class="leaf"><div class="half top"><div class="text">${{v}}</div></div><div class="half bottom" style="transform:rotateX(-180deg)"><div class="text">${{v}}</div></div></div>
        </div>`;
    }}

    function update(id, val, pad=0) {{
        let s = val.toString(); if(pad) s = s.padStart(pad,'0');
        const el = document.getElementById(id);
        if(el.children.length !== s.length) el.innerHTML = s.split('').map(c=>createFlap(c)).join('');
        s.split('').forEach((n,i)=>{{
            const u = el.children[i];
            const curr = u.querySelector('.top .text').innerText;
            if(n!==curr) {{
                u.querySelector('.leaf .bottom .text').innerText = n;
                u.querySelector('.leaf').classList.add('flipping');
                setTimeout(()=>{{ u.querySelector('.top .text').innerText = n; u.querySelector('.bottom .text').innerText = n; }}, 300);
                u.querySelector('.leaf').addEventListener('transitionend', function() {{
                    this.querySelector('.top .text').innerText = n;
                    this.classList.remove('flipping');
                }}, {{once:true}});
            }}
        }});
    }}

    function tick() {{
        const d = new Date(), l = Lunar.fromDate(d);
        update('year', d.getFullYear()); update('month', d.getMonth()+1, 2); update('day', d.getDate(), 2);
        update('lunar', l.getMonthInChinese()+'月'+l.getDayInChinese()+'·'+(l.getJieQi()||l.getPrevJieQi().getName()));
        update('hours', d.getHours(), 2); update('minutes', d.getMinutes(), 2); update('seconds', d.getSeconds(), 2);
        const city = Object.keys(weatherData)[0];
        update('weather-city', city); update('weather-desc', weatherData[city].desc); update('weather-temp', weatherData[city].temp);
    }}

    setInterval(tick, 1000); tick();

    document.getElementById('btn-font').onclick = () => {{
        document.body.classList.remove('font-style-'+fontIdx);
        fontIdx = (fontIdx + 1) % 3;
        document.body.classList.add('font-style-'+fontIdx);
    }};
    document.getElementById('btn-bg').onclick = () => {{
        document.body.classList.remove('style-'+bgIdx);
        bgIdx = (bgIdx + 1) % 2;
        document.body.classList.add('style-'+bgIdx);
    }};
</script>
</body>
</html>
"""
components.html(html_code, height=900)
