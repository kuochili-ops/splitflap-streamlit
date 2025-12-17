import streamlit as st
import streamlit.components.v1 as components
import math
import urllib.parse

# --- 1. 極致 UI 隱藏與佈局修正 ---
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0px; margin: 0px;}
    body {background-color: transparent; overflow: hidden;}
    [data-testid="stVerticalBlock"] {gap: 0.5rem;}
    /* 讓 Slider 顯示更精緻 */
    .stSlider label {color: #ccc; font-size: 0.8rem;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 強化版編碼處理 ---
query_params = st.query_params
is_embedded = query_params.get("embed", "false").lower() == "true"
raw_text = query_params.get("text", "")

def get_safe_text(raw):
    if not raw: return "女神降臨"
    try:
        decoded = urllib.parse.unquote(raw)
        return decoded.encode('latin-1').decode('utf-8')
    except:
        return urllib.parse.unquote(raw)

input_text = get_safe_text(raw_text)

if not is_embedded:
    col1, col2 = st.columns([3, 1])
    with col1:
        input_text = st.text_input("輸入內容", input_text)
    with col2:
        stay_seconds = st.slider("停留秒數", 0.5, 5.0, 2.0, 0.5)
else:
    stay_seconds = float(query_params.get("stay", 2.0))

# --- 3. 動態寬度邏輯 ---
N = len(input_text)
if N <= 1:
    cols = 1
else:
    quotient = math.ceil(N / 2)
    cols = min(quotient, 10)

rows_data = [list(input_text[i:i+cols]) for i in range(0, len(input_text), cols)]
for row in rows_data:
    while len(row) < cols:
        row.append(" ")

# --- 4. 生成 HTML (解決對齊與筆劃問題) ---
html_code = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    :root {{
        --unit-width: calc(min(75px, 98vw / {cols} - 6px));
        --unit-height: calc(var(--unit-width) * 1.4);
        --font-size: calc(var(--unit-width) * 0.95);
        --card-bg: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%);
    }}
    body {{ 
        background: transparent; display: flex; justify-content: center; align-items: center; 
        height: 100vh; margin: 0; overflow: hidden; cursor: pointer; user-select: none;
    }}
    .board-row {{ 
        display: grid; grid-template-columns: repeat({cols}, var(--unit-width)); 
        gap: 6px; perspective: 2000px;
    }}
    .flap-unit {{ 
        position: relative; width: var(--unit-width); height: var(--unit-height); 
        background: #000; border-radius: 4px; font-family: 'Noto Sans TC', sans-serif; 
        font-size: var(--font-size); font-weight: 900; color: #fff;
    }}
    /* 修復筆劃關鍵：使用 flex 置中並精確裁切 */
    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center;
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }}
    .top {{ 
        top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; 
        border-bottom: 1px solid rgba(0,0,0,0.5); 
    }}
    .bottom {{ 
        bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; 
    }}
    /* 強制文字在上下兩端正確顯示，不使用 line-height 以防偏差 */
    .text {{ 
        height: var(--unit-height); 
        display: flex; align-items: center; justify-content: center;
        position: absolute; width: 100%;
    }}
    .top .text {{ top: 0; }}
    .bottom .text {{ bottom: 0; }}

    .leaf {{ 
        position: absolute; top: 0; left: 0; width: 100%; height: 50%; 
        z-index: 20; transform-origin: bottom; 
        transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1); 
        transform-style: preserve-3d;
    }}
    .leaf-front {{ z-index: 21; background: #2a2a2a; }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 20; background: #1a1a1a; }}
    .flipping {{ transform: rotateX(-180deg); }}
    
    /* 轉軸細線 */
    .flap-unit::after {{
        content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
        background: #000; z-index: 50; transform: translateY(-50%);
    }}
</style>
</head>
<body>
<div id="board" class="board-row"></div>
<script>
    const allData = {rows_data};
    const stayTime = {stay_seconds} * 1000;
    let curr = 0; let busy = false; let timer;

    function build(chars) {{
        document.getElementById('board').innerHTML = chars.map(c => `
            <div class="flap-unit">
                <div class="half top bt"><div class="text">${{c}}</div></div>
                <div class="half bottom bb"><div class="text">${{c}}</div></div>
                <div class="leaf">
                    <div class="half top lf"><div class="text">${{c}}</div></div>
                    <div class="half bottom lb"><div class="text">${{c}}</div></div>
                </div>
            </div>`).join('');
    }}

    function flip() {{
        if (allData.length <= 1 || busy) return;
        busy = true;
        const next = (curr + 1) % allData.length;
        const chars = allData[next];
        const units = document.querySelectorAll('.flap-unit');

        units.forEach((u, i) => {{
            setTimeout(() => {{
                const leaf = u.querySelector('.leaf');
                u.querySelector('.bt .text').innerText = chars[i];
                u.querySelector('.lb .text').innerText = chars[i];
                leaf.classList.add('flipping');
                
                leaf.addEventListener('transitionend', function end() {{
                    leaf.removeEventListener('transitionend', end);
                    u.querySelector('.bb .text').innerText = chars[i];
                    u.querySelector('.lf .text').innerText = chars[i];
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    leaf.offsetHeight;
                    leaf.style.transition = '';
                    if (i === units.length - 1) {{ busy = false; startTimer(); }}
                }}, {{once: true}});
            }}, i * 40);
        }});
        curr = next;
    }}

    function startTimer() {{
        clearTimeout(timer);
        timer = setTimeout(flip, stayTime);
    }}

    document.body.onclick = () => {{ if(!busy) {{ clearTimeout(timer); flip(); }} }};
    build(allData[0]);
    startTimer();
</script>
</body>
</html>
"""

components.html(html_code, height=220 if is_embedded else 350)
