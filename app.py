import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Final Fix", layout="centered")

st.title("📟 物理翻板：裁切校正版")
st.caption("已修正中文字體偏移。點擊看板切換前後半段。")

user_input = st.text_input("輸入句子", "謝謝光臨歡迎再來")

if user_input:
    # 邏輯：將字串轉為 List 處理，確保中文字元計算正確
    char_list = list(user_input)
    mid = math.ceil(len(char_list) / 2)
    t1_list = char_list[:mid]
    t2_list = char_list[mid:]
    
    max_len = max(len(t1_list), len(t2_list))
    # 補齊空白
    while len(t1_list) < max_len: t1_list.append(" ")
    while len(t2_list) < max_len: t2_list.append(" ")

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
        
        body {{ background: transparent; display: flex; justify-content: center; padding: 20px 0; overflow: hidden; }}
        
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
            font-weight: 900;
            color: #fff;
            user-select: none;
        }}

        /* 通用容器：強制裁切 */
        .clipper {{
            position: absolute;
            left: 0;
            width: 100%;
            height: 50%;
            overflow: hidden;
            background: #1a1a1a;
            backface-visibility: hidden;
        }}

        .top-clip {{
            top: 0;
            border-radius: 8px 8px 0 0;
            border-bottom: 1px solid rgba(0,0,0,0.5);
        }}

        .bottom-clip {{
            bottom: 0;
            border-radius: 0 0 8px 8px;
        }}

        /* 文字內容：使用絕對定位精準對齊中心 */
        .text-content {{
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            width: 100%;
            text-align: center;
            font-size: 64px; /* 固定字體大小 */
            height: 100px;
            line-height: 100px;
        }}

        /* 上半截：文字置頂 */
        .top-clip .text-content {{
            top: 0;
        }}

        /* 下半截：文字往上頂 50px，剛好露出下半部 */
        .bottom-clip .text-content {{
            bottom: 0;
        }}

        /* 翻動葉片 */
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
            border-radius: 0 0 8px 8px; /* 翻下來後變下半部 */
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
        const s1 = {t1_list};
        const s2 = {t2_list};
        const board = document.getElementById('board');

        function init() {{
            s1.forEach((char1, i) => {{
                const char2 = s2[i];
                const unit = document.createElement('div');
                unit.className = 'flap-unit';
                
                // 結構：
                // .top-clip: 背景上半 (新字)
                // .bottom-clip: 背景下半 (舊字)
                // .leaf-front: 葉片正面 (舊字上半)
                // .leaf-back: 葉片背面 (新字下半)
                unit.innerHTML = `
                    <div class="clipper top-clip">
                        <div class="text-content">${{char2}}</div>
                    </div>
                    <div class="clipper bottom-clip">
                        <div class="text-content">${{char1}}</div>
                    </div>
                    <div class="leaf">
                        <div class="clipper top-clip leaf-front">
                            <div class="text-content">${{char1}}</div>
                        </div>
                        <div class="clipper bottom-clip leaf-back">
                            <div class="text-content">${{char2}}</div>
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
                }}, i * 50);
            }});
            board.classList.toggle('is-flipped');
        }});

        init();
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=400)
