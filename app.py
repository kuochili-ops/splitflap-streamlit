import streamlit as st
import streamlit.components.v1 as components
import math
import urllib.parse

# --- 1. 頁面隱藏設定 (完全去除邊框與滾動條) ---
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0px; margin: 0px;}
    body {background-color: transparent; overflow: hidden;}
    [data-testid="stVerticalBlock"] {gap: 0rem;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 強化版文字獲取與編碼修正 ---
query_params = st.query_params
is_embedded = query_params.get("embed", "false").lower() == "true"
raw_text = query_params.get("text", "")

# 修正亂碼關鍵：先手動解碼 URL，再處理 Streamlit 可能產生的編碼錯誤
def safe_decode(text):
    if not text: return "Serena 是我的女神"
    # 處理 URL 編碼
    decoded = urllib.parse.unquote(text)
    # 避免雙重編碼導致的亂碼
    try:
        return decoded.encode('latin-1').decode('utf-8')
    except:
        return decoded

input_text = safe_decode(raw_text)

# 控制參數
if not is_embedded:
    col1, col2 = st.columns([3, 1])
    with col1:
        input_text = st.text_input("輸入內容", input_text)
    with col2:
        stay_seconds = st.slider("停留秒數", 0.5, 5.0, 2.0, 0.5)
else:
    stay_seconds = float(query_params.get("stay", 2.0))

# --- 3. 動態寬度邏輯 (您的規格) ---
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

# --- 4. 旗艦版翻板 HTML (修正渲染問題) ---
html_code = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    :root {{
        --unit-width: calc(min(72px, 98vw / {cols} - 6px));
        --unit-height: calc(var(--unit-width) * 1.5);
        --font-size: calc(var(--unit-width) * 0.85);
    }}
    body {{ 
        background: transparent; display: flex; justify-content: center; align-items: center; 
        height: 100vh; margin: 0; overflow: hidden; cursor: pointer;
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
    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%); 
        display: flex; justify-content: center; backface-visibility: hidden;
    }}
    .top {{ top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 1px solid #000; }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; }}
    .text {{ height: var(--unit-height); line-height: var(--unit-height); text-align: center; }}
    .leaf {{ 
        position: absolute; top: 0; left: 0; width: 100%; height: 50%; 
        z-index: 15; transform-origin: bottom; 
        transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1.2); transform-style: preserve-3d;
    }}
    .leaf-front {{ z-index: 16; background: #2a2a2a; }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #1a1a1a; }}
    .flipping {{ transform: rotateX(-180deg); }}
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
                <div class="half bottom bb"><div class="text">${{charToHtml(c)}}</div></div>
                <div class="leaf">
                    <div class="half top lf"><div class="text">${{charToHtml(c)}}</div></div>
                    <div class="half bottom lb"><div class="text">${{charToHtml(c)}}</div></div>
                </div>
            </div>`).join('');
    }}

    function charToHtml(c) {{ return c === " " ? "&nbsp;" : c; }}

    function flip() {{
        if (allData.length <= 1 || busy) return;
        busy = true;
        const next = (curr + 1) % allData.length;
        const chars = allData[next];
        const units = document.querySelectorAll('.flap-unit');

        units.forEach((u, i) => {{
            setTimeout(() => {{
                const leaf = u.querySelector('.leaf');
                u.querySelector('.bt .text').innerHTML = charToHtml(chars[i]);
                u.querySelector('.lb .text').innerHTML = charToHtml(chars[i]);
                leaf.classList.add('flipping');
                leaf.addEventListener('transitionend', function end() {{
                    leaf.removeEventListener('transitionend', end);
                    u.querySelector('.bb .text').innerHTML = charToHtml(chars[i]);
                    u.querySelector('.lf .text').innerHTML = charToHtml(chars[i]);
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

# 計算高度以適應不同行數
components.html(html_code, height=200 if is_embedded else 300)
