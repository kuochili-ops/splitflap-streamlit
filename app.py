import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Final", layout="centered")

st.title("📟 物理翻板：座標精準版")
st.caption("針對手機瀏覽器優化，解決中文字體位移問題。")

user_input = st.text_input("輸入句子", "謝謝光臨歡迎再來")

if user_input:
    # 邏輯：將字串轉為 List 並平分
    full_text = list(user_input)
    mid = math.ceil(len(full_text) / 2)
    t1 = full_text[:mid]
    t2 = full_text[mid:]
    
    # 補齊長度
    max_len = max(len(t1), len(t2))
    while len(t1) < max_len: t1.append(" ")
    while len(t2) < max_len: t2.append(" ")

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
        
        body {{ background: transparent; display: flex; justify-content: center; padding: 20px 0; touch-action: manipulation; }}
        
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
            border-radius: 8px;
            font-family: 'Noto Sans TC', sans-serif;
            font-size: 64px;
            font-weight: 900;
            color: #fff;
        }}

        /* 核心裁切容器 */
        .clip-box {{
            position: absolute;
            left: 0;
            width: 100%;
            height: 50%;
            overflow: hidden;
            background: #1a1a1a;
            display: flex;
            justify-content: center;
            backface-visibility: hidden;
        }}

        .top-half {{
            top: 0;
            border-radius: 8px 8px 0 0;
            border-bottom: 1px solid rgba(0,0,0,0.5);
            align-items: flex-start; /* 頂部對齊 */
        }}

        .bottom-half {{
            bottom: 0;
            border-radius: 0 0 8px 8px;
            align-items: flex-start; /* 同樣頂部對齊，但靠位移拉上來 */
        }}

        /* 文字渲染層：關鍵在於高度必須固定 */
        .text-render {{
            height: 100px;
            line-height: 100px;
            text-align: center;
            width: 100%;
        }}

        /* 下半部文字：往上推 50px，確保只露出下半截 */
        .bottom-half .text-render {{
            transform: translateY(-50px);
        }}

        /* 翻轉葉片結構 */
        .leaf {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 50%;
            z-index: 5;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            transform-origin: bottom;
            backface-visibility: hidden;
        }}

        .leaf-front {{ z-index: 2; }}
        .leaf-back {{ 
            z-index: 1; 
            transform: rotateX(-180deg);
            background: #1a1a1a;
            border-radius: 0 0 8px 8px;
            height: 100%; /* 翻轉後佔據下半部 */
            top: 100%; /* 定位在底部 */
            transform-origin: top;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            overflow: hidden;
        }}

        /* 狀態變化 */
        .flipped .leaf {{
            transform: rotateX(-180deg);
        }}

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
        const s1 = {t1};
        const s2 = {t2};
        const board = document.getElementById('board');

        function init() {{
            s1.forEach((char1, i) => {{
                const char2 = s2[i];
                const unit = document.createElement('div');
                unit.className = 'flap-unit';
                
                unit.innerHTML = `
                    <div class="clip-box top-half">
                        <div class="text-render">${{char2}}</div>
                    </div>
                    <div class="clip-box bottom-half">
                        <div class="text-render">${{char1}}</div>
                    </div>
                    
                    <div class="leaf">
                        <div class="clip-box top-half leaf-front">
                            <div class="text-render">${{char1}}</div>
                        </div>
                        <div class="leaf-back">
                            <div class="text-render" style="transform: translateY(-50px);">${{char2}}</div>
                        </div>
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
                }}, i * 45);
            }});
            board.classList.toggle('is-flipped');
        }});

        init();
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=450)
