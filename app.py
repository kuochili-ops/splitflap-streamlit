import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Pro", layout="centered")

st.title("📟 物理翻板：最終校正版")
st.caption("修正了文字拆解錯誤。點擊看板：上板下翻切換訊息。")

user_input = st.text_input("輸入句子 (系統自動平分)", "謝謝光臨歡迎再來")

if user_input:
    # 邏輯：平分文字 (確保轉為 List 處理中文字元)
    chars = list(user_input)
    mid = math.ceil(len(chars) / 2)
    t1 = chars[:mid]
    t2 = chars[mid:]
    
    # 補齊長度
    max_len = max(len(t1), len(t2))
    text1 = "".join(t1).ljust(max_len, " ")
    text2 = "".join(t2).ljust(max_len, " ")

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
            gap: 12px;
            perspective: 1200px;
            cursor: pointer;
            justify-content: center;
        }}

        .flap-unit {{
            position: relative;
            width: 70px;
            height: 100px;
            background-color: #1a1a1a;
            border-radius: 6px;
            font-family: 'Noto Sans TC', sans-serif;
            font-size: 60px;
            font-weight: 900;
            color: #ffffff;
        }}

        /* 核心定位：確保上下對齊 */
        .part {{
            position: absolute;
            left: 0;
            width: 100%;
            height: 50%;
            overflow: hidden;
            background: #1a1a1a;
            backface-visibility: hidden;
            display: flex;
            justify-content: center;
        }}

        .top {{
            top: 0;
            align-items: flex-start;
            line-height: 100px; /* 文字的上半部 */
            border-radius: 6px 6px 0 0;
            border-bottom: 1px solid rgba(0,0,0,0.6);
        }}

        .bottom {{
            bottom: 0;
            align-items: flex-end;
            line-height: 0px; /* 文字的下半部 */
            border-radius: 0 0 6px 6px;
        }}

        /* 翻動葉片層 */
        .leaf {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 50%;
            z-index: 5;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            transform-origin: bottom;
        }}

        /* 葉片正面 (舊字上半) */
        .leaf-front {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: #1a1a1a;
            backface-visibility: hidden;
            z-index: 2;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            line-height: 100px;
            border-radius: 6px 6px 0 0;
        }}

        /* 葉片背面 (新字下半) */
        .leaf-back {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: #1a1a1a;
            backface-visibility: hidden;
            transform: rotateX(-180deg);
            z-index: 1;
            display: flex;
            justify-content: center;
            align-items: flex-end;
            line-height: 0px;
            border-radius: 0 0 6px 6px;
        }}

        /* 狀態切換 */
        .flipped .leaf {{
            transform: rotateX(-180deg);
        }}

        /* 裝飾線 */
        .flap-unit::after {{
            content: "";
            position: absolute;
            top: 50%; left: 0; width: 100%; height: 2px;
            background: rgba(0,0,0,0.9);
            z-index: 10;
        }}
    </style>
    </head>
    <body>

    <div class="board" id="board"></div>

    <script>
        const s1 = Array.from("{text1}");
        const s2 = Array.from("{text2}");
        const board = document.getElementById('board');

        function init() {{
            board.innerHTML = '';
            s1.forEach((char, i) => {{
                const targetChar = s2[i];
                const unit = document.createElement('div');
                unit.className = 'flap-unit';
                
                // 結構說明：
                // top: 顯示 s2 的上半 (新)
                // bottom: 顯示 s1 的下半 (舊)
                // leaf-front: 顯示 s1 的上半 (舊 - 翻下去)
                // leaf-back: 顯示 s2 的下半 (新 - 翻下來覆蓋)
                unit.innerHTML = `
                    <div class="part top">${{targetChar}}</div>
                    <div class="part bottom">${{char}}</div>
                    <div class="leaf">
                        <div class="leaf-front">${{char}}</div>
                        <div class="leaf-back">${{targetChar}}</div>
                    </div>
                `;
                board.appendChild(unit);
            }});
        }}

        function doFlip() {{
            const boardObj = document.getElementById('board');
            const units = document.querySelectorAll('.flap-unit');
            
            // 判斷當前是否已翻轉，實現來回切換
            const isFlipped = boardObj.classList.contains('is-flipped');
            
            units.forEach((unit, i) => {{
                setTimeout(() => {{
                    if (!isFlipped) {{
                        unit.classList.add('flipped');
                    }} else {{
                        unit.classList.remove('flipped');
                    }}
                }}, i * 50);
            }});

            boardObj.classList.toggle('is-flipped');
        }}

        init();
        board.addEventListener('click', doFlip);
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=400)
