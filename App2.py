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

# --- 2. 核心 HTML (整合 3D 動態翻板與清水模背景) ---
html_code = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    :root {
        --font-family: "PingFang TC", "Microsoft JhengHei", "Noto Sans TC", sans-serif;
        --flip-speed: 0.6s;
        /* 高質感黑色翻板背景 */
        --card-bg: linear-gradient(180deg, #3a3a3a 0%, #1a1a1a 50%, #000 51%, #222 100%);
    }

    body {
        margin: 0; padding-top: 30px;
        display: flex; flex-direction: column; align-items: center;
        min-height: 100vh; overflow: hidden;
        /* 模擬上傳圖片的清水模背景顏色與質感 */
        background: #bbb url('https://images.unsplash.com/photo-1590274853856-f22d5ee3d228?q=80&w=2072&auto=format&fit=crop') no-repeat center center fixed;
        background-size: cover;
    }

    /* 透明玻璃背板：寬度不超過手機螢幕 */
    .glass-panel {
        display: flex; flex-direction: column; align-items: center; gap: 12px;
        width: 92vw; max-width: 380px; 
        padding: 30px 10px;
        background: rgba(255, 255, 255, 0.05); 
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        box-shadow: 25px 35px 50px rgba(0, 0, 0, 0.45);
        transform: perspective(1000px) rotateX(1deg);
    }

    /* 翻板行與光影投射 */
    .row { 
        display: flex; gap: 4px; align-items: center; justify-content: center;
        width: 100%;
        filter: drop-shadow(15px 22px 18px rgba(0, 0, 0, 0.65));
    }

    /* 3D 翻板結構 */
    .flap-unit { 
        position: relative; width: 34px; height: 50px; 
        background: #000; border-radius: 3px; perspective: 1000px;
    }

    .half {
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden;
        background: var(--card-bg); display: flex; justify-content: center;
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }

    .top { top: 0; height: calc(50% + 0.5px); align-items: flex-start; border-radius: 3px 3px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.8); }
    .bottom { bottom: 0; height: 50%; align-items: flex-end; border-radius: 0 0 3px 3px; background: linear-gradient(180deg, #151515 0%, #000 100%); }

    .text { 
        height: 50px; width: 100%; text-align: center; position: absolute; left: 0; 
        line-height: 50px; color: #fff; font-size: 32px; font-weight: 900; font-family: var(--font-family);
    }
    .top .text { top: 0; }
    .bottom .text { bottom: 0; }

    /* 翻轉葉片 */
    .leaf { 
        position: absolute; top: 0; left: 0; width: 100%; height: 50%; 
        z-index: 15; transform-origin: bottom; 
        transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); 
        transform-style: preserve-3d; 
    }
    .leaf-front { z-index: 16; background: var(--card-bg); border-radius: 3px 3px 0 0; }
    .leaf-back { 
        transform: rotateX(-180deg); z-index: 15; background: #111; 
        display: flex; justify-content: center; align-items: flex-end; 
        overflow: hidden; border-radius: 0 0 3px 3px; 
    }
    .flipping { transform: rotateX(-180deg); }

    /* 翻板中心縫隙線 */
    .flap-unit::before { 
        content: ""; position: absolute; top: 50%; left: 0; 
        width: 100%; height: 1.2px; background: rgba(0,0,0,0.9); 
        transform: translateY(-50%); z-index: 60; 
    }

    #weather-row { cursor: pointer; transition: 0.2s; }
    .separator { color: white; opacity: 0.3; font-size: 20px; margin: 0 4px; }
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
            <div class="row" id="w-desc" style="margin: 8px 0;"></div>
            <div class="row" id="w-temp"></div>
        </div>

        <div class="row" id="time"></div>
    </div>

<script src="https://cdn.jsdelivr.net/npm/lunar-javascript/lunar.js"></script>
<script>
    let cityIdx = 0;
    const weatherData = [
        { city: "台北市", desc: "多雲時晴", temp: "21°" },
        { city: "台中市", desc: "局部晴朗", temp: "24°" },
        { city: "高雄市", desc: "暖和晴天", temp: "27°" },
        { city: "花蓮縣", desc: "陰短暫雨", temp: "22°" }
    ];

    function createFlapUnit(c) {
        return `
            <div class="flap-unit">
                <div class="half top base-top"><div class="text">${c}</div></div>
                <div class="half bottom base-bottom"><div class="text">${c}</div></div>
                <div class="leaf">
                    <div class="half top leaf-front"><div class="text">${c}</div></div>
                    <div class="half bottom leaf-back"><div class="text">${c}</div></div>
                </div>
            </div>`;
    }

    function updateFlaps(id, val) {
        const box = document.getElementById(id);
        const s = val.toString();
        
        if (box.childElementCount !== s.length) {
            box.innerHTML = [...s].map(c => createFlapUnit(c)).join('');
            return;
        }

        const units = box.querySelectorAll('.flap-unit');
        [...s].forEach((char, i) => {
            const u = units[i];
            const current = u.querySelector('.base-top .text').innerText;
            if (current !== char) {
                setTimeout(() => {
                    const leaf = u.querySelector('.leaf');
                    u.querySelector('.leaf-back .text').innerText = char;
                    leaf.classList.add('flipping');
                    
                    setTimeout(() => {
                        u.querySelector('.base-top .text').innerText = char;
                        u.querySelector('.base-bottom .text').innerText = char;
                    }, 300);

                    leaf.addEventListener('transitionend', () => {
                        u.querySelector('.leaf-front .text').innerText = char;
                        leaf.style.transition = 'none';
                        leaf.classList.remove('flipping');
                        leaf.offsetHeight; 
                        leaf.style.transition = '';
                    }, {once: true});
                }, i * 45); // 加入連續翻轉的延遲感
            }
        });
    }

    function switchCity() {
        const data = weatherData[cityIdx];
        updateFlaps('w-city', data.city);
        updateFlaps('w-desc', data.desc);
        updateFlaps('w-temp', data.temp);
        cityIdx = (cityIdx + 1) % weatherData.length;
    }

    document.getElementById('weather-row').addEventListener('click', switchCity);

    function tick() {
        const d = new Date(), l = Lunar.fromDate(d);
        updateFlaps('year', d.getFullYear());
        updateFlaps('month', (d.getMonth()+1).toString().padStart(2,'0'));
        updateFlaps('day', d.getDate().toString().padStart(2,'0'));
        
        const lunarStr = l.getMonthInChinese() + '月' + l.getDayInChinese() + ' ' + (l.getJieQi() || "");
        updateFlaps('lunar-row', lunarStr.trim());
        
        const timeStr = d.getHours().toString().padStart(2,'0') + 
                        d.getMinutes().toString().padStart(2,'0') + 
                        d.getSeconds().toString().padStart(2,'0');
        updateFlaps('time', timeStr);
    }

    setInterval(tick, 1000); 
    tick();
    switchCity();
</script>
</body>
</html>
"""

components.html(html_code, height=900)
