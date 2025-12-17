import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Silk Smooth", layout="centered")

# --- 文字處理 ---
raw_input = st.text_input("輸入句子", "黃千凌是我今生的最愛")
chars = list(raw_input)
mid = math.ceil(len(chars) / 2)
s1, s2 = chars[:mid], chars[mid:]
max_l = max(len(s1), len(s2))
s1 += [" "] * (max_l - len(s1))
s2 += [" "] * (max_l - len(s2))

html_code = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    body {{ background: transparent; display: flex; flex-direction: column; align-items: center; padding: 20px 0; overflow: hidden; }}
    
    .board {{ 
        display: grid; 
        grid-template-columns: repeat({max_l}, 72px); 
        gap: 12px; 
        perspective: 2500px; 
    }}

    .flap-unit {{ 
        position: relative; width: 68px; height: 100px; 
        background: #111; border-radius: 4px; 
        font-family: 'Noto Sans TC', sans-serif; font-size: 52px; font-weight: 900; color: #fff;
    }}

    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; 
        overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; 
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }}

    .top {{ top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 1px solid #000; }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; }}
    .text {{ height: 100px; line-height: 100px; text-align: center; width: 100%; }}

    .base-top {{ z-index: 1; }} 
    .base-bottom {{ z-index: 2; }}

    .leaf {{ 
        position: absolute; top: 0; left: 0; width: 100%; height: 50%; 
        z-index: 10; transform-origin: bottom; 
        transition: transform 0.5s cubic-bezier(0.35, 0, 0.25, 1);
        transform-style: preserve-3d;
        will-change: transform; /* 硬體加速關鍵 */
    }}

    .leaf-front {{ z-index: 11; }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 10; }}
    .flipping {{ transform: rotateX(-180deg); }}

    /* 中間裝飾細線 */
    .flap-unit::after {{
        content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 1px;
        background: rgba(0,0,0,0.6); transform: translateY(-50%) translateZ(30px); z-index: 50;
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
                    <div class="half top leaf-front"><div class="text">${{c}}</div></div>
                    <div class="half bottom leaf-back"><div class="text">${{c}}</div></div>
                </div>
            </div>`).join('');
    }}

    async function flip() {{
        if (isAnimating) return;
        isAnimating = true;

        const units = document.querySelectorAll('.flap-unit');
        const nextArr = currentIsA ? tB : tA;

        for (let i = 0; i < units.length; i++) {{
            const u = units[i];
            const leaf = u.querySelector('.leaf');
            
            // 延遲發動，營造波浪效果
            setTimeout(() => {{
                // 翻轉前準備
                u.querySelector('.base-top .text').innerText = nextArr[i];
                u.querySelector('.leaf-back .text').innerText = nextArr[i];

                leaf.classList.add('flipping');

                const onEnd = () => {{
                    leaf.removeEventListener('transitionend', onEnd);
                    
                    // 瞬間更換所有面為新字
                    u.querySelector('.base-bottom .text').innerText = nextArr[i];
                    u.querySelector('.leaf-front .text').innerText = nextArr[i];
                    
                    // 靜默重置，使用 requestAnimationFrame 確保流暢
                    requestAnimationFrame(() => {{
                        leaf.style.transition = 'none';
                        leaf.classList.remove('flipping');
                        
                        u.querySelector('.base-top .text').innerText = nextArr[i];
                        u.querySelector('.leaf-back .text').innerText = nextArr[i];

                        requestAnimationFrame(() => {{
                            leaf.style.transition = '';
                        }});
                    }});

                    if (i === units.length - 1) {{
                        currentIsA = !currentIsA;
                        isAnimating = false;
                    }}
                }};
                leaf.addEventListener('transitionend', onEnd);
            }}, i * 60);
        }}
    }}

    document.body.addEventListener('click', flip);
    init();
</script>
</body>
</html>
"""

components.html(html_code, height=600)
