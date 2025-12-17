import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Absolute", layout="centered")

st.title("📟 物理翻板：雙葉片修復版")
st.caption("透過物理分離前半句與後半句的葉片，解決字體上半部消失的問題。")

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
        }}
        .top {{ top: 0; align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 1px solid #000; }}
        .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 6px 6px; }}
        .text {{ height: 100px; line-height: 100px; text-align: center; }}

        /* --- 靜態底座 --- */
        .base-old-bottom {{ transform: translateZ(1px); }}
        .base-new-top {{ transform: translateZ(0px); }}

        /* --- 前半句葉片 (由 0 翻到 -90) --- */
        .leaf-old {{
            position: absolute; top: 0; left: 0; width: 100%; height: 50%;
            transform-origin: bottom;
            z-index: 10;
            transition: transform 0.3s ease-in, opacity 0.01s 0.3s;
            transform: translateZ(5px) rotateX(0deg);
        }}

        /* --- 後半句葉片 (由 90 翻到 0) --- */
        .leaf-new {{
            position: absolute; top: 50%; left: 0; width: 100%; height: 50%;
            transform-origin: top;
            z-index: 11;
            transition: transform 0.3s ease-out 0.3s;
            transform: translateZ(5px) rotateX(90deg);
            opacity: 0;
        }}

        /* 動畫觸發 */
        .is-active .leaf-old {{ transform: translateZ(5px) rotateX(-90deg); opacity: 0; }}
        .is-active .leaf-new {{ transform: translateZ(5px) rotateX(0deg); opacity: 1; }}

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

        function createUnits(from, to) {{
            board.innerHTML = from.map((char1, i) => `
                <div class="flap-unit">
                    <div class="half top base-new-top"><div class="text">${{to[i]}}</div></div>
                    <div class="half bottom base-old-bottom"><div class="text">${{char1}}</div></div>
                    
                    <div class="half top leaf-old"><div class="text">${{char1}}</div></div>
                    
                    <div class="half bottom leaf-new"><div class="text">${{to[i]}}</div></div>
                </div>
            `).join('');
        }}

        createUnits(s1, s2);

        let isFlipped = false;
        board.addEventListener('click', () => {{
            if (isFlipped) {{
                isFlipped = false;
                createUnits(s1, s2);
                return;
            }}
            
            isFlipped = true;
            const units = document.querySelectorAll('.flap-unit');
            units.forEach((u, i) => {{
                setTimeout(() => {{
                    u.classList.add('is-active');
                }}, i * 70);
            }});
        }});
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=450)
