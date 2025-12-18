import streamlit as st
import streamlit.components.v1 as components
import math
import urllib.parse

st.set_page_config(layout="centered")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding-top: 2rem;}
    body {background-color: #0e1117;}
    .stSlider label {color: #eee; font-weight: bold; font-size: 1rem;}
    </style>
    """, unsafe_allow_html=True)

query_params = st.query_params
is_embedded = query_params.get("embed", "false").lower() == "true"
raw_url_text = query_params.get("text", "")

def get_safe_text(raw):
    if not raw: return "筆畫精準銜接，首幀完美對齊"
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
        stay_seconds = st.slider("停留秒數", 1.0, 10.0, 2.5, 0.5)
else:
    stay_seconds = float(query_params.get("stay", 2.5))

N = len(input_text)
cols = min(math.ceil(N / 2), 10) if N > 1 else 1
rows_data = [list(input_text[i:i+cols]) for i in range(0, len(input_text), cols)]
for row in rows_data:
    while len(row) < cols: row.append(" ")

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
    body {{ background: transparent; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; overflow: hidden; cursor: pointer; }}
    .board {{ display: grid; grid-template-columns: repeat({cols}, var(--unit-width)); gap: 10px; perspective: 2000px; }}
    
    .flap {{ position: relative; width: var(--unit-width); height: var(--unit-height); background: #000; border-radius: 4px; font-family: 'Noto Sans TC', sans-serif; font-size: var(--font-size); font-weight: 900; color: #fff; line-height: 1; }}
    
    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center; 
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }}
    
    /* 核心修正：首幀高度補償與中線強化 */
    .top {{ top: 0; height: calc(50% + 1px); align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.8); }}
    .bottom {{ bottom: 0; height: 50%; align-items: flex-end; border-radius: 0 0 4px 4px; }}
    
    .text {{ 
        height: var(--unit-height); line-height: var(--unit-height); 
        text-align: center; width: 100%; position: absolute; left: 0;
        transform: translateZ(0); /* 強制開啟硬體加速 */
    }}
    .top .text {{ top: 0; }}
    .bottom .text {{ bottom: 0; }}

    .leaf {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 20; transform-origin: bottom; transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }}
    .leaf-front {{ z-index: 21; background: var(--card-bg); }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 20; background: #1a1a1a; display: flex; justify-content: center; align-items: flex-end; }}
    .flipping {{ transform: rotateX(-180deg); }}

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
        const board = document.getElementById('board');
        board.innerHTML = chars.map(c => `
            <div class="flap">
                <div class="half top base-t"><div class="text">${{c}}</div></div>
                <div class="half bottom base-b"><div class="text">${{c}}</div></div>
                <div class="leaf">
                    <div class="half top leaf-f"><div class="text">${{c}}</div></div>
                    <div class="half bottom leaf-b"><div class="text">${{c}}</div></div>
                </div>
            </div>`).join('');
            
        // 初始載入強制校準：讓瀏覽器立即計算所有元素的尺寸
        requestAnimationFrame(() => {{
            const texts = document.querySelectorAll('.text');
            texts.forEach(t => t.style.opacity = '1');
        }});
    }}

    function flip() {{
        if (allData.length <= 1 || busy) return;
        busy = true;
        const nextChars = allData[(curr + 1) % allData.length];
        const units = document.querySelectorAll('.flap');

        units.forEach((u, i) => {{
            setTimeout(() => {{
                const leaf = u.querySelector('.leaf');
                
                // 瞬間歸位重置
                leaf.style.transition = 'none';
                leaf.classList.remove('flipping');
                
                const prevText = u.querySelector('.base-t .text').innerText;
                u.querySelector('.leaf-f .text').innerText = prevText;
                u.querySelector('.leaf-b .text').innerText = nextChars[i];
                
                leaf.offsetHeight; 

                // 開始翻轉
                leaf.style.transition = '';
                leaf.classList.add('flipping');

                setTimeout(() => {{
                    u.querySelector('.base-t .text').innerText = nextChars[i];
                }}, 280);

                leaf.addEventListener('transitionend', function end() {{
                    leaf.removeEventListener('transitionend', end);
                    u.querySelector('.base-b .text').innerText = nextChars[i];
                    
                    if (i === units.length - 1) {{ 
                        busy = false; 
                        startTimer(); 
                    }}
                }}, {{once: true}});
            }}, i * 45);
        }});
        curr = (curr + 1) % allData.length;
    }}

    function startTimer() {{ clearTimeout(timer); timer = setTimeout(flip, stayTime); }}
    document.body.onclick = () => {{ if(!busy) flip(); }};
    
    // 初始化
    build(allData[0]); 
    startTimer();
</script>
</body>
</html>
"""

components.html(html_code, height=350)
