import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Final Fix", layout="centered")

st.title("📟 物理翻板：最終物理修復版")
st.caption("修正翻轉葉片懸空與字體拼合問題。點擊看板切換。")

user_input = st.text_input("輸入句子", "謝謝光臨歡迎再來")

if user_input:
    # 邏輯：精確平分
    full_text = list(user_input)
    mid = math.ceil(len(full_text) / 2)
    t1 = full_text[:mid]
    t2 = full_text[mid:]
    
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
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            perspective: 1500px;
            cursor: pointer;
            justify-content: center;
        }}

        .flap-unit {{
            position: relative;
            width: 70px;
            height: 100px;
            background-color: #111;
            border-radius: 6px;
            font-family: 'Noto Sans TC', sans-serif;
            font-size: 60px;
            font-weight: 900;
            color: #fff;
            user-select: none;
        }}

        /* 靜態底座 */
        .base-half {{
            position: absolute;
            left: 0; width: 100%; height: 50%;
            overflow: hidden;
            background: #1a1a1a;
            display: flex;
            justify-content: center;
        }}
        .base-top {{ top: 0; border-radius: 6px 6px 0 0; align-items: flex-start; border-bottom: 1px solid #000; }}
        .base-bottom {{ bottom: 0; border-radius: 0 0 6px 6px; align-items: flex-end; }}

        /* 翻動葉片容器 */
        .flap-leaf {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 50%;
            z-index: 10;
            transform-origin: bottom;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            transform-style: preserve-3d;
        }}

        /* 葉片正反面：強制填滿半格 */
        .leaf-side {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            overflow: hidden;
            backface-visibility: hidden;
            display: flex;
            justify-content: center;
            background: #1a1a1a;
        }}

        .leaf-front {{ 
            z-index: 2; 
            align-items: flex-start;
            border-radius: 6px 6px 0 0;
            border-bottom: 1px solid #000;
        }}
        
        .leaf-back {{ 
            transform: rotateX(-180deg); 
            align-items: flex-end;
            border-radius: 0 0 6px 6px;
        }}

        /* 文字渲染層：精確高度確保對齊 */
        .text {{
            height: 100px;
            line-height: 100px;
            text-align: center;
        }}

        /* 翻轉狀態 */
        .flipped .flap-leaf {{
            transform: rotateX(-180deg);
        }}

        .flap-unit::after {{
            content: "";
            position: absolute;
            top: 50%; left: 0; width: 100%; height: 2px;
            background: rgba(0,0,0,0.8);
            z-index: 20;
        }}
    </style>
    </head>
    <body>

    <div class="board" id="board"></div>

    <script>
        const s1 = {t1};
        const s2 = {t2};
        const board = document.getElementById('board');

        function init() {{
            s1.forEach((char1, i) => {{
                const char2 = s2[i];
                const unit = document.createElement('div');
                unit.className = 'flap-unit';
                
                // 結構：
                // base-top: 新字上半 (目標)
                // base-bottom: 舊字下半 (起始) -> 這裡也要放新字下半，只是被遮住
                // leaf-front: 舊字上半 (起始)
                // leaf-back: 新字下半 (目標)
                unit.innerHTML = `
                    <div class="base-half base-top"><div class="text">${{char2}}</div></div>
                    <div class="base-half base-bottom"><div class="text">${{char2}}</div></div>
                    <div class="flap-leaf">
                        <div class="leaf-side leaf-front"><div class="text">${{char1}}</div></div>
                        <div class="leaf-side leaf-back"><div class="text">${{char1}}</div></div>
                    </div>
                `;
                board.appendChild(unit);
            }});
        }}

        board.addEventListener('click', () => {{
            const units = document.querySelectorAll('.flap-unit');
            const isFlipped = board.classList.contains('is-flipped');
            units.forEach((u, i) => {{
                setTimeout(() => {{
                    if(!isFlipped) u.classList.add('flipped');
                    else u.classList.remove('flipped');
                }}, i * 50);
            }});
            board.classList.toggle('is-flipped');
        }});

        init();
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=450)
