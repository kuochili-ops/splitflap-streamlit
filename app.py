import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Physical", layout="centered")

st.title("📟 物理翻板告示板")
st.caption("點擊看板，體驗「上板下翻」的墜落動態")

user_input = st.text_input("輸入句子", "今晚想來點 鼎泰豐小籠包")

if user_input:
    total_len = len(user_input)
    split_point = math.ceil(total_len / 2)
    
    # 分割上下半句
    t1 = user_input[:split_point]
    t2 = user_input[split_point:]
    
    # 補齊長度
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
            gap: 8px;
            perspective: 1000px;
            cursor: pointer;
        }}

        /* 每一格的容器 */
        .flap {{
            position: relative;
            width: 60px;
            height: 90px;
            background-color: #333;
            border-radius: 6px;
            font-family: 'Noto Sans TC', sans-serif;
            font-size: 50px;
            font-weight: bold;
            color: #ddd;
            line-height: 90px;
            text-align: center;
        }}

        /* 上半部與下半部的共用樣式 */
        .top, .bottom {{
            position: absolute;
            left: 0;
            width: 100%;
            height: 50%;
            overflow: hidden;
            background: #1a1a1a;
            -webkit-backface-visibility: hidden;
            backface-visibility: hidden;
        }}

        .top {{
            top: 0;
            border-radius: 6px 6px 0 0;
            line-height: 90px; /* 顯示文字上半部 */
            border-bottom: 1px solid rgba(0,0,0,0.5);
        }}

        .bottom {{
            bottom: 0;
            border-radius: 0 0 6px 6px;
            line-height: 0px; /* 顯示文字下半部 */
        }}

        /* 翻轉中的葉片 */
        .leaf {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 50%;
            background: #1a1a1a;
            border-radius: 6px 6px 0 0;
            z-index: 5;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            transform-origin: bottom;
            line-height: 90px;
            overflow: hidden;
            backface-visibility: hidden;
        }}

        /* 翻轉後的背面 */
        .leaf-back {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: #1a1a1a;
            transform: rotateX(-180deg);
            transform-origin: bottom;
            line-height: 0px;
            backface-visibility: hidden;
            border-radius: 0 0 6px 6px;
        }}

        .flipped .leaf {{
            transform: rotateX(-180deg);
        }}

        /* 中間陰影線 */
        .flap::after {{
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

        function createFlap(charA, charB) {{
            const wrap = document.createElement('div');
            wrap.className = 'flap';
            
            // 下層靜態文字 (B)
            wrap.innerHTML = `
                <div class="top">${{charB}}</div>
                <div class="bottom">${{charA}}</div>
                <div class="leaf">${{charA}}</div>
                <div class="leaf-back">${{charB}}</div>
            `;
            return wrap;
        }}

        function init() {{
            t1.forEach((char, i) => {{
                board.appendChild(createFlap(char, t2[i]));
            }});
        }}

        function doFlip() {{
            const flaps = document.querySelectorAll('.flap');
            flaps.forEach((flap, i) => {{
                setTimeout(() => {{
                    flap.classList.toggle('flipped');
                }}, i * 60);
            }});
        }}

        board.addEventListener('click', doFlip);
        init();
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=400)
