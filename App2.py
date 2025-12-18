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

# --- 2. 核心 HTML (包含翻轉動畫) ---
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
        min-height: 100vh; overflow: hidden;
        background: #bbb url('https://images.unsplash.com/photo-1590274853856-f22d5ee3d228?q=80&w=2072&auto=format&fit=crop') no-repeat center center fixed;
        background-size: cover;
    }}

    .glass-panel {{
        display: flex; flex-direction: column; align-items: center; gap: 15px;
        width: 92vw; max-width: 380px; 
        padding: 40px 10px;
        background: rgba(255, 255, 255, 0.05); 
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        box-shadow: 20px 30px 50px rgba(0, 0, 0, 0.4);
    }}

    .row {{ display: flex; gap: 4px; align-items: center; justify-content: center; width: 100%; filter: drop-shadow(15px 20px 15px rgba(0, 0, 0, 0.6)); }}

    /* 翻板基礎結構 */
    .flap-unit {{ 
        position: relative; width: 38px; height: 56px; 
        background: #000; border-radius: 4px;
        perspective: 300px;
    }}

    .half {{
        position: absolute; width: 100%; height: 50%; overflow: hidden;
        background: #1a1a1a; color: #fff; font-size: 36px; font-weight: 900;
        display: flex; justify-content: center; left: 0;
        font-family: "PingFang TC", sans-serif;
    }}

    .top {{ top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 0.5px solid #000; z-index: 2; }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; z-index: 1; }}
    
    /* 動畫核心：翻轉片 */
    .leaf {{
        position: absolute; top: 0; left: 0; width: 100%; height: 50%;
        background: #1a1a1a; color: #fff; font-size: 36px; font-weight: 900;
        display: flex; justify-content: center; align-items: flex-start;
        border-radius: 4px 4px 0 0; border-bottom: 0.5px solid #000;
        transform-origin: bottom; z-index: 3; transition: transform 0.4s ease-in;
        backface-visibility: hidden;
    }}

    .flipping .leaf {{ transform: rotateX(-180deg); }}
    .text {{ height: 56px; line-height: 56px; }}

    #weather-row {{ cursor: pointer; }}
    .separator {{ color: white; opacity: 0.3; font-size: 24px; margin: 0 5px; }}
</style>
</head>
<body>

    <div class="glass-panel">
        <div class="row" id="year"></div>
        <div class="row">
            <div id="month" class="row" style="width:auto"></div>
            <div class="separator">/</div>
            <div id="day" class="row" style="width:auto"></div>
        </div>
        <div class="row" id="lunar-row" style="transform: scale(0.8);"></div>
        <div id="weather-row">
            <div class="row" id="w-city"></div>
            <div class="row" id="w-desc" style="margin: 10px 0;"></div>
            <div class="row" id="w-temp"></div>
        </div>
        <div class="row" id="time"></div>
    </div>

<script src="https://cdn.jsdelivr.net/npm/lunar-javascript/lunar.js"></script>
<script>
    let cityIdx = 0;
    const weatherData = [
        {{ city: "台北市", desc: "多雲時晴", temp: "21°" }},
        {{ city: "台中市", desc: "晴朗無雲", temp: "24°" }},
        {{ city: "高雄市", desc: "暖和晴天", temp: "27°" }},
        {{ city: "宜蘭縣", desc: "陰短暫雨", temp: "19°" }}
    ];

    function createFlap(char) {{
        return `
            <div class="flap-unit">
                <div class="half top"><div class="text">${{char}}</div></div>
                <div class="leaf"><div class="text">${{char}}</div></div>
                <div class="half bottom"><div class="text">${{char}}</div></div>
            </div>`;
    }}

    function updateFlaps(id, val) {{
        const box = document.getElementById(id);
        const s = val.toString();
        
        // 如果長度不同，重新初始化結構
        if (box.childElementCount !== s.length) {{
            box.innerHTML = [...s].map(c => createFlap(c)).join('');
            return;
        }}

        const units = box.querySelectorAll('.flap-unit');
        [...s].forEach((char, i) => {{
            const unit = units[i];
            const current = unit.querySelector('.top .text').innerText;
            if (current !== char) {{
                // 觸發動畫
                unit.classList.remove('flipping');
                void unit.offsetWidth; // 強制重繪
                
                // 下半部預先換成新字
                unit.querySelector('.bottom .text').innerText = char;
                unit.classList.add('flipping');

                // 動畫結束後同步所有文字
                setTimeout(() => {{
                    unit.querySelector('.top .text').innerText = char;
                    unit.querySelector('.leaf .text').innerText = char;
                    unit.classList.remove('flipping');
                }}, 400);
            }}
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
        const lunarStr = l.getMonthInChinese() + '月' + l.getDayInChinese() + ' ' + (l.getJieQi() || "");
        updateFlaps('lunar-row', lunarStr.trim());
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
