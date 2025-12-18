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
        margin: 0; padding-top: 40px;
        display: flex; flex-direction: column; align-items: center;
        min-height: 100vh; overflow: hidden;
        /* 模擬您圖片中的清水模背景 */
        background: #bbb url('https://images.unsplash.com/photo-1590274853856-f22d5ee3d228?q=80&w=2070&auto=format&fit=crop') no-repeat center center fixed;
        background-size: cover;
    }}

    /* 透明玻璃背板：寬度限制在手機比例 */
    .glass-panel {{
        display: flex; flex-direction: column; align-items: center; gap: 15px;
        width: 92vw; max-width: 380px; 
        padding: 40px 10px;
        background: rgba(255, 255, 255, 0.05); 
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        /* 玻璃板對牆面的整體陰影 */
        box-shadow: 20px 30px 50px rgba(0, 0, 0, 0.4);
        transform: perspective(1000px) rotateX(2deg);
    }}

    /* 翻板行樣式 */
    .row {{ 
        display: flex; gap: 4px; align-items: center; justify-content: center;
        width: 100%;
        /* 翻板光影投射到牆面上的陰影 */
        filter: drop-shadow(15px 20px 15px rgba(0, 0, 0, 0.6));
    }}

    /* 翻板元件：針對中文寬度微調 */
    .flap-unit {{ 
        position: relative; width: 38px; height: 56px; background: #000; border-radius: 4px;
        color: #fff; font-size: 36px; font-weight: 900;
        font-family: "PingFang TC", "Microsoft JhengHei", sans-serif;
    }}

    .half {{ 
        position: absolute; width: 100%; height: 50%; overflow: hidden; 
        background: linear-gradient(180deg, #2a2a2a 0%, #000 100%);
        display: flex; justify-content: center;
    }}

    .top {{ top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 1px solid rgba(0,0,0,0.8); }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; }}
    .text {{ height: 56px; line-height: 56px; text-align: center; }}

    #weather-row {{ cursor: pointer; transition: 0.2s; }}
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
        
        <div class="row" id="lunar-row" style="transform: scale(0.85);"></div>

        <div id="weather-row">
            <div class="row" id="w-city"></div>
            <div class="row" id="w-desc" style="margin: 10px 0;"></div>
            <div class="row" id="w-temp"></div>
        </div>

        <div class="row" id="time" style="margin-top:5px"></div>
    </div>

<script src="https://cdn.jsdelivr.net/npm/lunar-javascript/lunar.js"></script>
<script>
    let cityIdx = 0;
    // 中文縣市與天氣數據
    const weatherData = [
        {{ city: "台北市", desc: "多雲時晴", temp: "21°" }},
        {{ city: "台中市", desc: "晴朗無雲", temp: "24°" }},
        {{ city: "高雄市", desc: "暖和晴天", temp: "27°" }},
        {{ city: "宜蘭縣", desc: "陰短暫雨", temp: "19°" }}
    ];

    function updateFlaps(id, val) {{
        const box = document.getElementById(id);
        const s = val.toString();
        // 確保寬度自適應
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
        // 更新日期
        updateFlaps('year', d.getFullYear());
        updateFlaps('month', (d.getMonth()+1).toString().padStart(2,'0'));
        updateFlaps('day', d.getDate().toString().padStart(2,'0'));
        
        // 更新農曆與節氣 (格式: 十一月廿九 冬至)
        const lunarStr = l.getMonthInChinese() + '月' + l.getDayInChinese() + ' ' + (l.getJieQi() || "");
        updateFlaps('lunar-row', lunarStr.trim());
        
        // 更新時間
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
