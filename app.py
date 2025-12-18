import streamlit as st
import streamlit.components.v1 as components
import math
import urllib.parse

# --- 1. 頁面佈局設定 ---
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding-top: 2rem;}
    body {background-color: #0e1117;}
    .stSlider label {color: #eee; font-weight: bold; font-size: 1rem;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 獲取文字與控制參數 ---
query_params = st.query_params
is_embedded = query_params.get("embed", "false").lower() == "true"
raw_url_text = query_params.get("text", "")

def get_safe_text(raw):
    if not raw: return "筆畫絕對對齊，翻轉毫無殘損"
    try:
        decoded = urllib.parse.unquote(raw)
        return decoded.encode('latin-1').decode('utf-8')
    except:
        return urllib.parse.unquote(raw)

input_text = get_safe_text(raw_url_text)

if not is_embedded:
    col1, col2 = st.columns([3, 1])
    with col1:
        input_text = st.text_input("輸入測試文字", input_text)
    with col2:
        stay_seconds = st.slider("停留秒數", 1.0, 10.0, 2.0, 0.5)
else:
    stay_seconds = float(query_params.get("stay", 2.0))

# --- 3. 計算行列寬度 ---
N = len(input_text)
cols = min(math.ceil(N / 2), 10) if N > 1 else 1
rows_data = [list(input_text[i:i+cols]) for i in range(0, len(input_text), cols)]
for row in rows_data:
    while len(row) < cols: row.append(" ")

# --- 4. 生成 HTML (核心對齊與抗鋸齒技術) ---
html_code = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    :root {{
        --unit-width: calc(min(80px, 94vw / {cols} - 8px));
        --unit-height: calc(var(--unit-width) * 1.5);
        --font-size: calc(var(--unit-width) * 1.05);
        --flip-speed: 0.6s;
        --card-bg: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%);
    }}
    body {{ background: transparent; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; overflow: hidden; cursor: pointer; user-select: none; }}
    .board {{ display: grid; grid-template-columns: repeat({cols}, var(--unit-width)); gap: 10px; perspective: 2000px; }}
    
    .flap {{ position: relative; width: var(--unit-width); height: var(--unit-height); background: #000; border-radius: 4px; font-family: 'Noto Sans TC', sans-serif; font-size: var(--font-size); font-weight: 900; color: #fff; }}
    
    /* 核心修復：強制上下半格共用同一個基準原點，防止筆畫斷開 */
    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center; align-items: center;
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }}
    .top {{ top: 0; border-radius: 4px 4px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.8); }}
    .bottom {{ bottom: 0; border-radius: 0 0 4px 4px; }}
    
    /* 確保文字在兩半格中絕對重合 🧩 */
    .text {{ 
        height: var(--unit-height); 
        line-height: var(--unit-height); 
        text-align: center; width: 100%; 
        position: absolute; left: 0;
        top: 50%; transform: translateY(-50%); /* 鎖定中心線 */
    }}
    /* 精確裁剪上下半部，防止溢出或殘留 */
    .top .text {{ clip-path: inset(0 0 50% 0); }}
    .bottom .text {{ clip-path: inset(50% 0 0 0); }}

    .leaf {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 20; transform-origin: bottom; transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1.15); transform-style: preserve-3d; }}
    .leaf-front {{ z-index: 21; background: var(--card-bg); }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 20; background: #1a1a1a; }}
    .flipping {{ transform: rotateX(-180deg); }}

    /* 物理轉軸細節 */
    .flap::after {{ content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px; background: rgba(0,0,0,0.9); z-index: 50; transform: translateY(-50%); }}
</style>
</head>
<body>
<div id="board" class="board"></div>
<script>
    const allData = {rows_data};
    const stayTime = {stay_seconds} * 1000;
    let curr = 0, busy = false, timer;

    function build(chars) {{
        document.getElementById('board').innerHTML = chars.map(c => `
            <div class="flap">
                <div class="half top base-t"><div class="text">${{c}}</div></div>
                <div class="half bottom base-b"><div class="text">${{c}}</div></div>
                <div class="leaf">
                    <div class="half top leaf-f"><div class="text">${{c}}</div></div>
                    <div class="half bottom leaf-back-half"><div class="text">${{c}}</div></div>
                </div>
            </div>`).join('');
    }}

    function flip() {{
        if (allData.length <= 1 || busy) return;
        busy = true;
        const nextChars = allData[(curr + 1) % allData.length];
        const units = document.querySelectorAll('.flap');

        units.forEach((u, i) => {{
            setTimeout(() => {{
                const leaf = u.querySelector('.leaf');
                u.querySelector('.leaf-back-half .text').innerText = nextChars[i];
                u.querySelector('.base-t .text').innerText = nextChars[i];
                
                leaf.classList.add('flipping');

                // 核心同步：旋轉至 90 度瞬間切換剩餘部分
                setTimeout(() => {{
                    u.querySelector('.leaf-f .text').innerText = nextChars[i];
                    u.querySelector('.base-b .text').innerText = nextChars[i];
                }}, 275); 

                leaf.addEventListener('transitionend', function end() {{
                    leaf.removeEventListener('transitionend', end);
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    leaf.offsetHeight; 
                    leaf.style.transition = '';
                    if (i === units.length - 1) {{ busy = false; startTimer(); }}
                }}, {{once: true}});
            }}, i * 40);
        }});
        curr = (curr + 1) % allData.length;
    }}

    function startTimer() {{ clearTimeout(timer); timer = setTimeout(flip, stayTime); }}
    document.body.onclick = () => {{ if(!busy) flip(); }};
    build(allData[0]); startTimer();
</script>
</body>
</html>
"""

components.html(html_code, height=350)
