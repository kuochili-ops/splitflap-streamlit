import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Seamless", layout="centered")

st.title("📟 物理翻板：雙向流暢版")
st.caption("現在不論前翻還是後翻，都具備完整的物理墮落動態。")

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

        /* --- 雙向物理結構 --- */
        
        /* 基礎層：固定顯示 B 句上半與 A 句下半 */
        .base-t2 {{ transform: translateZ(0px); }} 
        .base-t1 {{ transform: translateZ(1px); }}

        /* 葉片 A (後半部)：負責從 A 翻到 B */
        .leaf-to-b {{
            position: absolute; top: 0; left: 0; width: 100%; height: 50%;
            transform-origin: bottom; z-index: 10;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            transform: translateZ(4px) rotateX(0deg);
        }}
        .leaf-to-b .back {{ transform: rotateX(-180deg); background: #1a1a1a; }}

        /* 葉片 B (前半部)：負責從 B 翻回 A */
        .leaf-to-a {{
            position: absolute; top: 0; left: 0; width: 100%; height: 50%;
            transform-origin: bottom; z-index: 5;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            transform: translateZ(2px) rotateX(0deg);
        }}
        .leaf-to-a .back {{ transform: rotateX(-180deg); background: #1a1a1a; }}

        /* 動畫狀態 */
        .flipped-to-b .leaf-to-b {{ transform: translateZ(4px) rotateX(-180deg); }}
        .flipped-to-a .leaf-to-a {{ transform: translateZ(2px) rotateX(-180deg); z-index: 12; }}

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
            <div class="flap-unit" id="unit-${{i}}">
                <div class="half top base-t2"><div class="text">${{s2[i]}}</div></div>
                <div class="half bottom base-t1"><div class="text">${{charA}}</div></div>
                
                <div class="leaf-to-a">
                    <div class="half top front"><div class="text">${{s2[i]}}</div></div>
                    <div class="half bottom back"><div class="text">${{charA}}</div></div>
                </div>

                <div class="leaf-to-b">
                    <div class="half top front"><div class="text">${{charA}}</div></div>
                    <div class="half bottom back"><div class="text">${{s2[i]}}</div></div>
                </div>
            </div>
        `).join('');

        let state = "A"; // A or B
        board.addEventListener('click', () => {{
            const units = document.querySelectorAll('.flap-unit');
            
            if (state === "A") {{
                state = "B";
                units.forEach((u, i) => {{
                    setTimeout(() => u.classList.add('flipped-to-b'), i * 70);
                }});
            }} else {{
                state = "A";
                units.forEach((u, i) => {{
                    // 清除去程狀態，並啟動回程動畫
                    setTimeout(() => {{
                        u.classList.remove('flipped-to-b');
                        u.classList.add('flipped-to-a');
                    }}, i * 70);
                }});
                // 動畫結束後重置回程葉片，準備下一次循環
                setTimeout(() => {{
                    units.forEach(u => u.classList.remove('flipped-to-a'));
                }}, 1000 + units.length * 70);
            }}
        }});
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=450)
