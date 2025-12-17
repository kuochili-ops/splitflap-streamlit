import streamlit as st
import streamlit.components.v1 as components
import math

# --- 1. 設置隱藏 UI 的 CSS ---
st.set_page_config(page_title="Flip Board Embed", layout="centered")

st.markdown("""
    <style>
    /* 隱藏頂部導覽列、選單按鈕與頁尾 */
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    /* 移除 Streamlit 預設的上下邊距 */
    .block-container {padding: 0px; margin-top: -20px;}
    /* 隱藏滾動條 */
    body {overflow: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 獲取文字來源 ---
# 優先讀取網址列參數 ?text=...
query_params = st.query_params
url_text = query_params.get("text", "")

# 判斷是否隱藏輸入框 (當網址包含 embed=true 或已經有傳入文字時)
is_embedded = query_params.get("embed", "false").lower() == "true"

if not is_embedded and not url_text:
    input_text = st.text_input("輸入要顯示的句子", "謝謝光臨歡迎再來")
else:
    # 嵌入模式下，直接顯示傳入的文字，若無則顯示預設字
    input_text = url_text if url_text else "歡迎光臨"

# --- 3. 處理文字邏輯 ---
chars = list(input_text)
mid = math.ceil(len(chars) / 2)
s1, s2 = chars[:mid], chars[mid:]
max_l = max(len(s1), len(s2))
s1 += [" "] * (max_l - len(s1))
s2 += [" "] * (max_l - len(s2))

# --- 4. 嵌入完美翻板 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    :root {{
        --unit-width: calc(min(72px, 94vw / {max_l} - 6px));
        --unit-height: calc(var(--unit-width) * 1.5);
        --font-size: calc(var(--unit-width) * 0.85);
        --card-bg: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%);
    }}
    body {{ background: transparent; display: flex; justify-content: center; padding: 20px 0; margin: 0; overflow: hidden; }}
    .board {{ display: grid; grid-template-columns: repeat({max_l}, var(--unit-width)); gap: 6px; perspective: 2000px; }}
    .flap-unit {{ position: relative; width: var(--unit-width); height: var(--unit-height); background: #000; border-radius: 6px; font-family: 'Noto Sans TC', sans-serif; font-size: var(--font-size); font-weight: 900; color: #f0f0f0; }}
    .half {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: var(--card-bg); display: flex; justify-content: center; backface-visibility: hidden; -webkit-backface-visibility: hidden; }}
    .top {{ top: 0; align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 1.5px solid rgba(0,0,0,0.8); }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 6px 6px; }}
    .text {{ height: var(--unit-height); line-height: var(--unit-height); text-align: center; width: 100%; }}
    .leaf {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 15; transform-origin: bottom; transition: transform 0.55s cubic-bezier(0.5, 0, 0.1, 1.25); transform-style: preserve-3d; will-change: transform; }}
    .leaf-front {{ z-index: 16; background: var(--card-bg); }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #1a1a1a; }}
    .flipping {{ transform: rotateX(-180deg); }}
    .flap-unit::before {{ content: ""; position: absolute; top: 50%; left: -2px; width: calc(100% + 4px); height: 4px; background: linear-gradient(180deg, #111, #444, #111); transform: translateY(-50%) translateZ(20px); z-index: 60; border-radius: 2px; }}
</style>
</head>
<body>
<div class="board" id="board"></div>
<script>
    const tA = {s1}, tB = {s2};
    let currentIsA = true;
    let isAnimating = false;

    function init() {{
        document.getElementById('board').innerHTML = tA.map((c, i) => `
            <div class="flap-unit">
                <div class="half top base-top"><div class="text">${{c}}</div></div>
                <div class="half bottom base-bottom"><div class="text">${{c}}</div></div>
                <div class="leaf">
                    <div class="half top leaf-front"><div class="text">${{c}}</div></div>
                    <div class="half bottom leaf-back"><div class="text">${{c}}</div></div>
                </div>
            </div>`).join('');
    }}

    function flip() {{
        if (isAnimating) return;
        isAnimating = true;
        const units = document.querySelectorAll('.flap-unit');
        const nextArr = currentIsA ? tB : tA;
        units.forEach((u, i) => {{
            const delay = 40 * i + (Math.random() * 15);
            setTimeout(() => {{
                const leaf = u.querySelector('.leaf');
                u.querySelector('.base-top .text').innerText = nextArr[i];
                u.querySelector('.leaf-back .text').innerText = nextArr[i];
                leaf.classList.add('flipping');
                const onComplete = () => {{
                    leaf.removeEventListener('transitionend', onComplete);
                    u.querySelector('.base-bottom .text').innerText = nextArr[i];
                    u.querySelector('.leaf-front .text').innerText = nextArr[i];
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    leaf.offsetHeight; 
                    u.querySelector('.base-top .text').innerText = nextArr[i];
                    u.querySelector('.leaf-back .text').innerText = nextArr[i];
                    leaf.style.transition = '';
                    if (i === units.length - 1) {{ currentIsA = !currentIsA; isAnimating = false; }}
                }};
                leaf.addEventListener('transitionend', onComplete);
            }}, delay);
        }});
    }}
    document.body.addEventListener('click', flip);
    init();
</script>
</body>
</html>
"""

components.html(html_code, height=350)
