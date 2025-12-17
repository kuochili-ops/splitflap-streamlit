import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Realistic Split-Flap", layout="centered")

# 設定支援的字符序列 (擬真翻牌的順序)
CHAR_SET = " 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ日月火水木金土天地人上下左右的一是在不了有個我"

def smart_split_text(text):
    if not text: return "READY", "GO"
    text = text.upper() # 轉大寫以匹配字符集
    length = len(text)
    mid = length // 2
    if length <= 5: return text, text
    split_index = text.rfind(' ', 0, mid + 2)
    if split_index == -1: split_index = mid
    return text[:split_index].strip(), text[split_index:].strip()

st.title("⚙️ 擬真機械翻板告示板")
st.caption("點擊看板，體驗循序翻牌的機械動感")

user_input = st.text_input("輸入內容", "FLIGHT 888 TAIPEI")

if user_input:
    text1, text2 = smart_split_text(user_input)
    BOARD_SIZE = max(len(text1), len(text2), 10)
    
    safe_text1 = text1.ljust(BOARD_SIZE, " ")
    safe_text2 = text2.ljust(BOARD_SIZE, " ")

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&display=swap');
        body {{ background: transparent; display: flex; justify-content: center; padding: 20px 0; overflow: hidden; }}
        
        .board {{
            background: #111;
            padding: 15px;
            border-radius: 8px;
            display: flex;
            gap: 4px;
            border: 4px solid #333;
            cursor: pointer;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}

        .flap-unit {{
            width: 40px;
            height: 60px;
            background: #222;
            position: relative;
            font-family: 'Roboto Mono', monospace;
            font-size: 34px;
            color: #ddd;
            text-align: center;
            line-height: 60px;
            border-radius: 4px;
            perspective: 200px;
        }}

        /* 上半部與下半部遮罩 */
        .flap-unit::before {{
            content: "";
            position: absolute;
            top: 50%; left: 0; width: 100%; height: 2px;
            background: rgba(0,0,0,0.8);
            z-index: 10;
        }}

        /* 翻牌動畫：模擬單次拍打 */
        .flipping {{
            animation: flap-anim 0.1s step-end;
        }}

        @keyframes flap-anim {{
            0% {{ transform: rotateX(0deg); background: #333; }}
            50% {{ transform: rotateX(-90deg); background: #444; }}
            100% {{ transform: rotateX(0deg); background: #222; }}
        }}
    </style>
    </head>
    <body>

    <div class="board" id="board"></div>

    <script>
        const charSet = "{CHAR_SET}";
        const textPhase1 = "{safe_text1}";
        const textPhase2 = "{safe_text2}";
        const board = document.getElementById('board');
        let currentPhase = 1;
        let isAnimating = false;

        // 初始化看板
        function init() {{
            for (let i = 0; i < {BOARD_SIZE}; i++) {{
                const unit = document.createElement('div');
                unit.className = 'flap-unit';
                unit.innerText = textPhase1[i];
                board.appendChild(unit);
            }}
        }}

        // 核心邏輯：循序翻動
        async function animateTo(targetString) {{
            isAnimating = true;
            const units = document.querySelectorAll('.flap-unit');
            const promises = [];

            units.forEach((unit, i) => {{
                promises.push(new Promise(async (resolve) => {{
                    let currentStr = unit.innerText;
                    let targetStr = targetString[i];
                    
                    // 如果目標跟現在一樣，就不動
                    if (currentStr === targetStr) return resolve();

                    // 尋找在字符集中的位置
                    let currentIndex = charSet.indexOf(currentStr);
                    if (currentIndex === -1) currentIndex = 0;

                    // 開始循序翻轉
                    while (unit.innerText !== targetStr) {{
                        currentIndex = (currentIndex + 1) % charSet.length;
                        let nextChar = charSet[currentIndex];

                        // 觸發一次物理動畫效果
                        unit.classList.remove('flipping');
                        void unit.offsetWidth; 
                        unit.classList.add('flipping');
                        
                        unit.innerText = nextChar;

                        // 模擬機械翻轉的速度 (毫秒)
                        await new Promise(r => setTimeout(r, 40)); 
                        
                        // 到了就停止
                        if (nextChar === targetStr) break;
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
    
    components.html(html_code, height=300)
