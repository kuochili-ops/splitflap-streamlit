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

# --- 3. 核心 HTML (解決背景與按鈕問題) ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    /* 穩定版背景：使用重複紋理生成清水模感，不依賴風景圖連結 */
    body {{
        margin: 0; padding-top: 40px;
        display: flex; flex-direction: column; align-items: center;
        min-height: 100vh; overflow: hidden; gap: 15px;
        background-color: #8e8e8e;
        background-image: 
            linear-gradient(rgba(255,255,255,.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.05) 1px, transparent 1px),
            url('https://www.transparenttextures.com/patterns/concrete-wall.png');
        background-attachment: fixed;
        transition: 0.3s;
    }}

    /* 字體樣式定義 */
    .f-tc {{ font-family: "PingFang TC", "Microsoft JhengHei", sans-serif; }}
    .f-serif {{ font-family: "Noto Serif TC", serif; }}
    .f-mono {{ font-family: "Courier New", monospace; }}

    /* 物理投影與翻板 */
    .row {{ 
        display: flex; gap: 8px; align-items: center; 
        filter: drop-shadow(12px 12px 20px rgba(0,0,0,0.5)); 
    }}
    .flap-unit {{ 
        position: relative; width: 44px; height: 68px; background: #000; border-radius: 4px;
        color: #fff; font-size: 46px; font-weight: 900;
    }}
    .half {{ 
        position: absolute; width: 100%; height: 50%; overflow: hidden; 
        background: rgba(30, 30, 30, 0.7); backdrop-filter: blur(5px);
        display: flex; justify-content: center; backface-visibility: hidden;
    }}
    .top {{ top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 1px solid rgba(0,0,0,0.4); }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; }}
    .text {{ height: 68px; line-height: 68px; }}

    /* 控制面板 */
    .controls {{ position: fixed; left: 20px; bottom: 20px; display: flex; gap: 10px; z-index: 100; }}
    .btn {{
        width: 44px; height: 44px; border-radius: 50%; background: rgba(0,0,0,0.5);
        border: 2px solid #fff; color: #fff; display: flex; align-items: center; justify-content: center;
        cursor: pointer; font-weight: bold;
    }}

    /* Spotify 嵌入區域 */
    .spotify-box {{
        margin-top: 20px; width: 300px; height: 80px;
        filter: drop-shadow(5px 5px 15px rgba(0,0,0,0.3));
    }}
</style>
</head>
<body id="main-body" class="f-tc">
    <div class="controls">
        <div onclick="changeFont()" class="btn">A</div>
        <div onclick="toggleBg()" class="btn">S</div>
    </div>

    <div class="row" id="year"></div>
    <div class="row"><div id="month" class="row"></div><div style="color:white;opacity:0.3;font-size:30px">/</div><div id="day" class="row"></div></div>
    <div class="row small" id="lunar" style="transform:scale(0.8)"></div>
    <div class="row small" style="transform:scale(0.9)">
        <div id="w-city">台北</div><div id="w-desc" style="margin:0 10px">{w['desc']}</div><div id="w-temp">{w['temp']}</div>
    </div>
    <div class="row" id="time"></div>

    <div class="spotify-box">
        <iframe src="https://open.spotify.com/embed/playlist/37i9dQZF1DX4sWSp46o6C1?utm_source=generator&theme=0" width="100%" height="80" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
    </div>

<script src="https://cdn.jsdelivr.net/npm/lunar-javascript/lunar.js"></script>
<script>
    let fontState = 0;
    const fonts = ["f-tc", "f-serif", "f-mono"];

    function changeFont() {{
        const body = document.getElementById("main-body");
        body.classList.remove(fonts[fontState]);
        fontState = (fontState + 1) % fonts.length;
        body.classList.add(fonts[fontState]);
    }}

    function toggleBg() {{
        const body = document.getElementById("main-body");
        if(body.style.backgroundColor === "rgb(17, 17, 17)") {{
            body.style.backgroundColor = "#8e8e8e";
            body.style.backgroundImage = "url('https://www.transparenttextures.com/patterns/concrete-wall.png')";
        }} else {{
            body.style.backgroundColor = "#111";
            body.style.backgroundImage = "none";
        }}
    }}

    function update(id, val, pad=0) {{
        let s = val.toString(); if(pad) s = s.padStart(pad,'0');
        const box = document.getElementById(id);
        if(box.innerHTML.length < 10) {{
            box.innerHTML = [...s].map(c => `<div class="flap-unit"><div class="half top"><div class="text">${{c}}</div></div><div class="half bottom"><div class="text">${{c}}</div></div></div>`).join('');
        }}
        [...s].forEach((n, i) => {{
            const units = box.getElementsByClassName('text');
            units[i*2].innerText = n; units[i*2+1].innerText = n;
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
