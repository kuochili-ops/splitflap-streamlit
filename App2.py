import streamlit as st
import streamlit.components.v1 as components

# --- 1. 頁面設定 ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: #333 !important;}
    iframe {border: none; width: 100%; height: 100vh; overflow: hidden; margin-top: -50px;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body {{
        margin: 0; padding-top: 30px;
        display: flex; flex-direction: column; align-items: center;
        min-height: 100vh; overflow: hidden;
        /* 使用與您上傳圖片一致的清水模風格背景 */
        background: url('https://images.unsplash.com/photo-1590274853856-f22d5ee3d228?q=80&w=2070&auto=format&fit=crop') no-repeat center center fixed;
        background-size: cover;
    }}

    /* 透明玻璃板容器：寬度限制在手機範圍內 (max-width: 90vw) */
    .glass-panel {{
        display: flex; flex-direction: column; align-items: center; gap: 12px;
        width: 90vw; max-width: 400px; /* 符合手機寬度限制 */
        padding: 30px 10px;
        background: rgba(255, 255, 255, 0.03); 
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        box-shadow: 
            25px 30px 50px rgba(0, 0, 0, 0.5), 
            inset 1px 1px 2px rgba(255, 255, 255, 0.1);
        transform: perspective(1000px) rotateX(1deg);
    }}

    /* 翻板橫向排列：確保不超出玻璃板，若太長會自動縮小 */
    .row {{ 
        display: flex; gap: 4px; align-items: center; justify-content: center;
        width: 100%; flex-wrap: nowrap;
        /* 翻板對牆面的投射陰影 */
        filter: drop-shadow(20px 25px 25px rgba(0, 0, 0, 0.7));
    }}

    /* 調整翻板大小以適應手機寬度 */
    .flap-unit {{ 
        position: relative; width: 32px; height: 50px; background: #000; border-radius: 3px;
        color: #fff; font-size: 30px; font-weight: 900;
    }}

    .half {{ 
        position: absolute; width: 100%; height: 50%; overflow: hidden; 
        background: linear-gradient(180deg, #222 0%, #000 100%);
        display: flex; justify-content: center;
    }}

    .top {{ top: 0; align-items: flex-start; border-radius: 3px 3px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.8); }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 3px 3px; }}
    .text {{ height: 50px; line-height: 50px; font-family: "Courier New", monospace; }}

    #weather-row {{ cursor: pointer; }}
    .small-text {{ font-size: 18px; color: white; opacity: 0.5; }}
</style>
</head>
<body>

    <div class="glass-panel">
        <div class="row" id="year"></div>
        <div class="row">
            <div id="month" class="row" style="width:auto"></div>
            <div class="small-text">/</div>
            <div id="day" class="row" style="width:auto"></div>
        </div>
        
        <div id="weather-row">
            <div class="row" id="w-city"></div>
            <div class="row" id="w-desc" style="margin: 8px 0;"></div>
            <div class="row" id="w-temp"></div>
        </div>

        <div class="row" id="time" style="margin-top:10px"></div>
        <div id="lunar" class="row" style="transform:scale(0.7); opacity:0.6"></div>
    </div>

<script src="https://cdn.jsdelivr.net/npm/lunar-javascript/lunar.js"></script>
<script>
    let cityIdx = 0;
    const weatherData = [
        {{ city: "TAIPEI", desc: "CLOUDY", temp: "21C" }},
        {{ city: "TAICHUNG", desc: "SUNNY", temp: "25C" }},
        {{ city: "KAOHSIUNG", desc: "CLEAR", temp: "28C" }},
        {{ city: "HUALIEN", desc: "RAINY", temp: "22C" }}
    ];

    function updateFlaps(id, val) {{
        const box = document.getElementById(id);
        const s = val.toString().toUpperCase();
        if (box.innerHTML === "" || box.childElementCount !== s.length) {{
            box.innerHTML = [...s].map(c => `
                <div class="flap-unit">
                    <div class="half top"><div class="text">${{c}}</div></div>
                    <div class="half bottom"><div class="text">${{c}}</div></div>
                </div>`).join('');
        }}
        const texts = box.querySelectorAll('.text');
        [...s].forEach((n, i) => {{
            texts[i*2].innerText = n; texts[i*2+1].innerText = n;
        }});
    }}

    function switchCity() {{
        const data = weatherData[cityIdx];
        updateFlaps('w-city', data.city);
        updateFlaps('w-desc', data.desc);
        updateFlaps('w-temp', data.temp);
        cityIdx = (cityIdx + 1) % weatherData.length;
    }}

    document.getElementById('weather-row').addEventListener('click', switchCity);

    function tick() {{
        const d = new Date(), l = Lunar.fromDate(d);
        updateFlaps('year', d.getFullYear());
        updateFlaps('month', (d.getMonth()+1).toString().padStart(2,'0'));
        updateFlaps('day', d.getDate().toString().padStart(2,'0'));
        updateFlaps('time', d.getHours().toString().padStart(2,'0')+d.getMinutes().toString().padStart(2,'0')+d.getSeconds().toString().padStart(2,'0'));
        updateFlaps('lunar', l.getMonthInChinese()+'月'+l.getDayInChinese());
    }}

    setInterval(tick, 1000); 
    tick();
    switchCity();
</script>
</body>
</html>
"""
components.html(html_code, height=900)
