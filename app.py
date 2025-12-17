import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Absolute Sync", layout="centered")

# --- 文字處理 ---
raw_input = st.text_input("輸入句子", "謝謝光臨歡迎再來")
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
    body {{ background: transparent; display: flex; flex-direction: column; align-items: center; padding: 20px 0; }}
    .board {{ display: grid; grid-template-columns: repeat({max_l}, 72px); gap: 12px; perspective: 2000px; }}
    .flap-unit {{ position: relative; width: 68px; height: 100px; background: #111; border-radius: 4px; font-family: 'Noto Sans TC', sans-serif; font-size: 52px; font-weight: 900; color: #fff; }}
    .half {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: #1a1a1a; display: flex; justify-content: center; backface-visibility: hidden; -webkit-backface-visibility: hidden; }}
    .top {{ top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 1px solid #000; }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; }}
    .text {{ height: 100px; line-height: 100px; text-align: center; width: 100%; }}
    
    .base-top {{ z-index: 1; }} 
    .base-bottom {{ z-index: 2; }}
    .leaf {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 10; transform-origin: bottom; transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }}
    .leaf-front {{ z-index: 11; }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 10; }}
    .flipping {{ transform: rotateX(-180deg); }}
</style>
</head>
<body>
<div class="board" id="board"></div>
<script>
    const tA = {s1}, tB = {s2};
    let currentIsA = true;
    let isAnimating = false;

    // 【關鍵修復】: 初始化時，所有面 (1,2,11,10) 必須全部填充同一個字 A
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
            setTimeout(() => {{
                const leaf = u.querySelector('.leaf');
                
                // 【關鍵修復】: 只有在翻轉那一刻，才把下一個字填入看不到的背面
                u.querySelector('.base-top .text').innerText = nextArr[i];
                u.querySelector('.leaf-back .text').innerText = nextArr[i];

                leaf.classList.add('flipping');

                leaf.addEventListener('transitionend', function handler() {{
                    leaf.removeEventListener('transitionend', handler);
                    
                    // 動畫結束，同步所有面為新字
                    u.querySelector('.base-bottom .text').innerText = nextArr[i];
                    u.querySelector('.leaf-front .text').innerText = nextArr[i];
                    
                    // 瞬間重置
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    
                    // 確保靜態狀態下，預備面也是新字，維持 100% 一致
                    u.querySelector('.base-top .text').innerText = nextArr[i];
                    u.querySelector('.leaf-back .text').innerText = nextArr[i];

                    void leaf.offsetWidth;
                    leaf.style.transition = '';
                    
                    if (i === units.length - 1) {{
                        currentIsA = !currentIsA;
                        isAnimating = false;
                    }}
                }}, {{ once: true }});
            }}, i * 50);
        }});
    }}
    document.body.addEventListener('click', flip);
    init();
</script>
</body>
</html>
"""
components.html(html_code, height=400)
