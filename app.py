import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Multi-Line", layout="centered")

st.title("📟 物理翻板：多行絕對穩定版")
st.caption("自動處理長句換行，並修復多行狀態下的層級競爭問題。")

user_input = st.text_input("輸入句子", "妳無愛我無所謂妳放撒我無所謂往事就是我的安慰")

if user_input:
    chars = list(user_input)
    # 自動切割為 4 個一組的行，讓顯示更整齊
    rows = [chars[i:i + 4] for i in range(0, len(chars), 4)]
    
    # 這裡我們模擬「前半段」與「後半段」的切換邏輯
    # 您可以根據需要修改 t1 (初始) 與 t2 (目標)
    t1 = chars
    # 目標文字：將原句反轉或平移，這裡示範簡單的位移
    t2 = chars[4:] + chars[:4] 

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
        body {{ background: transparent; display: flex; flex-direction: column; align-items: center; padding: 20px 0; }}
        
        .board {{
            display: grid;
            grid-template-columns: repeat(4, 75px);
            gap: 15px;
            perspective: 2000px;
        }}

        .flap-unit {{
            position: relative; width: 70px; height: 100px;
            background-color: #111; border-radius: 6px;
            font-family: 'Noto Sans TC', sans-serif; font-size: 55px; font-weight: 900; color: #fff;
            transform-style: preserve-3d;
        }}

        .half {{
            position: absolute; left: 0; width: 100%; height: 50%;
            overflow: hidden; background: #1a1a1a; display: flex; justify-content: center;
            -webkit-backface-visibility: visible; backface-visibility: visible;
        }}
        .top {{ top: 0; align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 1px solid #000; }}
        .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 6px 6px; }}
        .text {{ height: 100px; line-height: 100px; text-align: center; }}

        /* --- 穩定版物理層級 --- */
        .base-t2-top {{ z-index: 1; transform: translateZ(0px); }}
        .base-t1-bottom {{ z-index: 2; transform: translateZ(1px); }}

        .leaf-old {{
            position: absolute; top: 0; left: 0; width: 100%; height: 50%;
            transform-origin: bottom; z-index: 10;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.1s;
            transform: translateZ(4px) rotateX(0deg);
        }}

        .leaf-new {{
            position: absolute; top: 50%; left: 0; width: 100%; height: 50%;
            transform-origin: top; z-index: 5;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.1s;
            transform: translateZ(3px) rotateX(180deg);
            opacity: 0;
        }}

        /* 往 B 翻 (去程) */
        .to-b .leaf-old {{ transform: translateZ(4px) rotateX(-180deg); opacity: 0; }}
        .to-b .leaf-new {{ transform: translateZ(3px) rotateX(0deg); z-index: 12; opacity: 1; }}

        /* 裝飾線：強制置頂 */
        .flap-unit::after {{
            content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
            background: #000; transform: translateY(-50%) translateZ(20px); z-index: 30;
        }}
    </style>
    </head>
    <body>
    <div class="board" id="board"></div>

    <script>
        const s1 = {t1};
        const s2 = {t2};
        const board = document.getElementById('board');

        board.innerHTML = s1.map((charA, i) => `
            <div class="flap-unit" data-index="${{i}}">
                <div class="half top base-t2-top"><div class="text">${{s2[i] || ""}}</div></div>
                <div class="half bottom base-t1-bottom"><div class="text">${{charA}}</div></div>
                <div class="half top leaf-old"><div class="text">${{charA}}</div></div>
                <div class="half bottom leaf-new"><div class="text">${{s2[i] || ""}}</div></div>
            </div>
        `).join('');

        let isB = false;
        board.addEventListener('click', () => {{
            isB = !isB;
            const units = document.querySelectorAll('.flap-unit');
            units.forEach((u, i) => {{
                // 增加行與行之間的微小延遲，增加節奏感
                setTimeout(() => {{
                    if (isB) u.classList.add('to-b');
                    else u.classList.remove('to-b');
                }}, i * 50);
            }});
        }});
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=600)
