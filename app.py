import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Interactive Flap Board", layout="centered")

def smart_split_text(text):
    if not text: return "TOUCH", "ME"
    length = len(text)
    mid = length // 2
    if length <= 5: return text, text
    
    # 找空格切分，若無則強制平分
    split_index = text.rfind(' ', 0, mid + 2)
    if split_index == -1: split_index = mid
    
    return text[:split_index].strip(), text[split_index:].strip()

st.title("🔘 互動式翻牌告示板")
st.write("點擊下方的告示板來切換訊息內容")

user_input = st.text_input("輸入你想說的話", "人生到底為了啥 為了吃頓好的")
run_btn = st.button("更新內容")

if user_input:
    text1, text2 = smart_split_text(user_input)
    
    # 計算看板長度，最少 8 格
    BOARD_SIZE = max(len(text1), len(text2), 8)
    
    def pad_text(t, size):
        return t.ljust(size, "\u00A0")

    safe_text1 = pad_text(text1, BOARD_SIZE)
    safe_text2 = pad_text(text2, BOARD_SIZE)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@700&display=swap');
        
        body {{
            background-color: transparent;
            margin: 0;
            display: flex;
            justify-content: center;
            padding: 20px 0;
            user-select: none; /* 防止點擊時選取到文字 */
        }}

        .board {{
            background: linear-gradient(145deg, #111, #222);
            padding: 20px;
            border-radius: 15px;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 8px;
            border: 5px solid #333;
            box-shadow: 0 20px 40px rgba(0,0,0,0.7);
            max-width: 95vw;
            cursor: pointer; /* 讓使用者知道可以點擊 */
            transition: transform 0.1s;
        }}
        
        .board:active {{
            transform: scale(0.98); /* 點擊時的縮小反饋 */
        }}
        
        .char-box {{
            width: 45px;
            height: 70px;
            background-color: #1a1a1a;
            color: #ffffff;
            font-family: 'Noto Sans TC', sans-serif;
            font-size: 36px;
            font-weight: bold;
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 6px;
            position: relative;
            overflow: hidden;
            border: 1px solid #000;
        }}

        .char-box::after {{
            content: "";
            position: absolute;
            top: 50%; left: 0; width: 100%; height: 2px;
            background: rgba(0,0,0,0.8);
            z-index: 5;
        }}

        .overlay {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, transparent 50%, rgba(0,0,0,0.2) 100%);
            pointer-events: none;
        }}

        /* 翻牌動畫 */
        .flipping {{
            animation: flipDown 0.6s cubic-bezier(0.455, 0.03, 0.515, 0.955);
        }}

        @keyframes flipDown {{
            0% {{ transform: rotateX(0deg); }}
            50% {{ transform: rotateX(-90deg); opacity: 0.8; }}
            51% {{ transform: rotateX(90deg); opacity: 0.8; }}
            100% {{ transform: rotateX(0deg); }}
        }}

        @media (max-width: 480px) {{
            .char-box {{ width: 36px; height: 58px; font-size: 26px; }}
            .board {{ padding: 12px; gap: 5px; }}
        }}
    </style>
    </head>
    <body>

    <div class="board" id="board" title="點擊切換訊息"></div>

    <script>
        const text1 = "{safe_text1}";
        const text2 = "{safe_text2}";
        const board = document.getElementById('board');
        let currentPhase = 1; 
        let isAnimating = false;

        function init() {{
            board.innerHTML = '';
            text1.split('').forEach(char => {{
                const box = document.createElement('div');
                box.className = 'char-box';
                box.innerHTML = `<span>${{char === ' ' ? '&nbsp;' : char}}</span><div class="overlay"></div>`;
                board.appendChild(box);
            }});
        }}

        function toggleFlip() {{
            if (isAnimating) return; // 動畫中防止重複觸發
            isAnimating = true;
            
            const targetText = (currentPhase === 1) ? text2 : text1;
            const boxes = document.querySelectorAll('.char-box');
            
            boxes.forEach((box, i) => {{
                setTimeout(() => {{
                    box.classList.remove('flipping');
                    void box.offsetWidth; // 強制重新渲染觸發動畫
                    box.classList.add('flipping');
                    
                    setTimeout(() => {{
                        const char = targetText[i] === ' ' ? '&nbsp;' : targetText[i];
                        box.querySelector('span').innerHTML = char;
                    }}, 300);
                    
                    // 最後一個字動畫結束後解鎖
                    if (i === boxes.length - 1) {{
                        setTimeout(() => {{ isAnimating = false; }}, 600);
                    }}
                }}, i * 50);
            }});
            
            currentPhase = (currentPhase === 1) ? 2 : 1;
        }}

        board.addEventListener('click', toggleFlip);
        init();
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=350)
