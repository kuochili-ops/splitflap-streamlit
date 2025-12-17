import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Final Fix", layout="centered")

st.title("📟 物理翻板：字元拼合終極版")
st.caption("修正了中文字元上下組合錯誤。點擊看板切換前後半句。")

user_input = st.text_input("輸入句子", "謝謝光臨歡迎再來")

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
            display: flex; flex-wrap: wrap; gap: 10px; perspective: 1000px; justify-content: center;
        }}

        .flap-unit {{
            position: relative; width: 70px; height: 100px;
            background-color: #1a1a1a; border-radius: 6px;
            font-family: 'Noto Sans TC', sans-serif; font-size: 60px; font-weight: 900; color: #fff;
        }}

        /* 絕對精準裁切 */
        .half {{
            position: absolute; left: 0; width: 100%; height: 50%;
            overflow: hidden; background: #1a1a1a; display: flex; justify-content: center;
            backface-visibility: hidden; -webkit-backface-visibility: hidden;
        }}

        .top {{ top: 0; align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 1px solid #000; }}
        .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 6px 6px; }}

        /* 文字容器強制對齊 */
        .text {{ height: 100px; line-height: 100px; text-align: center; }}

        /* 翻轉葉片 */
        .leaf {{
            position: absolute; top: 0; left: 0; width: 100%; height: 50%;
            z-index: 10; transform-origin: bottom;
            transition: transform 0.5s ease-in;
            transform-style: preserve-3d;
        }}

        .leaf-front {{ z-index: 2; }}
        .leaf-back {{ transform: rotateX(-180deg); z-index: 1; }}

        /* 動畫類別 */
        .flipping {{ transform: rotateX(-180deg); }}

        .flap-unit::after {{
            content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
            background: rgba(0,0,0,0.8); z-index: 20;
        }}
    </style>
    </head>
    <body>
    <div class="board" id="board"></div>

    <script>
        const s1 = {t1};
        const s2 = {t2};
        let currentText = s1;
        let isAnimating = false;

        function createHTML(chars) {{
            return chars.map(char => `
                <div class="flap-unit">
                    <div class="half top"><div class="text">${{char}}</div></div>
                    <div class="half bottom"><div class="text">${{char}}</div></div>
                    <div class="leaf">
                        <div class="half top leaf-front"><div class="text">${{char}}</div></div>
                        <div class="half bottom leaf-back"><div class="text">${{char}}</div></div>
                    </div>
                </div>
            `).join('');
        }}

        const board = document.getElementById('board');
        board.innerHTML = createHTML(s1);

        board.addEventListener('click', () => {{
            if (isAnimating) return;
            isAnimating = true;

            const nextText = (currentText === s1) ? s2 : s1;
            const units = document.querySelectorAll('.flap-unit');

            units.forEach((unit, i) => {{
                setTimeout(() => {{
                    const leaf = unit.querySelector('.leaf');
                    const leafBackText = leaf.querySelector('.leaf-back .text');
                    const topBaseText = unit.querySelector('.top .text');

                    // 1. 準備：將葉片背面和底座上半部預設為「新字」
                    leafBackText.innerText = nextText[i];
                    topBaseText.innerText = nextText[i];

                    // 2. 開始下翻
                    leaf.classList.add('flipping');

                    // 3. 關鍵：翻到一半時，把底座下半部也換成「新字」
                    setTimeout(() => {{
                        unit.querySelector('.bottom .text').innerText = nextText[i];
                    }}, 250);

                    // 4. 動畫結束，重置 DOM 結構確保穩定
                    if (i === units.length - 1) {{
                        setTimeout(() => {{
                            board.innerHTML = createHTML(nextText);
                            currentText = nextText;
                            isAnimating = false;
                        }}, 550);
                    }}
                }}, i * 50);
            }});
        });
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=450)
