import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Stable Split-Flap", layout="centered")

# 這裡包含了常用的中文字、英數與「全形空格」
# 注意：這串字元集必須涵蓋你輸入的所有字，否則它會因為找不到而跳過或報錯
CHAR_SET = " 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ！？。，、：；「」人生到底為了啥吃頓好的"

def smart_split_text(text):
    if not text: return "READY", "GO"
    # 統一轉為大寫以匹配 CHAR_SET
    text = text.upper()
    length = len(text)
    mid = length // 2
    if length <= 5: return text, text
    
    split_index = text.rfind(' ', 0, mid + 2)
    if split_index == -1: split_index = mid
    return text[:split_index].strip(), text[split_index:].strip()

st.title("⚙️ 穩定版機械翻板")
st.caption("解決中文匹配問題，點擊看板進行循環切換")

user_input = st.text_input("輸入內容（請確保字元在字盤內）", "人生到底為了啥 吃頓好的")

if user_input:
    text1, text2 = smart_split_text(user_input)
    # 看板長度設固定，避免排版跳動
    BOARD_SIZE = 12
    
    # 使用標準空格補齊
    safe_text1 = text1.ljust(BOARD_SIZE, " ")
    safe_text2 = text2.ljust(BOARD_SIZE, " ")

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@700&display=swap');
        body {{ background: transparent; display: flex; justify-content: center; padding: 20px 0; }}
        
        .board {{
            background: #111;
            padding: 12px;
            border-radius: 8px;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 4px;
            border: 4px solid #333;
            cursor: pointer;
        }}

        .flap-unit {{
            width: 45px;
            height: 65px;
            background: #1a1a1a;
            position: relative;
            font-family: 'Noto Sans TC', sans-serif;
            font-size: 32px;
            color: #efefef;
            text-align: center;
            line-height: 65px;
            border-radius: 4px;
            perspective: 300px;
            overflow: hidden;
        }}

        .flap-unit::after {{
            content: "";
            position: absolute;
            top: 50%; left: 0; width: 100%; height: 1px;
            background: rgba(0,0,0,0.8);
            z-index: 10;
        }}

        .flipping {{
            animation: flap-anim 0.08s ease-in-out;
        }}

        @keyframes flap-anim {{
            0% {{ transform: rotateX(0deg); opacity: 1; }}
            50% {{ transform: rotateX(-90deg); opacity: 0.7; }}
            100% {{ transform: rotateX(0deg); opacity: 1; }}
        }}
    </style>
    </head>
    <body>
    <div class="board" id="board"></div>

    <script>
        // 確保這裡的字串與 Python 端的 CHAR_SET 完全一致
        const charSet = Array.from("{CHAR_SET}"); 
        const textPhase1 = "{safe_text1}";
        const textPhase2 = "{safe_text2}";
        const board = document.getElementById('board');
        let currentPhase = 1;
        let isAnimating = false;

        function init() {{
            for (let i = 0; i < {BOARD_SIZE}; i++) {{
                const unit = document.createElement('div');
                unit.className = 'flap-unit';
                unit.innerText = textPhase1[i] || " ";
                board.appendChild(unit);
            }}
        }}

        async function animateTo(targetString) {{
            isAnimating = true;
            const units = document.querySelectorAll('.flap-unit');
            const promises = [];

            units.forEach((unit, i) => {{
                promises.push(new Promise(async (resolve) => {{
                    let targetChar = targetString[i] || " ";
                    
                    // 檢查目標字是否在字元集內，不在的話強制改為空格
                    if (!charSet.includes(targetChar)) targetChar = " ";

                    let maxAttempts = charSet.length * 2; // 安全鎖：最多跑兩圈
                    let attempts = 0;

                    while (unit.innerText !== targetChar && attempts < maxAttempts) {{
                        let currentIndex = charSet.indexOf(unit.innerText);
                        if (currentIndex === -1) currentIndex = 0;

                        let nextIndex = (currentIndex + 1) % charSet.length;
                        unit.innerText = charSet[nextIndex];

                        // 動畫效果
                        unit.classList.remove('flipping');
                        void unit.offsetWidth; 
                        unit.classList.add('flipping');

                        await new Promise(r => setTimeout(r, 40)); 
                        attempts++;
                    }}
                    resolve();
                }}));
            }});

            await Promise.all(promises);
            isAnimating = false;
        }}

        board.addEventListener('click', () => {{
            if (isAnimating) return;
            const target = (currentPhase === 1) ? textPhase2 : textPhase1;
            animateTo(target);
            currentPhase = (currentPhase === 1) ? 2 : 1;
        }});

        init();
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=350)
