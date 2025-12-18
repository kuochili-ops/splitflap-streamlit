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
def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Taipei&appid={OWM_API_KEY}&units=metric&lang=zh_tw"
    try:
        r = requests.get(url, timeout=3).json()
        desc = r['weather'][0]['description']
        return {"city": "台北", "desc": desc[:2], "temp": f"{round(r['main']['temp'])}°"}
    except: return {"city": "台北", "desc": "多雲", "temp": "21°"}

weather_info = get_weather()

# --- 3. 核心 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    :root {{
        --flip-speed: 0.6s;
        /* 清水模牆面圖片 */
        --concrete-bg: url('https://images.unsplash.com/photo-1590333746437-12826767598c?q=80&w=2071&auto=format&fit=crop');
    }}

    body {{ 
        margin: 0; padding: 60px 0 0 0;
        display: flex; flex-direction: column; align-items: center; 
        min-height: 100vh; overflow: hidden; gap: 18px;
        background: var(--concrete-bg) no-repeat center center fixed;
        background-size: cover;
    }}

    /* 翻板容器與投影陰影 */
    .row {{ display: flex; gap: 10px; align-items: center; }}
    
    .flap-unit {{ 
        position: relative; width: 48px; height: 72px; 
        background: rgba(0,0,0,0.4); border-radius: 6px;
        font-family: "PingFang TC", "Microsoft JhengHei", sans-serif;
        font-size: 50px; font-weight: 900; color: #fff;
        /* 在牆面形成斜向陰影 */
        box-shadow: 25px 25px 50px rgba(0,0,0,0.5), 5px 5px 15px rgba(0,0,0,0.3);
    }}

    .half {{ 
        position: absolute; width: 100%; height: 50%; overflow: hidden; 
        background: rgba(35, 35, 35, 0.6); /* 半透明板面 */
        backdrop-filter: blur(5px); /* 磨砂質感 */
        display: flex; justify-content: center;
        -webkit-backface-visibility: hidden; backface-visibility: hidden;
    }}

    .top {{ top: 0; align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.7); }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 6px 6px; }}
    .text {{ height: 72px; line-height: 72px; text-align: center; width: 100%; }}

    /* 翻轉葉片邏輯優化 */
    .leaf {{ position: absolute; top: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }}
    .leaf-front {{ background: rgba(35, 35, 35, 0.65); z-index: 12; border-radius: 6px 6px 0 0; }}
    .leaf-back {{ background: rgba(25, 25, 25, 0.8); transform: rotateX(-180deg); z-index: 11; border-radius: 0 0 6px 6px; display: flex; align-items: flex-end; justify-content: center; }}
    .flipping {{ transform: rotateX(-180deg); }}

    /* 小尺寸 row */
    .small .flap-unit {{ width: 36px; height: 54px; font-size: 30px; }}
    .small .text {{ height: 54px; line-height: 54px; }}

    .separator {{ color: rgba(255,255,255,0.4); font-size: 32px; font-weight: 900; }}
</style>
</head>
<body>
    <div class="row" id="year"></div>
    <div class="row">
        <div id="month" class="row"></div>
        <div class="separator">/</div>
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
    const wData = {json.dumps(weather_info)};

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
                    leaf.offsetHeight; // force reflow
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
        update('w-city', wData.city); update('w-desc', wData.desc); update('w-temp', wData.temp);
        
        const hms = d.getHours().toString().padStart(2,'0') + 
                    d.getMinutes().toString().padStart(2,'0') + 
                    d.getSeconds().toString().padStart(2,'0');
        update('time', hms);
    }}

    setInterval(tick, 1000); tick();
</script>
</body>
</html>
"""
components.html(html_code, height=900)
