import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Corrected", layout="centered")

st.title("📟 物理翻板：字元拼合修正版")
st.caption("已解決中文字元組合錯誤問題。點擊看板進行正確翻轉。")

user_input = st.text_input("輸入句子", "謝謝光臨歡迎再來")

if user_input:
    # 平分文字
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
            font-family: 'Noto Sans TC', sans-serif; font-size: 64px; font-weight: 900; color: #fff;
        }}

        /* 通用切片樣式 */
        .side {{
            position: absolute; left: 0; width: 100%; height: 50%;
            overflow: hidden; background: #1a1a1a; display: flex; justify-content: center;
            backface-visibility: hidden; -webkit-backface-visibility: hidden;
        }}

        /* 內容定位：確保上下完全對齊 */
        .text-box {{ height: 100px; line-height: 100px; text-align: center; }}
        .top-side {{ top: 0; align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 1px solid #000; }}
        .bottom-side {{ bottom: 0; align-items: flex-end; border-radius: 0 0 6px 6px; }}
        .bottom-side .text-box {{ transform: translateY(0); display: flex; align-items: flex-end; height: 100%; }}

        /* 1. 底座上半部：顯示「新字」上半 */
        .base-top {{ z-index: 1; }}
        /* 2. 底座下半部：顯示「舊字」下半 */
        .base-bottom {{ z-index: 1; }}

        /* 3. 翻動葉片：關鍵動畫層 */
        .leaf {{
            position: absolute; top: 0; left: 0; width: 100%; height: 50%;
            z-index: 10; transform-origin: bottom;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            transform-style: preserve-3d;
        }}

        /* 葉片正面：顯示「舊字」上半 */
        .leaf-front {{ z-index: 12; }}
        /* 葉片背面：顯示「新字」下半 */
        .leaf-back {{ 
            transform: rotateX(-180deg); z-index: 11; 
            background: #1a1a1a; align-items: flex-end;
        }}

        /* 動態翻轉 */
        .flipped .leaf {{ transform: rotateX(-180deg); }}

        .flap-unit::after {{
            content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
            background: rgba(0,0,0,0.8); z-index: 20;
        }}
    </style>
    </head>
    <body>
    <div class="board" id="board"></div>

    <script>
        const s1 = {t1}; // 舊字 (謝謝光臨)
        const s2 = {t2}; // 新字 (歡迎再來)
        const board = document.getElementById('board');

        function init() {{
            s1.forEach((oldChar, i) => {{
                const newChar = s2[i];
                const unit = document.createElement('div');
                unit.className = 'flap-unit';
                
                // 正確的物理層級：
                // 底座下半部必須先顯示 oldChar，當 leaf 翻下來蓋住它時，顯示的是 leaf-back 的 newChar
                unit.innerHTML = `
                    <div class="side top-side base-top"><div class="text-box">${{newChar}}</div></div>
                    <div class="side bottom-side base-bottom"><div class="text-box">${{oldChar}}</div></div>
                    <div class="leaf">
                        <div class="side top-side leaf-front"><div class="text-box">${{oldChar}}</div></div>
                        <div class="side bottom-side leaf-back"><div class="text-box">${{newChar}}</div></div>
                    </div>
                `;
                board.appendChild(unit);
            }});
        }}

        board.addEventListener('click', () => {{
            const isFlipped = board.classList.contains('active');
            document.querySelectorAll('.flap-unit').forEach((u, i) => {{
                setTimeout(() => {{
                    if(!isFlipped) u.classList.add('flipped');
                    else u.classList.remove('flipped');
                }}, i * 50);
            }});
            board.classList.toggle('active');
        }});

        init();
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=450)
