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

# --- 2. 天氣數據 ---
OWM_API_KEY = "Dcd113bba5675965ccf9e60a7e6d06e5"
def get_weather():
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q=Taipei&appid={OWM_API_KEY}&units=metric&lang=zh_tw"
        r = requests.get(url, timeout=2).json()
        return {"city": "台北", "desc": r['weather'][0]['description'][:2], "temp": f"{round(r['main']['temp'])}°"}
    except: return {"city": "台北", "desc": "多雲", "temp": "21°"}

w = get_weather()

# --- 3. 核心 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {{
        --flip-speed: 0.6s;
    }}

    body {{
        margin: 0; padding-top: 50px;
        display: flex; flex-direction: column; align-items: center;
        min-height: 100vh; overflow: hidden; gap: 15px;
        /* 鎖定您目前成功的清水模背景 */
        background: url('https://images.unsplash.com/photo-1516550893923-42d28e5677af?q=80&w=2072&auto=format&fit=crop') no-repeat center center fixed;
        background-size: cover;
        transition: 0.3s;
    }}

    /* 定義三種字體族群 */
    .f-style-0 {{ font-family: "PingFang TC", "Heiti TC", sans-serif; }}
    .f-style-1 {{ font-family: "Noto Serif TC", "PMingLiU", serif; }}
    .f-style-2 {{ font-family: "Courier New", monospace; }}

    .row {{ 
        display: flex; gap: 8px; align-items: center; 
        filter: drop-shadow(15px 15px 25px rgba(0,0,0,0.6)); 
    }}

    .flap-unit {{ 
        position: relative; width: 46px; height: 70px; background: #000; border-radius: 4px;
        color: #fff; font-size: 48px; font-weight: 900;
    }}

    .half {{ 
        position: absolute; width: 100%; height: 50%; overflow: hidden; 
        background: rgba(30, 30, 30, 0.65); backdrop-filter: blur(5px);
        display: flex; justify-content: center; backface-visibility: hidden;
    }}

    .top {{ top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.5); }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; }}
    .text {{ height: 70px; line-height: 70px; }}

    /* 控制面板 */
    .controls {{ position: fixed; left: 25px; bottom: 25px; display: flex; gap: 15px; z-index: 9999; }}
    .btn {{
        width: 50px; height: 50px; border-radius: 50%; background: rgba(0,0,0,0.5);
        border: 2px solid #fff; color: #fff; display: flex; align-items: center; justify-content: center;
        cursor: pointer; font-weight: bold; font-family: sans-serif; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }}
    .btn:active {{ transform: scale(0.9); }}
</style>
</head>
<body id="master-body" class="f-style-0">
    <div class="controls">
        <div id="btn-font" class="btn">A</div>
        <div id="btn-style" class="btn">S</div>
    </div>

    <div class="row" id="year"></div>
    <div class="row"><div id="month" class="row"></div><div style="color:white;opacity:0.3;font-size:30px">/</div><div id="day" class="row"></div></div>
    <div class="row small" id="lunar" style="transform:scale(0.85)"></div>
    <div class="row small" style="transform:scale(0.95)">
        <div id="w-city">台北</div><div id="w-desc" style="margin:0 10px">{w['desc']}</div><div id="w-temp">{w['temp']}</div>
    </div>
    <div class="row" id="time"></div>

<script src="https://cdn.jsdelivr.net/npm/lunar-javascript/lunar.js"></script>
<script>
    let currentFontIdx = 0;

    // 重新編寫更強健的字體切換邏輯
    document.getElementById('btn-font').addEventListener('click', function() {{
        const body = document.getElementById('master-body');
        body.classList.remove('f-style-' + currentFontIdx);
        currentFontIdx = (currentFontIdx + 1) % 3;
        body.classList.add('f-style-' + currentFontIdx);
    }});

    document.getElementById('btn-style').addEventListener('click', function() {{
        const body = document.getElementById('master-body');
        if(body.style.background.includes('photo')) {{
            body.style.background = '#111';
        }} else {{
            body.style.background = "url('https://images.unsplash.com/photo-1516550893923-42d28e5677af?q=80&w=2072&auto=format&fit=crop') no-repeat center center fixed";
            body.style.backgroundSize = "cover";
        }}
    }});

    function update(id, val, pad=0) {{
        let s = val.toString(); if(pad) s = s.padStart(pad,'0');
        const box = document.getElementById(id);
        if(box.innerHTML.length < 10) {{
            box.innerHTML = [...s].map(c => `<div class="flap-unit">
                <div class="half top"><div class="text">${{c}}</div></div>
                <div class="half bottom"><div class="text">${{c}}</div></div>
            </div>`).join('');
        }}
        [...s].forEach((n, i) => {{
            const texts = box.querySelectorAll('.text');
            texts[i*2].innerText = n; texts[i*2+1].innerText = n;
        }});
    }}

    function tick() {{
        const d = new Date(), l = Lunar.fromDate(d);
        update('year', d.getFullYear());
        update('month', d.getMonth()+1, 2);
        update('day', d.getDate(), 2);
        update('lunar', l.getMonthInChinese()+'月'+l.getDayInChinese()+'·'+(l.getJieQi()||l.getPrevJieQi().getName()));
        update('time', d.getHours().toString().padStart(2,'0')+d.getMinutes().toString().padStart(2,'0')+d.getSeconds().toString().padStart(2,'0'));
    }}

    setInterval(tick, 1000); tick();
</script>
</body>
</html>
"""
components.html(html_code, height=900)
