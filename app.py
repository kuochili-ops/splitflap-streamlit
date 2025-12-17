import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Ultra Smooth", layout="centered")

# --- 文字處理 ---
raw_input = st.text_input("輸入句子", "黃千凌是我今生的最愛")
chars = list(raw_input)
mid = math.ceil(len(chars) / 2)
s1, s2 = chars[:mid], chars[mid:]
max_l = max(len(s1), len(s2))
s1 += [" "] * (max_l - len(s1))
s2 += [" "] * (max_l - len(s2))

# 將資料轉為 JS 可讀格式
s1_js = str(s1)
s2_js = str(s2)

html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    
    :root {{
        /* 根據字數自動計算寬度，確保不超出手機螢幕 */
        --unit-width: calc(min(68px, 90vw / {max_l} - 10px));
        --unit-height: calc(var(--unit-width) * 1.47);
        --font-size: calc(var(--unit-width) * 0.76);
    }}

    body {{ 
        background: transparent; 
        display: flex; 
        justify-content: center; 
        padding: 20px 0; 
        margin: 0;
        overflow: hidden;
    }}
    
    .board {{ 
        display: grid; 
        grid-template-columns: repeat({max_l}, var(--unit-width)); 
        gap: clamp(4px, 1vw, 12px); 
        perspective: 2000px; 
    }}

    .flap-unit {{ 
        position: relative; 
        width: var(--unit-width); 
        height: var(--unit-height); 
        background: #111; 
        border-radius: 4px; 
        font-family: 'Noto Sans TC', sans-serif; 
        font-size: var(--font-size); 
        font-weight: 900; 
        color: #fff;
    }}

    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; 
        overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; 
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }}

    .top {{ top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 1px solid #000; }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; }}
    .text {{ height: var(--unit-height); line-height: var(--unit-height); text-align: center; width: 100%; }}

    .base-top {{ z-index: 1; }} 
    .base-bottom {{ z-index: 2; }}

    .leaf {{ 
        position: absolute; top: 0; left: 0; width: 100%; height: 50%; 
        z-index: 10; transform-origin: bottom; 
        transition: transform 0.45s cubic-bezier(0.4, 0, 0.2, 1);
        transform-style: preserve-3d;
        will-change: transform;
    }}

    .leaf-front {{ z-index: 11; }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 10; }}
    .flipping {{ transform: rotateX(-180deg); }}

    .flap-unit::after {{
        content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 1.5px;
        background: rgba(0,0,0,0.9); transform: translateY(-50%) translateZ(10px); z-index: 50;
    }}
</style>
</head>
<body>
<div class="board" id="board"></div>

<script>
    const tA = {s1_js}, tB = {s2_js};
    let currentIsA = true;
    let isAnimating = false;

    function init() {{
        document.getElementById('board').innerHTML = tA.map((c, i) => `
            <div class="flap-unit" id="unit-${{i}}">
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
            // 降低間隔時間讓動作更連貫
            setTimeout(() => {{
                const leaf = u.querySelector('.leaf');
                
                // 1. 準備背景內容
                u.querySelector('.base-top .text').innerText = nextArr[i];
                u.querySelector('.leaf-back .text').innerText = nextArr[i];

                // 2. 執行翻轉
                leaf.classList.add('flipping');

                // 3. 使用一次性事件處理
                const finalize = () => {{
                    leaf.removeEventListener('transitionend', finalize);
                    
                    // 同步目前可見的面
                    u.querySelector('.base-bottom .text').innerText = nextArr[i];
                    u.querySelector('.leaf-front .text').innerText = nextArr[i];
                    
                    // 瞬間歸位 (不觸發動畫)
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    
                    // 強制重繪後恢復動畫屬性
                    leaf.offsetHeight; 
                    leaf.style.transition = '';

                    if (i === units.length - 1) {{
                        currentIsA = !currentIsA;
                        isAnimating = false;
                    }}
                }};
                leaf.addEventListener('transitionend', finalize);
            }}, i * 45); 
        }});
    }}

    document.body.addEventListener('click', flip);
    init();
</script>
</body>
</html>
"""

components.html(html_code, height=450)
