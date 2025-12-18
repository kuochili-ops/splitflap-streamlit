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

# --- 2. 核心 HTML (透明懸浮玻璃版樣式) ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body {{
        margin: 0; padding-top: 40px;
        display: flex; flex-direction: column; align-items: center;
        min-height: 100vh; overflow: hidden; gap: 20px;
        /* 清水模牆面背景 */
        background: url('https://images.unsplash.com/photo-1516550893923-42d28e5677af?q=80&w=2072&auto=format&fit=crop') no-repeat center center fixed;
        background-size: cover;
        transition: 0.3s;
        user-select: none;
    }}

    /* 透明玻璃背板：所有翻板都在這塊板子上 */
    .glass-panel {{
        display: flex; flex-direction: column; align-items: center; gap: 18px;
        padding: 40px 60px;
        background: rgba(255, 255, 255, 0.05); /* 極淡的白色模擬玻璃面 */
        backdrop-filter: blur(8px); /* 玻璃的磨砂感 */
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        /* 核心細節：這層陰影模擬整塊透明板對牆面的投射 */
        box-shadow: 
            20px 20px 50px rgba(0, 0, 0, 0.4), 
            inset 1px 1px 2px rgba(255, 255, 255, 0.1);
        transform: perspective(1000px) rotateX(2deg); /* 輕微俯視感 */
    }}

    .row {{ 
        display: flex; gap: 8px; align-items: center;
        /* 翻板元件對牆面的光影投射：位移較遠，營造懸浮高度 */
        filter: drop-shadow(25px 25px 30px rgba(0, 0, 0, 0.7));
    }}

    /* 翻板元件樣式 */
    .flap-unit {{ 
        position: relative; width: 44px; height: 68px; background: #000; border-radius: 4px;
        color: #fff; font-size: 44px; font-weight: 900;
    }}

    .half {{ 
        position: absolute; width: 100%; height: 50%; overflow: hidden; 
        background: linear-gradient(180deg, #1a1a1a 0%, #000 100%);
        display: flex; justify-content: center;
    }}

    .top {{ top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 1px solid rgba(0,0,0,0.8); }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; }}
    .text {{ height: 68px; line-height: 68px; font-family: "Courier New", monospace; }}

    /* 天氣列點擊區 */
    #weather-row {{ cursor: pointer; transition: 0.2s; }}
    #weather-row:active {{ transform: scale(0.95); opacity: 0.8; }}

    .controls {{ position: fixed; left: 25px; bottom: 25px; display: flex; gap: 15px; z-index: 9999; }}
    .btn {{
        width: 45px; height: 45px; border-radius: 50%; background: rgba(0,0,0,0.4);
        border: 1px solid rgba(255,255,255,0.3); color: #fff; display: flex; align-items: center; justify-content: center;
        cursor: pointer; font-size: 14px;
    }}
</style>
</head>
<body id="master-body">
    <div class="controls">
        <div id="btn-style" class="btn">背景</div>
    </div>

    <div class="glass-panel">
        <div class="row" id="year"></div>
        <div class="row">
            <div id="month" class="row"></div>
            <div style="color:white; opacity:0.3; font-size:30px; margin: 0 5px">/</div>
            <div id="day" class="row"></div>
        </div>
        <div class="row" id="lunar" style="transform:scale(0.85)"></div>

        <div class="row" id="weather-row" style="margin: 10px 0;">
            <div id="w-city" class="row"></div>
            <div style="width:15px"></div>
            <div id="w-desc" class="row"></div>
            <div style="width:15px"></div>
            <div id="w-temp" class="row"></div>
        </div>

        <div class="row" id="time"></div>
    </div>

<script src="https://cdn.jsdelivr.net/npm/lunar-javascript/lunar.js"></script>
<script>
    let cityIdx = 0;
    const weatherData = [
        {{ city: "台北", desc: "多雲", temp: "21°" }},
        {{ city: "台中", desc: "晴天", temp: "25°" }},
        {{ city: "高雄", desc: "晴朗", temp: "28°" }},
        {{ city: "台東", desc: "短暫雨", temp: "23°" }}
    ];

    function updateFlaps(id, val) {{
        const box = document.getElementById(id);
        const s = val.toString();
        if (box.innerHTML === "" || box.childElementCount !== s.length) {{
            box.innerHTML = [...s].map(c => `
                <div class="flap-unit">
                    <div class="half top"><div class="text">${{c}}</div></div>
                    <div class="half bottom"><div class="text">${{c}}</div></div>
                </div>`).join('');
        }}
        const texts = box.querySelectorAll('.text');
        [...s].forEach((n, i) => {{
            texts[i*2].innerText = n; 
            texts[i*2+1].innerText = n;
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
    
    document.getElementById('btn-style').addEventListener('click', () => {{
        const body = document.getElementById('master-body');
        if(body.style.background.includes('photo')) {{
            body.style.background = '#222';
        }} else {{
            body.style.background = "url('https://images.unsplash.com/photo-1516550893923-42d28e5677af?q=80&w=2072&auto=format&fit=crop') no-repeat center center fixed";
            body.style.backgroundSize = "cover";
        }}
    }});

    function tick() {{
        const d = new Date(), l = Lunar.fromDate(d);
        updateFlaps('year', d.getFullYear());
        updateFlaps('month', (d.getMonth()+1).toString().padStart(2,'0'));
        updateFlaps('day', d.getDate().toString().padStart(2,'0'));
        updateFlaps('lunar', l.getMonthInChinese()+'月'+l.getDayInChinese());
        updateFlaps('time', d.getHours().toString().padStart(2,'0')+d.getMinutes().toString().padStart(2,'0')+d.getSeconds().toString().padStart(2,'0'));
    }}

    setInterval(tick, 1000); 
    tick();
    switchCity();
</script>
</body>
</html>
"""
components.html(html_code, height=900)
