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
# 注意：為了讓前端能靈活切換，我將城市資料改為 JavaScript 陣列處理
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body {{
        margin: 0; padding-top: 50px;
        display: flex; flex-direction: column; align-items: center;
        min-height: 100vh; overflow: hidden; gap: 15px;
        background: url('https://images.unsplash.com/photo-1516550893923-42d28e5677af?q=80&w=2072&auto=format&fit=crop') no-repeat center center fixed;
        background-size: cover;
        transition: 0.3s;
        user-select: none;
    }}

    .f-style-0 {{ font-family: "PingFang TC", "Heiti TC", sans-serif; }}
    .f-style-1 {{ font-family: "Noto Serif TC", "PMingLiU", serif; }}
    .f-style-2 {{ font-family: "Courier New", monospace; }}

    .row {{ 
        display: flex; gap: 6px; align-items: center; 
        filter: drop-shadow(10px 10px 20px rgba(0,0,0,0.5)); 
    }}

    /* 翻板基礎樣式 */
    .flap-unit {{ 
        position: relative; width: 44px; height: 66px; background: #000; border-radius: 4px;
        color: #fff; font-size: 42px; font-weight: 900;
    }}

    .half {{ 
        position: absolute; width: 100%; height: 50%; overflow: hidden; 
        background: rgba(25, 25, 25, 0.7); backdrop-filter: blur(4px);
        display: flex; justify-content: center;
    }}

    .top {{ top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 1px solid rgba(0,0,0,0.6); }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; }}
    .text {{ height: 66px; line-height: 66px; }}

    /* 天氣列專用樣式 */
    #weather-row {{ cursor: pointer; transition: transform 0.2s; }}
    #weather-row:active {{ transform: scale(0.92); }}

    .controls {{ position: fixed; left: 25px; bottom: 25px; display: flex; gap: 15px; z-index: 9999; }}
    .btn {{
        width: 50px; height: 50px; border-radius: 50%; background: rgba(0,0,0,0.5);
        border: 2px solid #fff; color: #fff; display: flex; align-items: center; justify-content: center;
        cursor: pointer; font-weight: bold;
    }}
</style>
</head>
<body id="master-body" class="f-style-0">
    <div class="controls">
        <div id="btn-font" class="btn">A</div>
        <div id="btn-style" class="btn">S</div>
    </div>

    <div class="row" id="year"></div>
    <div class="row">
        <div id="month" class="row"></div>
        <div style="color:white; opacity:0.3; font-size:30px; margin: 0 5px">/</div>
        <div id="day" class="row"></div>
    </div>
    <div class="row" id="lunar" style="transform:scale(0.8)"></div>

    <div class="row" id="weather-row" style="margin: 10px 0;">
        <div id="w-city" class="row"></div>
        <div style="width:15px"></div>
        <div id="w-desc" class="row"></div>
        <div style="width:15px"></div>
        <div id="w-temp" class="row"></div>
    </div>

    <div class="row" id="time"></div>

<script src="https://cdn.jsdelivr.net/npm/lunar-javascript/lunar.js"></script>
<script>
    let currentFontIdx = 0;
    let cityIdx = 0;

    // 模擬預報數據（您可以之後透過 API 動態更新此陣列）
    const weatherData = [
        {{ city: "台北", desc: "多雲", temp: "21°" }},
        {{ city: "台中", desc: "晴天", temp: "24°" }},
        {{ city: "高雄", desc: "晴天", temp: "26°" }},
        {{ city: "台東", desc: "陣雨", temp: "22°" }}
    ];

    function updateFlaps(id, val) {{
        const box = document.getElementById(id);
        const s = val.toString();
        // 如果長度改變或內容為空，重新生成 HTML
        if (box.innerHTML === "" || box.childElementCount !== s.length) {{
            box.innerHTML = [...s].map(c => `
                <div class="flap-unit">
                    <div class="half top"><div class="text">${{c}}</div></div>
                    <div class="half bottom"><div class="text">${{c}}</div></div>
                </div>`).join('');
        }}
        // 更新文字
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

    // 初始化與事件綁定
    document.getElementById('weather-row').addEventListener('click', switchCity);
    
    document.getElementById('btn-font').addEventListener('click', () => {{
        const body = document.getElementById('master-body');
        body.classList.remove('f-style-' + currentFontIdx);
        currentFontIdx = (currentFontIdx + 1) % 3;
        body.classList.add('f-style-' + currentFontIdx);
    }});

    document.getElementById('btn-style').addEventListener('click', () => {{
        const body = document.getElementById('master-body');
        if(body.style.background.includes('photo')) {{
            body.style.background = '#111';
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

    // 啟動
    setInterval(tick, 1000); 
    tick();
    switchCity(); // 初始顯示第一個城市
</script>
</body>
</html>
"""
components.html(html_code, height=900)
