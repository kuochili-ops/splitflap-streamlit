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

# --- 2. 天氣數據 ---
OWM_API_KEY = "Dcd113bba5675965ccf9e60a7e6d06e5"
def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Taipei&appid={OWM_API_KEY}&units=metric&lang=zh_tw"
    try:
        r = requests.get(url, timeout=3).json()
        desc = r['weather'][0]['description']
        return {"city": "台北", "desc": desc[:2], "temp": f"{round(r['main']['temp'])}°"}
    except: return {"city": "台北", "desc": "多雲", "temp": "21°"}

w = get_weather()

# --- 3. 核心 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    :root {{ --flip-speed: 0.6s; }}
    
    /* Style 0: 純黑模式 */
    body.style-0 {{
        background-color: #151515;
        --card-bg: linear-gradient(180deg, #333 0%, #111 50%, #000 51%, #222 100%);
        --text-shadow: none;
        --box-shadow: 0 10px 20px rgba(0,0,0,0.8);
    }}
    
    /* Style 1: 清水模模式 (Concrete Wall) */
    body.style-1 {{
        background: url('https://images.unsplash.com/photo-1516550893923-42d28e5677af?q=80&w=2072&auto=format&fit=crop') no-repeat center center fixed;
        background-size: cover;
        --card-bg: rgba(25, 25, 25, 0.55); /* 半透明板 */
        --text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
        /* 牆面投射陰影：向右下偏移 */
        --box-shadow: 20px 20px 40px rgba(0,0,0,0.6), 5px 5px 15px rgba(0,0,0,0.4);
    }}

    body {{ 
        display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
        height: 100vh; margin: 0; padding-top: 50px; gap: 18px; 
        transition: background 0.5s ease; overflow: hidden;
    }}
    
    .row {{ display: flex; gap: 8px; align-items: center; }}
    .flap-unit {{ 
        position: relative; width: 46px; height: 70px; background: #000; border-radius: 4px;
        font-family: "PingFang TC", sans-serif; font-size: 48px; font-weight: 900; color: #fff;
        box-shadow: var(--box-shadow); transition: all 0.5s ease;
    }}
    .half {{ 
        position: absolute; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center;
        backdrop-filter: blur(3px); /* 磨砂玻璃效果 */
    }}
    .top {{ top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.6); }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; }}
    .text {{ height: 70px; line-height: 70px; text-shadow: var(--text-shadow); }}
    
    .leaf {{ position: absolute; top: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform var(--flip-speed); transform-style: preserve-3d; }}
    .flipping {{ transform: rotateX(-180deg); }}
    
    .small .flap-unit {{ width: 34px; height: 52px; font-size: 28px; }}
    .small .text {{ height: 52px; line-height: 52px; }}

    #btn-bg {{
        position: fixed; right: 25px; bottom: 25px; width: 45px; height: 45px;
        border-radius: 50%; background: rgba(255,255,255,0.1); border: 1px solid #444;
        color: white; cursor: pointer; display: flex; align-items: center; justify-content: center;
    }}
</style>
</head>
<body class="style-1">
    <div id="btn-bg">S</div>

    <div class="row" id="year"></div>
    <div class="row">
        <div id="month" class="row"></div>
        <div style="color:rgba(255,255,255,0.4);font-size:32px;font-weight:900">/</div>
        <div id="day" class="row"></div>
    </div>
    <div class="row small" id="lunar"></div>
    <div class="row small">
        <div id="w-city" class="row"></div>
        <div id="w-desc" class="row"></div>
        <div id="w-temp" class="row"></div>
    </div>
    <div class="row" id="time"></div>

<script src="https://cdn.jsdelivr.net/npm/lunar-javascript/lunar.js"></script>
<script>
    let bgIdx = 1;
    const wData = {json.dumps(w)};

    function create(v) {{
        return `<div class="flap-unit">
            <div class="half top"><div class="text">${{v}}</div></div>
            <div class="half bottom"><div class="text">${{v}}</div></div>
            <div class="leaf"><div class="half top"><div class="text">${{v}}</div></div><div class="half bottom" style="transform:rotateX(-180deg)"><div class="text">${{v}}</div></div></div>
        </div>`;
    }}

    function update(id, val, pad=0) {{
        let s = val.toString(); if(pad) s = s.padStart(pad,'0');
        const el = document.getElementById(id);
        if(el.children.length !== s.length) el.innerHTML = s.split('').map(c=>create(c)).join('');
        [...s].forEach((n,i)=>{{
            const u = el.children[i], curr = u.querySelector('.top .text').innerText;
            if(n!==curr) {{
                u.querySelector('.leaf .bottom .text').innerText = n;
                u.querySelector('.leaf').classList.add('flipping');
                setTimeout(()=>{{ u.querySelector('.top .text').innerText=n; u.querySelector('.bottom .text').innerText=n; }}, 300);
                u.querySelector('.leaf').addEventListener('transitionend', function() {{
                    this.querySelector('.top .text').innerText = n;
                    this.classList.remove('flipping');
                }}, {{once:true}});
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
        update('w-city', wData.city); update('w-desc', wData.desc); update('w-temp', wData.temp);
    }}

    document.getElementById('btn-bg').onclick = () => {{
        document.body.classList.remove('style-'+bgIdx);
        bgIdx = (bgIdx + 1) % 2;
        document.body.classList.add('style-'+bgIdx);
    }};

    setInterval(tick, 1000); tick();
</script>
</body>
</html>
"""
components.html(html_code, height=900)
