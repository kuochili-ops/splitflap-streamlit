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

# --- 2. 獲取天氣 (穩定版) ---
OWM_API_KEY = "Dcd113bba5675965ccf9e60a7e6d06e5"
CITIES = ["台北", "台中", "高雄", "台南", "花蓮"]
def get_weather_json():
    data = {}
    for c in CITIES:
        data[c] = {"desc": "多雲", "temp": "21°"} # 預設值
    return json.dumps(data)

weather_json = get_weather_json()

# --- 3. 核心 HTML (清水模鎖定版) ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {{
        /* 鎖定清水模背景圖源 */
        --concrete-url: url('https://images.unsplash.com/photo-1516550893923-42d28e5677af?q=80&w=2072&auto=format&fit=crop');
        --flip-speed: 0.6s;
    }}

    body {{ 
        margin: 0; padding-top: 50px;
        display: flex; flex-direction: column; align-items: center; 
        min-height: 100vh; overflow: hidden; gap: 18px;
        /* 背景設定：鎖定水泥牆 */
        background: var(--concrete-url) no-repeat center center fixed;
        background-size: cover;
        background-color: #888; /* 備用灰色 */
        transition: 0.5s;
    }}

    /* 物理投影：讓板塊看起來像掛在牆上 */
    .row {{ 
        display: flex; gap: 8px; align-items: center; 
        filter: drop-shadow(15px 15px 25px rgba(0,0,0,0.6)); 
    }}
    
    .flap-unit {{ 
        position: relative; width: 46px; height: 70px; background: #000; border-radius: 4px;
        font-family: "PingFang TC", sans-serif; font-size: 48px; font-weight: 900; color: #fff;
    }}
    
    .half {{ 
        position: absolute; width: 100%; height: 50%; overflow: hidden; 
        background: rgba(40, 40, 40, 0.6); /* 半透明 */
        backdrop-filter: blur(6px); /* 磨砂玻璃 */
        display: flex; justify-content: center;
        backface-visibility: hidden;
    }}
    
    .top {{ top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.5); }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; }}
    .text {{ height: 70px; line-height: 70px; }}

    .leaf {{ position: absolute; top: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }}
    .leaf-front {{ background: rgba(40, 40, 40, 0.65); z-index: 12; border-radius: 4px 4px 0 0; }}
    .leaf-back {{ background: #111; transform: rotateX(-180deg); z-index: 11; border-radius: 0 0 4px 4px; display: flex; align-items: flex-end; justify-content: center; }}
    .flipping {{ transform: rotateX(-180deg); }}

    .small .flap-unit {{ width: 34px; height: 52px; font-size: 28px; }}
    .small .text {{ height: 52px; line-height: 52px; }}

    /* 控制按鈕：半透明圓形 */
    .controls {{ position: fixed; left: 20px; bottom: 20px; display: flex; gap: 10px; }}
    .btn {{
        width: 44px; height: 44px; border-radius: 50%; background: rgba(0,0,0,0.3);
        border: 1px solid #fff; color: white; display: flex; align-items: center; justify-content: center;
        cursor: pointer; font-size: 14px; font-weight: bold;
    }}
</style>
</head>
<body>
    <div class="controls">
        <div id="btn-f" class="btn">A</div>
        <div id="btn-s" class="btn">S</div>
    </div>

    <div class="row" id="year"></div>
    <div class="row"><div id="month" class="row"></div><div style="color:rgba(255,255,255,0.3); font-size:30px">/</div><div id="day" class="row"></div></div>
    <div class="row small" id="lunar"></div>
    <div class="row small" style="cursor:pointer" id="w-btn">
        <div id="w-city" class="row"></div>
        <div id="w-desc" class="row" style="margin:0 5px"></div>
        <div id="w-temp" class="row"></div>
    </div>
    <div class="row" id="time"></div>

<script src="https://cdn.jsdelivr.net/npm/lunar-javascript/lunar.js"></script>
<script>
    let fontIdx = 0, styleMode = "concrete";

    function update(id, val, pad=0) {{
        let s = val.toString(); if(pad) s = s.padStart(pad,'0');
        const box = document.getElementById(id);
        if(box.children.length !== s.length) {{
            box.innerHTML = [...s].map(c => `<div class="flap-unit">
                <div class="half top base-top"><div class="text">${{c}}</div></div>
                <div class="half bottom base-bottom"><div class="text">${{c}}</div></div>
                <div class="leaf">
                    <div class="half top leaf-front"><div class="text">${{c}}</div></div>
                    <div class="half bottom leaf-back"><div class="text">${{c}}</div></div>
                </div>
            </div>`).join('');
        }}
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
        update('w-city', '台北'); update('w-desc', '多雲'); update('w-temp', '21°');
    }}

    document.getElementById('btn-f').onclick = () => {{
        document.body.classList.remove('font-'+fontIdx);
        fontIdx = (fontIdx + 1) % 3;
        document.body.classList.add('font-'+fontIdx);
    }};
    
    document.getElementById('btn-s').onclick = () => {{
        if(styleMode === "concrete") {{
            document.body.style.background = "#111";
            styleMode = "black";
        }} else {{
            document.body.style.background = "var(--concrete-url) no-repeat center center fixed";
            document.body.style.backgroundSize = "cover";
            styleMode = "concrete";
        }}
    }};

    setInterval(tick, 1000); tick();
</script>
</body>
</html>
"""
components.html(html_code, height=900)
