import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Pro", layout="centered")

st.title("📟 物理翻板：雙向無縫版")
st.caption("無論從 A 到 B 還是從 B 到 A，都擁有完整的物理加速與墮落動態。")

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
            backface-visibility: hidden; -webkit-backface-visibility: hidden;
        }}
        .top {{ top: 0; align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 1px solid #000; }}
        .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 6px 6px; }}
        .text {{ height: 100px; line-height: 100px; text-align: center; }}

        /* --- 靜態底座：固定在最深處 --- */
        .base-t2 {{ transform: translateZ(0px); z-index: 1; }} /* 只有 A 翻下後才看得到它 */
        .base-t1 {{ transform: translateZ(0px); z-index: 1; }} /* 只有 B 翻下後才看得到它 */

        /* --- 雙向葉片結構 --- */
        
        /* 葉片 A (由 A 翻向 B) */
        .leaf-a {{
            position: absolute; top: 0; left: 0; width: 100%; height: 50%;
            transform-origin: bottom; z-index: 10;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            transform: translateZ(2px) rotateX(0deg);
        }}
        /* 葉片 B (由 B 翻向 A) */
        .leaf-b {{
            position: absolute; top: 50%; left: 0; width: 100%; height: 50%;
            transform-origin: top; z-index: 5;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            transform: translateZ(2px) rotateX(180deg);
        }}

        /* 狀態 1: A -> B */
        .to-b .leaf-a {{ transform: translateZ(2px) rotateX(-180deg); z-index: 5; }}
        .to-b .leaf-b {{ transform: translateZ(2px) rotateX(0deg); z-index: 10; }}

        /* 狀態 2: B -> A (即還原) */
        /* transition 會自動處理反向動畫，無需額外類別 */

        .flap-unit::after {{
            content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
            background: #000; transform: translateY(-50%) translateZ(10px); z-index: 20;
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
                <div class="half top base-t2"><div class="text">${{s2[i]}}</div></div>
                <div class="half bottom base-t1"><div class="text">${{charA}}</div></div>
                
                <div class="half top leaf-a"><div class="text">${{charA}}</div></div>
                <div class="half bottom leaf-b"><div class="text">${{s2[i]}}</div></div>
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
                }}, i * 70);
            }});
        }});
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=450)
