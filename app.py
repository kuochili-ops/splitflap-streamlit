import streamlit as st
import streamlit.components.v1 as components

# 設定頁面
st.set_page_config(page_title="Split-Flap Display", layout="centered")

def smart_split_text(text):
    """
    簡單斷句邏輯：
    回傳 (第一段, 第二段)
    """
    if not text:
        return "READY", "GO"
        
    length = len(text)
    mid = length // 2
    
    # 如果句子太短，兩段都顯示一樣，或者第二段顯示空
    if length <= 4:
        return text, text

    # 尋找最佳切分點 (優先找空格)
    left_space = text.rfind(' ', 0, mid + 2)
    right_space = text.find(' ', mid - 1)
    
    if left_space != -1:
        split_index = left_space
    elif right_space != -1:
        split_index = right_space
    else:
        split_index = mid

    part1 = text[:split_index].strip()
    part2 = text[split_index:].strip()
    
    return part1, part2

# --- Streamlit UI ---
st.title("🔠 Single-Row Flap Board")
st.markdown("單排顯示，訊息將在 **1秒後** 自動翻頁切換")

user_input = st.text_input("輸入文字", "Taipei Station")
run_btn = st.button("Display Message")

if run_btn:
    # 1. 取得兩段文字
    text1, text2 = smart_split_text(user_input)
    
    # 2. 為了美觀，我們將文字補齊長度，確保版面不跳動
    # 假設看板長度固定為 10 格 (可自行調整)
    BOARD_SIZE = 10
    
    def pad_text(t, size):
        # 截斷過長的
        t = t[:size]
        # 補滿空格 (置中或是靠左皆可，這裡用靠左補空格)
        return t.ljust(size, "\u00A0") # \u00A0 是不換行空格

    safe_text1 = pad_text(text1, BOARD_SIZE)
    safe_text2 = pad_text(text2, BOARD_SIZE)

    # 3. 生成 HTML/JS
    # 我們把 text1 和 text2 都傳給前端，由 JS 控制切換
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&display=swap');
        
        body {{
            background-color: transparent;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 120px; /* 配合 iframe 高度 */
        }}

        .board {{
            background-color: #222;
            padding: 15px 20px;
            border-radius: 8px;
            display: flex;
            gap: 5px;
            border: 3px solid #444;
            box-shadow: 0 8px 20px rgba(0,0,0,0.6);
        }}
        
        .char-box {{
            width: 45px;
            height: 70px;
            background-color: #1a1a1a;
            color: #eee;
            font-family: 'Roboto Mono', monospace;
            font-size: 40px;
            font-weight: bold;
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 4px;
            position: relative;
            overflow: hidden;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.8);
        }}

        /* 中間的分割線 */
        .line {{
            position: absolute;
            top: 50%;
            left: 0;
            width: 100%;
            height: 2px;
            background-color: rgba(0,0,0,0.5);
            z-index: 5;
        }}

        /* 翻頁動畫的關鍵 Class */
        .flipping {{
            animation: flipDown 0.6s ease-in-out;
        }}

        @keyframes flipDown {{
            0% {{ transform: perspective(400px) rotateX(0deg); opacity: 1; }}
            45% {{ transform: perspective(400px) rotateX(-90deg); opacity: 0.5; }}
            55% {{ transform: perspective(400px) rotateX(90deg); opacity: 0.5; }}
            100% {{ transform: perspective(400px) rotateX(0deg); opacity: 1; }}
        }}

    </style>
    </head>
    <body>

    <div class="board" id="board">
        </div>

    <script>
        // 接收 Python 傳來的資料
        const textPhase1 = "{safe_text1}";
        const textPhase2 = "{safe_text2}";
        const board = document.getElementById('board');
        const boardSize = {BOARD_SIZE};

        // 初始化看板格子
        function initBoard() {{
            board.innerHTML = '';
            for (let i = 0; i < boardSize; i++) {{
                let box = document.createElement('div');
                box.className = 'char-box';
                // 初始顯示第一段文字
                box.innerText = textPhase1[i] || ''; 
                
                let line = document.createElement('div');
                line.className = 'line';
                box.appendChild(line);
                
                board.appendChild(box);
            }}
        }}

        // 執行翻頁動作
        function flipToPhase2() {{
            const boxes = document.querySelectorAll('.char-box');
            
            boxes.forEach((box, index) => {{
                // 1. 加入動畫 class
                // 為了讓效果更自然，每個字加一點點延遲
                setTimeout(() => {{
                    box.classList.add('flipping');
                    
                    // 2. 在動畫翻到一半的時候(約300ms)更換文字
                    setTimeout(() => {{
                        // 保留原本的 line 元素，只改文字節點
                        // 這裡簡單處理：直接重設 innerHTML 會比較暴力，
                        // 我們只改第一個 childNode (也就是文字 Text Node)
                        if(box.firstChild.nodeType === Node.TEXT_NODE) {{
                            box.firstChild.textContent = textPhase2[index];
                        }} else {{
                            // 如果結構跑掉，就直接插文字
                            box.innerText = textPhase2[index];
                            let line = document.createElement('div');
                            line.className = 'line';
                            box.appendChild(line);
                        }}
                    }}, 250); // 在翻轉到一半看不太清楚時換字

                    // 3. 動畫結束後移除 class (雖然這裡只跑一次，但好習慣)
                    setTimeout(() => {{
                        box.classList.remove('flipping');
                    }}, 600);

                }}, index * 50); // 每個字錯開 50ms
            }});
        }}

        // --- 主流程 ---
        initBoard();

        // 設定 1000ms (1秒) 後切換
        setTimeout(() => {{
            flipToPhase2();
        }}, 1000);

    </script>
    </body>
    </html>
    """

    # 渲染組件
    components.html(html_code, height=150)

else:
    st.info("👆 輸入長句並按下按鈕")
    # 預設顯示一個靜態的示意圖
    st.markdown("---")
