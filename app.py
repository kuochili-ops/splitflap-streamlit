import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Perfect", layout="centered")

st.title("📟 完美物理翻板")
st.caption("點擊看板，體驗正確的「上板下翻」物理變換")

user_input = st.text_input("輸入句子", "今晚想來點 鼎泰豐小籠包")

if user_input:
    # 邏輯：平分文字
    total_len = len(user_input)
    split_point = math.ceil(total_len / 2)
    t1 = user_input[:split_point]
    t2 = user_input[split_point:]
    
    max_len = max(len(t1), len(t2))
    text1 = t1.ljust(max_len, " ")
    text2 = t2.ljust(max_len, " ")

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@700&display=swap');
        
        body {{ background: transparent; display: flex; justify-content: center; padding: 20px 0; }}
        
        .board {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            perspective: 1000px;
            cursor: pointer;
        }}

        .flap-unit {{
            position: relative;
            width: 60px;
            height: 90px;
            background-color: #1a1a1a;
            border-radius: 6px;
            font-family: 'Noto Sans TC', sans-serif;
            font-size: 50px;
            font-weight: bold;
            color: #efefef;
        }}

        /* 共通設定：將字體定位在中間，透過 overflow 切割 */
        .base-top, .base-bottom, .leaf-front, .leaf-back {{
            position: absolute;
            left: 0;
            width: 100%;
            height: 50%;
            overflow: hidden;
            background: #1a1a1a;
            backface-visibility: hidden;
            text-align: center;
        }}

        /* 上半截的文字定位 */
        .base-top, .leaf-front {{
            top: 0;
            line-height: 90px;
            border-radius: 6px 6px 0 0;
            z-index: 1;
        }}

        /* 下半截的文字定位 */
        .base-bottom, .leaf-back {{
            bottom: 0;
            line-height: 0px; /* 讓字體往上飄，露出下半截 */
            border-radius: 0 0 6px 6px;
            z-index: 0;
        }}

        /* 翻轉葉片：關鍵在於 transform-origin 在底部 */
        .leaf-front {{
            z-index: 3;
            transition: transform 0.6s ease-in;
            transform-origin: bottom;
            border-bottom: 1px solid rgba(0,0,0,0.5);
        }}

        .leaf-back {{
            z-index: 4;
            transition: transform 0.6s ease-in;
            transform-origin: top; /* 背面要從頂部轉下來 */
            transform: rotateX(180deg);
            display: flex;
            align-items: flex-end;
            justify-content: center;
        }}

        /* 動態類別：點擊後觸發 */
        .flipped .leaf-front {{
            transform: rotateX(-180deg);
        }}
        .flipped .leaf-back {{
            transform: rotateX(0deg);
        }}

        /* 裝飾線 */
        .flap-unit::after {{
            content: "";
            position: absolute;
            top: 50%; left: 0; width: 100%; height: 2px;
            background: rgba(0,0,0,0.8);
            z-index: 10;
        }}
    </style>
    </head>
    <body>

    <div class="board" id="board"></div>

    <script>
        const t1 = Array.from("{text1}");
        const t2 = Array.from("{text2}");
        const board = document.getElementById('board');
        let currentPhase = 1;

        function renderBoard(fromText, toText) {{
            board.innerHTML = '';
            fromText.forEach((char, i) => {{
                const targetChar = toText[i] || " ";
                const unit = document.createElement('div');
                unit.className = 'flap-unit';
                
                // HTML 結構：
                // base-top: 新字的上半
                // base-bottom: 舊字的下半 (會被蓋住) -> 更新為新字的下半
                // leaf-front: 舊字的上半 (翻下去)
                // leaf-back: 新字的下半 (翻下來露出)
                unit.innerHTML = `
                    <div class="base-top">${{targetChar}}</div>
                    <div class="base-bottom">${{targetChar}}</div>
                    <div class="leaf-front">${{char}}</div>
                    <div class="leaf-back">${{targetChar}}</div>
                `;
                board.appendChild(unit);
            }});
        }}

        function toggle() {{
            const units = document.querySelectorAll('.flap-unit');
            units.forEach((unit, i) => {{
                setTimeout(() => {{
                    unit.classList.add('flipped');
                }}, i * 50);
            }});
            
            // 動畫結束後，重置狀態以便下次翻轉
            setTimeout(() => {{
                const oldT1 = [...t1];
                const oldT2 = [...t2];
                if (currentPhase === 1) {{
                    renderBoard(t2, t1);
                    currentPhase = 2;
                }} else {{
                    renderBoard(t1, t2);
                    currentPhase = 1;
                }}
            }}, 1000);
        }}

        renderBoard(t1, t2);
        board.addEventListener('click', toggle);
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=450)
