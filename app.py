import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Natural Split-Flap", layout="centered")

st.title("📟 物理翻板：自然動態版")
st.caption("優化了翻轉曲線與光影效果，讓動作更流暢自然。")

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
            display: flex; flex-wrap: wrap; gap: 12px; perspective: 1500px; justify-content: center;
        }}

        .flap-unit {{
            position: relative; width: 70px; height: 100px;
            background-color: #111; border-radius: 6px;
            font-family: 'Noto Sans TC', sans-serif; font-size: 60px; font-weight: 900; color: #eee;
        }}

        .half {{
            position: absolute; left: 0; width: 100%; height: 50%;
            overflow: hidden; background: #1a1a1a; display: flex; justify-content: center;
            backface-visibility: hidden; -webkit-backface-visibility: hidden;
        }}

        .top {{ top: 0; align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 1px solid #000; }}
        .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 6px 6px; }}

        .text {{ height: 100px; line-height: 100px; text-align: center; }}

        /* 增加光影效果 */
        .top::before {{
            content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(to bottom, rgba(0,0,0,0.3) 0%, transparent 100%); pointer-events: none;
        }}

        /* 翻動葉片：使用更自然的緩動 */
        .leaf {{
            position: absolute; top: 0; left: 0; width: 100%; height: 50%;
            z-index: 10; transform-origin: bottom;
            transition: transform 0.6s cubic-bezier(0.45, 0.05, 0.55, 0.95);
            transform-style: preserve-3d;
        }}

        .leaf-front {{ z-index: 2; border-bottom: 1px solid #000; }}
        .leaf-back {{ 
            transform: rotateX(-180deg); z-index: 1; 
            background: #1a1a1a; /* 確保背面顏色一致 */
        }}

        .flipping {{ transform: rotateX(-180deg); }}

        /* 軸心裝飾 */
        .flap-unit::after {{
            content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
            background: #000; z-index: 20; transform: translateY(-50%);
        }}
    </style>
    </head>
    <body>
    <div class="board" id="board"></div>

    <script>
        const s1 = {t1};
        const s2 = {t2};
        let isT1 = true;

        function render() {{
            const current = isT1 ? s1 : s2;
            const target = isT1 ? s2 : s1;
            
            board.innerHTML = current.map((c, i) => `
                <div class="flap-unit">
                    <div class="half top"><div class="text">${{target[i]}}</div></div>
                    <div class="half bottom"><div class="text">${{c}}</div></div>
                    <div class="leaf">
                        <div class="half top leaf-front"><div class="text">${{c}}</div></div>
                        <div class="half bottom leaf-back"><div class="text">${{target[i]}}</div></div>
                    </div>
                </div>
            `).join('');
        }}

        const board = document.getElementById('board');
        render();

        board.addEventListener('click', () => {{
            const units = document.querySelectorAll('.flap-unit');
            units.forEach((unit, i) => {{
                setTimeout(() => {{
                    unit.querySelector('.leaf').classList.add('flipping');
                }}, i * 60);
            }});

            // 動畫結束後徹底切換狀態
            setTimeout(() => {{
                isT1 = !isT1;
                render();
            }}, 800);
        }});
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=450)
