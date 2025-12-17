import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Ultimate Split-Flap", layout="centered")

st.title("📟 物理翻板：全靜態穩定版")
st.caption("使用純 CSS 物理疊層結構，徹底根絕拼合錯誤與動作閃爍。")

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
        body {{ background: transparent; display: flex; justify-content: center; padding: 20px 0; overflow: hidden; }}
        
        .board {{
            display: flex; flex-wrap: wrap; gap: 10px; perspective: 1000px; justify-content: center;
        }}

        .flap-unit {{
            position: relative; width: 70px; height: 100px;
            background-color: #111; border-radius: 6px;
            font-family: 'Noto Sans TC', sans-serif; font-size: 60px; font-weight: 900; color: #fff;
        }}

        /* 通用半格容器 */
        .half {{
            position: absolute; left: 0; width: 100%; height: 50%;
            overflow: hidden; background: #1a1a1a; display: flex; justify-content: center;
            backface-visibility: hidden; -webkit-backface-visibility: hidden;
        }}
        .top {{ top: 0; align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 1px solid #000; }}
        .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 6px 6px; }}
        .text {{ height: 100px; line-height: 100px; text-align: center; }}

        /* --- 核心四層結構 --- */
        
        /* 1. 最底層下半部：顯示新字的下半 (目標) */
        .base-new-bottom {{ z-index: 1; }}

        /* 2. 底座上半部：顯示新字的上半 (目標) */
        .base-new-top {{ z-index: 2; }}

        /* 3. 靜態覆蓋層：顯示舊字的下半 (起始) */
        /* 當葉片翻下來時，會蓋掉這一層 */
        .base-old-bottom {{ z-index: 3; }}

        /* 4. 動態翻轉葉片 */
        .leaf {{
            position: absolute; top: 0; left: 0; width: 100%; height: 50%;
            z-index: 10; transform-origin: bottom;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            transform-style: preserve-3d;
        }}
        .leaf-front {{ z-index: 12; }} /* 舊字上半部 */
        .leaf-back {{ 
            transform: rotateX(-180deg); z-index: 11; 
            background: #1a1a1a;
        }} /* 新字下半部 */

        /* 狀態切換 */
        .active .leaf {{ transform: rotateX(-180deg); }}
        
        /* 視覺裝飾：轉軸線 */
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
                // 若要往回翻，直接重置 DOM 重新開始，這是最穩定的做法
                isFlipped = false;
                createUnits(s1, s2);
                return;
            }}
            
            isFlipped = true;
            const units = document.querySelectorAll('.flap-unit');
            units.forEach((u, i) => {{
                setTimeout(() => {{
                    u.classList.add('active');
                }}, i * 70);
            }});
        }});
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=450)
