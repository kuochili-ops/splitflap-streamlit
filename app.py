import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Split-Flap Board", layout="centered")

def smart_split_text(text):
    if not text: return "HELLO", "WORLD"
    length = len(text)
    mid = length // 2
    if length <= 5: return text, text
    
    # 找空格切分，若無則強制平分
    split_index = text.rfind(' ', 0, mid + 2)
    if split_index == -1: split_index = mid
    
    return text[:split_index].strip(), text[split_index:].strip()

st.title("📟 復古翻牌告示板")

# 使用者輸入
user_input = st.text_input("輸入你想說的話", "人生到底為了啥")
run_btn = st.button("開始翻轉")

if run_btn:
    text1, text2 = smart_split_text(user_input)
    
    # 根據內容長度動圖調整看板格子數，最少 8 格
    BOARD_SIZE = max(len(text1), len(text2), 8)
    
    def pad_text(t, size):
        return t.ljust(size, "\u00A0")

    safe_text1 = pad_text(text1, BOARD_SIZE)
    safe_text2 = pad_text(text2, BOARD_SIZE)

    # 核心 CSS 與 JS 優化
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
            padding-top: 20px;
        }}

        .board {{
            background: linear-gradient(145deg, #111, #222);
            padding: 15px;
            border-radius: 12px;
            display: flex;
            flex-wrap: wrap; /* 關鍵：當螢幕不夠寬時會自動換行 */
            justify-content: center;
            gap: 6px;
            border: 4px solid #333;
            box-shadow: 0 15px 35px rgba(0,0,0,0.8);
            max-width: 95vw; /* 限制不超出螢幕寬度 */
        }}
        
        .char-box {{
            width: 42px;
            height: 65px;
            background-color: #1a1a1a;
            color: #ffffff;
            font-family: 'Noto Sans TC', sans-serif;
            font-size: 32px; /* 稍微縮小字體以適應手機 */
            font-weight: bold;
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 6px;
            position: relative;
            overflow: hidden;
            border: 1px solid #000;
        }}

        /* 翻牌的中間橫線與陰影效果 */
        .char-box::after {{
            content: "";
            position: absolute;
            top: 50%;
            left: 0;
            width: 100%;
            height: 1px;
            background: rgba(0,0,0,0.7);
            z-index: 5;
            box-shadow: 0 1px 2px rgba(255,255,255,0.1);
        }}

        /* 漸層覆蓋層，增加立體感 */
        .overlay {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, transparent 50%, rgba(0,0,0,0.2) 100%);
            pointer-events: none;
        }}

        .flipping {{
            animation: flipDown 0.6s cubic-bezier(0.455, 0.03, 0.515, 0.955);
        }}

        @keyframes flipDown {{
            0% {{ transform: rotateX(0deg); opacity: 1; }}
            50% {{ transform: rotateX(-90deg); opacity: 0.8; }}
            51% {{ transform: rotateX(90deg); opacity: 0.8; }}
            100% {{ transform: rotateX(0deg); opacity: 1; }}
        }}

        /* 手機版微調 */
        @media (max-width: 480px) {{
            .char-box {{ width: 34px; height: 55px; font-size: 24px; }}
            .board {{ padding: 10px; gap: 4px; }}
        }}
    </style>
    </head>
    <body>

    <div class="board" id="board"></div>

    <script>
        const text1 = "{safe_text1}";
        const text2 = "{safe_text2}";
        const board = document.getElementById('board');

        // 初始化
        function init() {{
            text1.split('').forEach(char => {{
                const box = document.createElement('div');
                box.className = 'char-box';
                box.innerHTML = `<span>${{char === ' ' ? '&nbsp;' : char}}</span><div class="overlay"></div>`;
                board.appendChild(box);
            }});
        }}

        function startFlip() {{
            const boxes = document.querySelectorAll('.char-box');
            boxes.forEach((box, i) => {{
                setTimeout(() => {{
                    box.classList.add('flipping');
                    // 在翻轉到 90 度時換字
                    setTimeout(() => {{
                        const char = text2[i] === ' ' ? '&nbsp;' : text2[i];
                        box.querySelector('span').innerHTML = char;
                    }}, 300);
                }}, i * 70);
            }});
        }}

        init();
        setTimeout(startFlip, 1200); // 1.2秒後開始翻牌
    </script>
    </body>
    </html>
    """
    
    # 調高組件高度以確保不被切掉
    components.html(html_code, height=250)
