import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Ultimate Texture", layout="centered")

# --- 文字處理 ---
input_text = st.text_input("輸入句子", "黃千凌是我今生的最愛")
chars = list(input_text)
# 分段邏輯 (可根據需求微調)
mid = math.ceil(len(chars) / 2)
s1, s2 = chars[:mid], chars[mid:]
max_l = max(len(s1), len(s2))
s1 += [" "] * (max_l - len(s1))
s2 += [" "] * (max_l - len(s2))

html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    
    :root {{
        --unit-width: calc(min(70px, 92vw / {max_l} - 8px));
        --unit-height: calc(var(--unit-width) * 1.5);
        --font-size: calc(var(--unit-width) * 0.85);
        --anim-speed: 0.5s;
    }}

    body {{ background: transparent; display: flex; justify-content: center; padding: 40px 0; margin: 0; overflow: hidden; }}
    
    .board {{ display: grid; grid-template-columns: repeat({max_l}, var(--unit-width)); gap: 6px; perspective: 2000px; }}

    .flap-unit {{ 
        position: relative; width: var(--unit-width); height: var(--unit-height); 
        background: #111; border-radius: 4px; 
        font-family: 'Noto Sans TC', sans-serif; font-size: var(--font-size); font-weight: 900; color: #fff;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }}

    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; 
        overflow: hidden; background: linear-gradient(180deg, #222 0%, #1a1a1a 100%); 
        display: flex; justify-content: center; 
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }}

    .top {{ top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 1px solid #000; }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; }}
    .text {{ height: var(--unit-height); line-height: var(--unit-height); text-align: center; width: 100%; }}

    .leaf {{ 
        position: absolute; top: 0; left: 0; width: 100%; height: 50%; 
        z-index: 10; transform-origin: bottom; 
        transition: transform var(--anim-speed) cubic-bezier(0.68, -0.1, 0.26, 1.3); /* 加入回彈曲線 */
        transform-style: preserve-3d;
        will-change: transform;
    }}

    .leaf-front {{ z-index: 11; background: linear-gradient(180deg, #252525 0%, #1a1a1a 100%); }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 10; background: #1a1a1a; }}
    .flipping {{ transform: rotateX(-180deg); }}

    /* 物理陰影遮罩 */
    .shadow {{
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0); transition: background var(--anim-speed);
        z-index: 12; pointer-events: none;
    }}
    .flipping .shadow {{ background: rgba(0,0,0,0.6); }}

    .flap-unit::after {{
        content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
        background: #000; transform: translateY(-50%) translateZ(15px); z-index: 50;
    }}
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
            <div class="flap-unit" id="unit-${{i}}">
                <div class="half top base-top"><div class="text">${{c}}</div></div>
                <div class="half bottom base-bottom"><div class="text">${{c}}</div></div>
                <div class="leaf">
                    <div class="half top leaf-front"><div class="text">${{c}}</div><div class="shadow"></div></div>
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
            // 加入隨機微延遲，模擬機械真實感
            const randomDelay = i * 50 + (Math.random() * 20);
            
            setTimeout(() => {{
                const leaf = u.querySelector('.leaf');
                u.querySelector('.base-top .text').innerText = nextArr[i];
                u.querySelector('.leaf-back .text').innerText = nextArr[i];

                leaf.classList.add('flipping');

                const finalize = () => {{
                    leaf.removeEventListener('transitionend', finalize);
                    u.querySelector('.base-bottom .text').innerText = nextArr[i];
                    u.querySelector('.leaf-front .text').innerText = nextArr[i];
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    leaf.offsetHeight; 
                    leaf.style.transition = '';

                    if (i === units.length - 1) {{
                        currentIsA = !currentIsA;
                        isAnimating = false;
                    }}
                }};
                leaf.addEventListener('transitionend', finalize);
            }}, randomDelay);
        }});
    }}

    document.body.addEventListener('click', flip);
    init();
</script>
</body>
</html>
"""

components.html(html_code, height=400)
