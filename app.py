import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Clockwork", layout="centered")

st.title("📟 物理翻板：極致流暢版")
st.caption("使用時鐘擺動邏輯，徹底解決回程亂碼與閃爍問題。")

user_input = st.text_input("輸入句子", "往事就是我的安慰")

if user_input:
    chars = list(user_input)
    mid = math.ceil(len(chars) / 2)
    t1 = chars[:mid]
    t2 = chars[mid:]
    
    max_len = max(len(t1), len(t2))
    while len(t1) < max_len: t1.append(" ")
    while len(t2) < max_len: t2.append(" ")

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
        body {{ background: transparent; display: flex; justify-content: center; padding: 20px 0; }}
        
        .board {{
            display: flex; flex-wrap: wrap; gap: 10px; perspective: 1500px; justify-content: center;
        }}

        .flap-unit {{
            position: relative; width: 70px; height: 100px;
            background-color: #111; border-radius: 6px;
            font-family: 'Noto Sans TC', sans-serif; font-size: 60px; font-weight: 900; color: #fff;
            transform-style: preserve-3d;
        }}

        .half {{
            position: absolute; left: 0; width: 100%; height: 50%;
            overflow: hidden; background: #1a1a1a; display: flex; justify-content: center;
            /* 強制取消背面隱藏，改用物理順序控制 */
            -webkit-backface-visibility: visible; backface-visibility: visible;
        }}
        .top {{ top: 0; align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 1px solid #000; }}
        .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 6px 6px; }}
        .text {{ height: 100px; line-height: 100px; text-align: center; }}

        /* --- 隔離層級結構 --- */
        
        /* 最底層：新字的上半部 */
        .base-t2-top {{ z-index: 1; transform: translateZ(0px); }}
        /* 次底層：舊字的下半部 */
        .base-t1-bottom {{ z-index: 2; transform: translateZ(1px); }}

        /* 翻轉葉片：前半句的上半部 (0 -> -180) */
        .leaf-old {{
            position: absolute; top: 0; left: 0; width: 100%; height: 50%;
            transform-origin: bottom; z-index: 10;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            transform: translateZ(4px) rotateX(0deg);
        }}

        /* 翻轉葉片：後半句的下半部 (180 -> 0) */
        .leaf-new {{
            position: absolute; top: 50%; left: 0; width: 100%; height: 50%;
            transform-origin: top; z-index: 5;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            transform: translateZ(3px) rotateX(180deg);
        }}

        /* --- 雙向狀態控制 --- */
        
        /* 狀態：翻向 B (後半句) */
        .to-b .leaf-old {{ transform: translateZ(4px) rotateX(-180deg); z-index: 5; opacity: 0; }}
        .to-b .leaf-new {{ transform: translateZ(3px) rotateX(0deg); z-index: 12; opacity: 1; }}

        /* 狀態：翻回 A (前半句) - 預設即是 */

        .flap-unit::after {{
            content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
            background: #000; transform: translateY(-50%) translateZ(15px); z-index: 20;
        }}
    </style>
    </head>
    <body>
    <div class="board" id="board"></div>

    <script>
        const s1 = {t1};
        const s2 = {t2};
        const board = document.getElementById('board');

        board.innerHTML = s1.map((charA, i) => `
            <div class="flap-unit">
                <div class="half top base-t2-top"><div class="text">${{s2[i]}}</div></div>
                <div class="half bottom base-t1-bottom"><div class="text">${{charA}}</div></div>
                
                <div class="half top leaf-old"><div class="text">${{charA}}</div></div>
                <div class="half bottom leaf-new"><div class="text">${{s2[i]}}</div></div>
            </div>
        `).join('');

        let isB = false;
        board.addEventListener('click', () => {{
            isB = !isB;
            const units = document.querySelectorAll('.flap-unit');
            units.forEach((u, i) => {{
                setTimeout(() => {{
                    if (isB) u.classList.add('to-b');
                    else u.classList.remove('to-b');
                }}, i * 60);
            }});
        }});
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=450)
