import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Dual Guard", layout="centered")

st.title("📟 物理翻板：雙重保險版")
st.caption("結合 3D 空間位移與內容鎖定，徹底解決手機瀏覽器亂碼問題。")

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
            display: flex; flex-wrap: wrap; gap: 10px; perspective: 2000px; justify-content: center;
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

        /* --- 核心：保險機制 --- */

        /* 初始狀態：隱藏所有後半句(目標)文字 */
        .base-new-top .text, 
        .base-new-bottom .text, 
        .leaf-back .text {{
            opacity: 0;
            transition: opacity 0.1s;
        }}

        /* 翻轉啟動後才顯現目標文字 */
        .flipping .base-new-top .text, 
        .flipping .base-new-bottom .text, 
        .flipping .leaf-back .text {{
            opacity: 1;
        }}

        /* 空間深度隔離 */
        .base-new-top {{ transform: translateZ(-2px); }}
        .base-new-bottom {{ transform: translateZ(-2px); }}
        .base-old-bottom {{ transform: translateZ(1px); }}

        .leaf {{
            position: absolute; top: 0; left: 0; width: 100%; height: 50%;
            transform-origin: bottom;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            transform-style: preserve-3d;
            transform: translateZ(5px);
            z-index: 10;
        }}
        
        .leaf-front {{ transform: translateZ(0.1px); }}
        .leaf-back {{ transform: rotateX(-180deg) translateZ(0.1px); }}

        /* 旋轉狀態 */
        .is-active .leaf {{ transform: translateZ(5px) rotateX(-180deg); }}

        .flap-unit::after {{
            content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
            background: #000; transform: translateY(-50%) translateZ(6px); z-index: 20;
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
                    <div class="half bottom base-new-bottom"><div class="text">${{to[i]}}</div></div>
                    <div class="half bottom base-old-bottom"><div class="text">${{char1}}</div></div>
                    <div class="leaf">
                        <div class="half top leaf-front"><div class="text">${{char1}}</div></div>
                        <div class="half bottom leaf-back"><div class="text">${{to[i]}}</div></div>
                    </div>
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
                    // 同步開啟透明度與旋轉動畫
                    u.classList.add('flipping');
                    u.classList.add('is-active');
                }}, i * 70);
            }});
        }});
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=450)
