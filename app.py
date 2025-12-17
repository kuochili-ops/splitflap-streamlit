import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Toggle", layout="centered")

st.title("📟 互動翻轉告示板")
st.caption("輸入一段話，點擊看板切換前後半段")

# 使用者輸入
user_input = st.text_input("請輸入句子", "人生到底為了啥吃頓好的")

if user_input:
    # 邏輯：將字數除以二
    total_len = len(user_input)
    split_point = math.ceil(total_len / 2)
    
    part1 = user_input[:split_point]
    part2 = user_input[split_point:]
    
    # 補齊長度，讓兩段呈現一致
    max_len = max(len(part1), len(part2))
    text1 = part1.ljust(max_len, " ")
    text2 = part2.ljust(max_len, " ")

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@700&display=swap');
        
        body {{ background: transparent; display: flex; justify-content: center; padding: 20px 0; overflow: hidden; }}
        
        .board {{
            background: #111;
            padding: 15px;
            border-radius: 10px;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 6px;
            border: 4px solid #333;
            cursor: pointer;
            perspective: 1000px;
        }}

        .flap-card {{
            position: relative;
            width: 50px;
            height: 80px;
            background: #1a1a1a;
            border-radius: 4px;
            font-family: 'Noto Sans TC', sans-serif;
            font-size: 40px;
            font-weight: bold;
            color: #ddd;
            line-height: 80px;
            text-align: center;
        }}

        /* 中間切割線 */
        .flap-card::after {{
            content: "";
            position: absolute;
            top: 50%; left: 0; width: 100%; height: 2px;
            background: rgba(0,0,0,0.9);
            z-index: 10;
        }}

        /* 翻轉動畫 */
        .flip-anim {{
            animation: flip-half 0.5s ease-in-out forwards;
        }}

        @keyframes flip-half {{
            0% {{ transform: rotateX(0deg); }}
            50% {{ transform: rotateX(-90deg); color: #888; }} /* 翻到一半 */
            51% {{ transform: rotateX(90deg); color: #888; }}  /* 從背後出現 */
            100% {{ transform: rotateX(0deg); }}
        }}

        @media (max-width: 480px) {{
            .flap-card {{ width: 38px; height: 60px; font-size: 28px; line-height: 60px; }}
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
        let isAnimating = false;

        // 初始化
        function init() {{
            t1.forEach(char => {{
                const card = document.createElement('div');
                card.className = 'flap-card';
                card.innerText = char === ' ' ? '\\u00A0' : char;
                board.appendChild(card);
            }});
        }}

        function toggle() {{
            if (isAnimating) return;
            isAnimating = true;
            
            const cards = document.querySelectorAll('.flap-card');
            const targetText = (currentPhase === 1) ? t2 : t1;

            cards.forEach((card, i) => {{
                setTimeout(() => {{
                    // 觸發動畫
                    card.classList.remove('flip-anim');
                    void card.offsetWidth; 
                    card.classList.add('flip-anim');

                    // 在翻轉到 90 度的瞬間換字 (約 250ms)
                    setTimeout(() => {{
                        const newChar = targetText[i] === ' ' ? '\\u00A0' : targetText[i];
                        card.innerText = newChar;
                    }}, 250);

                    if (i === cards.length - 1) {{
                        setTimeout(() => {{ isAnimating = false; }}, 500);
                    }}
                }}, i * 40); // 瀑布流依次翻轉
            }});

            currentPhase = (currentPhase === 1) ? 2 : 1;
        }}

        board.addEventListener('click', toggle);
        init();
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=300)
