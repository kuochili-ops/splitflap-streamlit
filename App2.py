import streamlit as st
import streamlit.components.v1 as components
import requests
import json

# --- 1. 頁面設定 ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: #333 !important;}
    iframe {border: none; width: 100%; height: 100vh; overflow: hidden; margin-top: -50px;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 縣市天氣數據 ---
OWM_API_KEY = "Dcd113bba5675965ccf9e60a7e6d06e5"
CITIES = {"台北": "Taipei", "台中": "Taichung", "高雄": "Kaohsiung", "宜蘭": "Yilan", "台南": "Tainan"}

def get_weather_data():
    results = {}
    for name, q in CITIES.items():
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={q}&appid={OWM_API_KEY}&units=metric&lang=zh_tw"
            r = requests.get(url, timeout=2).json()
            results[name] = {"desc": r['weather'][0]['description'][:2], "temp": f"{round(r['main']['temp'])}°"}
        except: continue
    return results

weather_json = json.dumps(get_weather_data() or {"台北": {"desc": "多雲", "temp": "21°"}})

# --- 3. 核心 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {{
        --concrete-img: url('https://images.unsplash.com/photo-1516550893923-42d28e5677af?q=80&w=2072&auto=format&fit=crop');
        --flip-speed: 0.6s;
    }}

    /* 清水模風格主體 */
    body.style-concrete {{
        background: var(--concrete-img) no-repeat center center fixed;
        background-size: cover;
        --card-bg: rgba(30, 30, 30, 0.65);
        --shadow: drop-shadow(15px 15px 25px rgba(0,0,0,0.6));
        --blur: blur(5px);
    }}
    
    body.style-black {{
        background: #111;
        --card-bg: #222;
        --shadow: drop-shadow(0 8px 15px rgba(0,0,0,0.8));
        --blur: blur(0px);
    }}

    body.font-0 {{ --font-family: "PingFang TC", sans-serif; }}
    body.font-1 {{ --font-family: serif; }}
    body.font-2 {{ --font-family: cursive; }}

    body {{ 
        display: flex; flex-direction: column; align-items: center; min-height: 100vh;
        margin: 0; padding-top: 50px; gap: 15px; transition: 0.5s; overflow: hidden;
    }}

    .row {{ display: flex; gap: 6px; align-items: center; filter: var(--shadow); }}
    
    .flap-unit {{ 
        position: relative; width: 44px; height: 66px; background: #000; border-radius: 4px;
        font-family: var(--font-family); font-size: 46px; font-weight: 900; color: #fff;
    }}
    
    .half {{ 
        position: absolute; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); backdrop-filter: var(--blur);
        display: flex; justify-content: center; backface-visibility: hidden;
    }}
    
    .top {{ top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.6); }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; }}
    .text {{ height: 66px; line-height: 66px; }}

    .leaf {{ position: absolute; top: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }}
    .leaf-front {{ background: var(--card-bg); z-index: 12; border-radius: 4px 4px 0 0; }}
    .leaf-back {{ background: rgba(10,10,10,0.9); transform: rotateX(-180deg); z-index: 11; border-radius: 0 0 4px 4px; display: flex; align-items: flex-end; justify-content: center; }}
    .flipping {{ transform: rotateX(-180deg); }}

    .small .flap-unit {{ width: 34px; height: 50px; font-size: 28px; }}
    .small .text {{ height: 50px; line-height: 50px; }}

    /* 控制面板 */
    .panel {{ position: fixed; left: 20px; bottom: 20px; display: flex; gap: 10px; }}
    .btn {{
        width: 44px; height: 44px; border-radius: 50%; background: rgba(0,0,0,0.4);
        border: 2px solid #fff; color: #fff; display: flex; align-items: center; justify-content: center;
        cursor: pointer; font-weight: bold; font-family: sans-serif;
    }}
    .weather-box {{ cursor: pointer; padding: 4px 8px; border-radius: 8px; }}
</style>
</head>
<body class="style-concrete font-0">
    <div class="panel">
        <div id="btn-f" class="btn">A</div>
        <div id="btn-s" class="btn">S</div>
    </div>

    <div class="row" id="year"></div>
    <div class="row">
        <div id="month" class="row"></div>
        <div style="color:white; opacity:0.3; font-size:28px">/</div>
        <div id="day" class="row"></div>
    </div>
    <div class="row small" id="lunar"></div>
    <div class="row small weather-box" id="weather-btn">
        <div id="w-city" class="row"></div>
        <div id="w-desc" class="row" style="margin: 0 5px"></div>
        <div id="w-temp" class="row"></div>
    </div>
    <div class="row" id="time"></div>

<script src="https://cdn.jsdelivr.net/npm/lunar-javascript/lunar.js"></script>
<script>
    const wData = {weather_json};
    const cities = Object.keys(wData);
    let cIdx = 0, fIdx = 0, sMode = "concrete";

    function create(v) {{
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
        const box = document.getElementById(id);
        if(box.children.length !== s.length) box.innerHTML = [...s].map(c=>create(c)).join('');
        [...s].forEach((n, i) => {{
            const unit = box.children[i];
            const old = unit.querySelector('.base-top .text').innerText;
            if(n !== old) {{
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
        const c = cities[cIdx];
        update('w-city', c); update('w-desc', wData[c].desc); update('w-temp', wData[c].temp);
    }}

    document.getElementById('btn-f').onclick = () => {{
        document.body.classList.remove('font-'+fIdx);
        fIdx = (fIdx + 1) % 3;
        document.body.classList.add('font-'+fIdx);
    }};
    document.getElementById('btn-s').onclick = () => {{
        document.body.classList.remove('style-'+sMode);
        sMode = (sMode === "concrete") ? "black" : "concrete";
        document.body.classList.add('style-'+sMode);
    }};
    document.getElementById('weather-btn').onclick = () => {{
        cIdx = (cIdx + 1) % cities.length;
        tick();
    }};

    setInterval(tick, 1000); tick();
</script>
</body>
</html>
"""
components.html(html_code, height=900)
