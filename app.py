import streamlit as st
import streamlit.components.v1 as components
import math
import urllib.parse

# --- 1. 頁面隱藏與樣式設定 ---
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding-top: 1rem;}
    body {background-color: transparent;}
    .stSlider label {color: #eee; font-weight: bold;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 獲取文字與控制參數 ---
query_params = st.query_params
is_embedded = query_params.get("embed", "false").lower() == "true"
raw_url_text = query_params.get("text", "")

def get_safe_text(raw):
    if not raw: return "首幀文字完美銜接，穩定不再殘損"
    try:
        decoded = urllib.parse.unquote(raw)
        return decoded.encode('latin-1').decode('utf-8')
    except:
        return urllib.parse.unquote(raw)

input_text = get_safe_text(raw_url_text)

if not is_embedded:
    col1, col2 = st.columns([3, 1])
    with col1:
        input_text = st.text_input("輸入句子", input_text)
    with col2:
        stay_seconds = st.slider("停留秒數", 1.0, 10.0, 3.0, 0.5)
else:
    stay_seconds = float(query_params.get("stay", 3.0))

# --- 3. 動態計算每行字元數 ---
N = len(input_text)
cols = min(math.ceil(N / 2), 10) if N > 1 else 1
rows_data = [list(input_text[i:i+cols]) for i in range(0, len(input_text), cols)]
for row in rows_data:
    while len(row) < cols: row.append(" ")

# --- 4. 生成 HTML ---
html_code = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    :root {{
        --unit-width: calc(min(75px, 94vw / {cols} - 6px));
        --unit-height: calc(var(--unit-width) * 1.5);
        --font-size: calc(var(--unit-width) * 1.05);
        --card-bg: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%);
    }}
    body {{ background: transparent; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; overflow: hidden; cursor: pointer; user-select: none; }}
    
    .board-row {{ display: grid; grid-template-columns: repeat({cols}, var(--unit-width)); gap: 8px; perspective: 2000px; }}
    .flap-unit {{ position: relative; width: var(--unit-width); height: var(--unit-height); background: #000; border-radius: 6px; font-family: 'Noto Sans TC', sans-serif; font-size: var(--font-size); font-weight: 900; color: #f0f0f0; }}
    
    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center; 
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }}
    /* 核心修正：上半部多給 1px 高度蓋過軸心縫隙，並使用絕對定位對齊文字 */
    .top {{ top: 0; height: calc(50% + 1px); align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 0.5px solid rgba(0,0,0,0.5); }}
    .bottom {{ bottom: 0; height: 50%; align-items: flex-end; border-radius: 0 0 6px 6px; }}
    
    .text {{ 
        height: var(--unit-height); width: 100%; text-align: center; 
        position: absolute; left: 0;
        line-height: var(--unit-height); /* 確保行高與總高度一致 */
    }}
    .top .text {{ top: 0; }}
    .bottom .text {{ bottom: 0; }}

    .leaf {{ 
        position: absolute; top: 0; left: 0; width: 100%; height: 50%; 
        z-index: 15; transform-origin: bottom; 
        transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1.2); 
        transform-style: preserve-3d;
    }}
    .leaf-front {{ z-index: 16; background: var(--card-bg); }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #1a1a1a; display: flex; justify-content: center; align-items: flex-end; overflow: hidden;}}
    .flipping {{ transform: rotateX(-180deg); }}

    .flap-unit::before {{
        content: ""; position: absolute; top: 50%; left: -1px; width: calc(100% + 2px); height: 2px;
        background: rgba(0,0,0,0.8); transform: translateY(-50%); z-index: 60;
    }}
</style>
</head>
<body>
<div id="board-container" class="board-row"></div>

<script>
    const allRows = {rows_data};
    const stayTime = {stay_seconds} * 1000;
    let currentRowIndex = 0;
    let isAnimating = false;
    let autoTimer = null;

    function createRow(contentArray) {{
        return contentArray.map(char => `
            <div class="flap-unit">
                <div class="half top base-top"><div class="text">${{char}}</div></div>
                <div class="half bottom base-bottom"><div class="text">${{char}}</div></div>
                <div class="leaf">
                    <div class="half top leaf-front"><div class="text">${{char}}</div></div>
                    <div class="half bottom leaf-back"><div class="text">${{char}}</div></div>
                </div>
            </div>
        `).join('');
    }}

    function init() {{
        document.getElementById('board-container').innerHTML = createRow(allRows[0]);
        resetTimer();
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
                
                // 動畫開始前：換掉底座上半部和葉片背面
                u.querySelector('.base-top .text').innerText = nextChars[i];
                u.querySelector('.leaf-back .text').innerText = nextChars[i];
                
                leaf.classList.add('flipping');

                leaf.addEventListener('transitionend', function onEnd() {{
                    leaf.removeEventListener('transitionend', onEnd);
                    
                    // 動畫結束：補上底座下半部和葉片正面
                    u.querySelector('.base-bottom .text').innerText = nextChars[i];
                    u.querySelector('.leaf-front .text').innerText = nextChars[i];
                    
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    leaf.offsetHeight; 
                    leaf.style.transition = '';
                    
                    if (i === units.length - 1) {{
                        isAnimating = false;
                        resetTimer();
                    }}
                }}, {{once: true}});
            }}, i * 40);
        }});

        currentRowIndex = nextRowIndex;
    }}

    function resetTimer() {{
        if (autoTimer) clearInterval(autoTimer);
        autoTimer = setInterval(performFlip, stayTime);
    }}

    document.body.addEventListener('click', () => {{
        if (!isAnimating) performFlip();
    }});

    init();
</script>
</body>
</html>
"""

components.html(html_code, height=300)
