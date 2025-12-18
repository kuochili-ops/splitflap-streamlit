import streamlit as st
import streamlit.components.v1 as components
import math
import urllib.parse
import html

# --- 1. 頁面佈局與透明化樣式 ---
st.set_page_config(layout="centered")

# 獲取嵌入狀態
query_params = st.query_params
is_embedded = query_params.get("embed", "false").lower() == "true"

# 強制透明化背景的 CSS
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding-top: 1rem; background-color: transparent !important;}
    .stApp {background-color: transparent !important;}
    body {background-color: transparent !important;}
    /* 讓 Slider 和輸入框在深色模式下更易讀 */
    .stTextInput label, .stSlider label {color: #eee !important; font-weight: bold;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 參數獲取與亂碼修正 ---
def decode_text(text):
    try:
        unquoted = urllib.parse.unquote(text)
        decoded = html.unescape(unquoted)
        return decoded
    except:
        return text

# 預設文字
default_text = decode_text(query_params.get("text", "筆畫精準銜接，點擊或輸入即可更換"))
default_stay = float(query_params.get("stay", 2.5))

# --- 3. 互動介面 (僅在非嵌入模式顯示) ---
if not is_embedded:
    col1, col2 = st.columns([3, 1])
    with col1:
        input_content = st.text_input("輸入顯示訊息 (多行請用逗號隔開)", default_text)
    with col2:
        stay_seconds = st.slider("停留秒數", 1.0, 10.0, default_stay, 0.5)
else:
    input_content = default_text
    stay_seconds = default_stay

# --- 4. 計算行列 ---
N = len(input_content)
cols = min(math.ceil(N / 2), 10) if N > 1 else 1
# 支援逗號換行，或自動切分
if "，" in input_content or "," in input_content:
    raw_rows = input_content.replace("，", ",").split(",")
    rows_data = []
    for r in raw_rows:
        row_chars = list(r.strip())
        while len(row_chars) < cols: row_chars.append(" ")
        rows_data.append(row_chars[:cols]) # 限制寬度
else:
    rows_data = [list(input_content[i:i+cols]) for i in range(0, len(input_content), cols)]
    for row in rows_data:
        while len(row) < cols: row.append(" ")

# --- 5. 核心看板 HTML ---
html_code = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    :root {{
        --unit-width: calc(min(85px, 94vw / {cols} - 6px));
        --unit-height: calc(var(--unit-width) * 1.5);
        --font-size: calc(var(--unit-width) * 1.05);
        --flip-speed: 0.6s;
        --card-bg: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%);
    }}
    body {{ background: transparent !important; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; overflow: hidden; cursor: pointer; user-select: none; }}
    .board-row {{ display: grid; grid-template-columns: repeat({cols}, var(--unit-width)); gap: 8px; perspective: 2000px; }}
    .flap-unit {{ position: relative; width: var(--unit-width); height: var(--unit-height); background: #000; border-radius: 6px; font-family: 'Noto Sans TC', sans-serif; font-size: var(--font-size); font-weight: 900; color: #f0f0f0; }}
    .half {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: var(--card-bg); display: flex; justify-content: center; backface-visibility: hidden; -webkit-backface-visibility: hidden; }}
    .top {{ top: 0; height: calc(50% + 1px); align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.5); }}
    .bottom {{ bottom: 0; height: 50%; align-items: flex-end; border-radius: 0 0 6px 6px; }}
    .text {{ height: var(--unit-height); width: 100%; text-align: center; position: absolute; left: 0; line-height: var(--unit-height); }}
    .top .text {{ top: 0; }}
    .bottom .text {{ bottom: 0; }}
    .leaf {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 15; transform-origin: bottom; transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }}
    .leaf-front {{ z-index: 16; background: var(--card-bg); }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #1a1a1a; display: flex; justify-content: center; align-items: flex-end; overflow: hidden; }}
    .flipping {{ transform: rotateX(-180deg); }}
    .flap-unit::before {{ content: ""; position: absolute; top: 50%; left: -1px; width: calc(100% + 2px); height: 2px; background: rgba(0,0,0,0.8); transform: translateY(-50%); z-index: 60; }}
</style>
</head>
<body>
<div id="board-container" class="board-row"></div>
<script>
    const allRows = {rows_data};
    const stayTime = {stay_seconds} * 1000;
    let currentRowIndex = 0, isAnimating = false, autoTimer = null;

    function createRow(contentArray) {{
        return contentArray.map(char => `
            <div class="flap-unit">
                <div class="half top base-top"><div class="text">${{char}}</div></div>
                <div class="half bottom base-bottom"><div class="text">${{char}}</div></div>
                <div class="leaf">
                    <div class="half top leaf-front"><div class="text">${{char}}</div></div>
                    <div class="half bottom leaf-back"><div class="text">${{char}}</div></div>
                </div>
            </div>`).join('');
    }}

    function performFlip() {{
        if (allRows.length <= 1 || isAnimating) return;
        isAnimating = true;
        const nextRowIndex = (currentRowIndex + 1) % allRows.length;
        const nextChars = allRows[nextRowIndex];
        const units = document.querySelectorAll('.flap-unit');
        units.forEach((u, i) => {{
            setTimeout(() => {{
                const leaf = u.querySelector('.leaf');
                u.querySelector('.leaf-back .text').innerText = nextChars[i];
                leaf.classList.add('flipping');
                setTimeout(() => {{
                    u.querySelector('.base-top .text').innerText = nextChars[i];
                    u.querySelector('.base-bottom .text').innerText = nextChars[i];
                }}, 300);
                leaf.addEventListener('transitionend', function onEnd() {{
                    leaf.removeEventListener('transitionend', onEnd);
                    u.querySelector('.leaf-front .text').innerText = nextChars[i];
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    leaf.offsetHeight; 
                    leaf.style.transition = '';
                    if (i === units.length - 1) {{ isAnimating = false; resetTimer(); }}
                }}, {{once: true}});
            }}, i * 40);
        }});
        currentRowIndex = nextRowIndex;
    }}

    function resetTimer() {{
        if (autoTimer) clearInterval(autoTimer);
        autoTimer = setInterval(performFlip, stayTime);
    }}

    function init() {{
        document.getElementById('board-container').innerHTML = createRow(allRows[0]);
        resetTimer();
    }}
    document.body.addEventListener('click', () => {{ if (!isAnimating) performFlip(); }});
    window.onload = init;
</script>
</body>
</html>
"""

components.html(html_code, height=400)
