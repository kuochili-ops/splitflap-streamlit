import streamlit as st
import streamlit.components.v1 as components
import math
import urllib.parse

# --- 1. 極致 UI 隱藏與背景設定 ---
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    /* 移除所有 Streamlit 預設間距與裝飾 */
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0px; margin: 0px;}
    body {background-color: transparent; overflow: hidden;}
    /* 讓 Slider 顯示更精緻 */
    .stSlider label {color: #ccc; font-size: 0.8rem;}
    [data-testid="stVerticalBlock"] {gap: 0.5rem;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 強化版編碼處理 ---
query_params = st.query_params
is_embedded = query_params.get("embed", "false").lower() == "true"
raw_text = query_params.get("text", "")

# 解決亂碼關鍵：優先使用 URL 解碼，並預防重複編碼
def get_safe_text(raw):
    if not raw: return "Serena 是我的女神"
    try:
        # 嘗試處理可能的 Latin-1 轉 UTF-8 錯誤
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

# --- 3. 規格邏輯：動態寬度 (商數限定 10 格) ---
N = len(input_text)
if N <= 1:
    cols = 1
else:
    quotient = math.ceil(N / 2)
    cols = quotient if quotient < 10 else 10

rows_data = [list(input_text[i:i+cols]) for i in range(0, len(input_text), cols)]
for row in rows_data:
    while len(row) < cols:
        row.append(" ")

# --- 4. 旗艦版 HTML (修正 3D 渲染與筆劃錯位) ---
html_code = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    :root {{
        --unit-width: calc(min(75px, 98vw / {cols} - 6px));
        --unit-height: calc(var(--unit-width) * 1.5);
        --font-size: calc(var(--unit-width) * 0.85);
        --card-bg: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%);
    }}
    body {{ 
        background: transparent; display: flex; justify-content: center; align-items: center; 
        height: 100vh; margin: 0; overflow: hidden; cursor: pointer; user-select: none;
    }}
    .board-row {{ 
        display: grid; grid-template-columns: repeat({cols}, var(--unit-width)); 
        gap: 6px; perspective: 2500px;
    }}
    .flap-unit {{ 
        position: relative; width: var(--unit-width); height: var(--unit-height); 
        background: #000; border-radius: 4px; font-family: 'Noto Sans TC', sans-serif; 
        font-size: var(--font-size); font-weight: 900; color: #fff;
    }}
    /* 修正半部顯示：確保內容垂直對齊不偏移 */
    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center; 
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }}
    .top {{ top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 1px solid #000; }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; }}
    .text {{ 
        height: var(--unit-height); line-height: var(--unit-height); 
        text-align: center; width: 100%;
        display: block;
    }}
    .leaf {{ 
        position: absolute; top: 0; left: 0; width: 100%; height: 50%; 
        z-index: 20; transform-origin: bottom; 
        transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1.25); 
        transform-style: preserve-3d;
    }}
    .leaf-front {{ z-index: 21; background: var(--card-bg); }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 20; background: #1a1a1a; }}
    .flipping {{ transform: rotateX(-180deg); }}
    /* 中央細線 */
    .flap-unit::after {{
        content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
        background: rgba(0,0,0,0.8); z-index: 50; transform: translateY(-50%);
    }}
</style>
</head>
<body>
<div id="board" class="board-row"></div>
<script>
    const allData = {rows_data};
    const stayTime = {stay_seconds} * 1000;
    let curr = 0;
    let busy = false;
    let timer;

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

# 動態高度：確保在嵌入時不顯示捲軸
components.html(html_code, height=220 if is_embedded else 350)
