import streamlit as st
import streamlit.components.v1 as components
import math

# --- 1. 頁面配置 ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; margin: 0 !important;}
    body {overflow: hidden; background: transparent;}
    </style>
    """, unsafe_allow_html=True)

# 獲取參數
full_text = st.query_params.get("text", "質感顯示翻版看板正常運作中")

# --- 2. 核心邏輯：計算分段 ---
# 每段最多 10 字
chunk_size = 10
chunks = [full_text[i:i + chunk_size] for i in range(0, len(full_text), chunk_size)]

# --- 3. 核心 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    body {{ 
        margin: 0; padding: 0; background: transparent;
        display: flex; justify-content: center; align-items: center;
        height: 100vh; font-family: 'Noto Sans TC', sans-serif;
    }}
    #board {{
        display: grid; gap: 10px;
        grid-template-columns: repeat({chunk_size}, 1fr);
    }}
    .flap {{
        position: relative; width: 60px; height: 84px; /* 固定高度防止半字 */
        background: #000; border-radius: 6px;
        font-size: 50px; font-weight: 900; color: #fff;
        perspective: 1000px;
    }}
    .half {{
        position: absolute; left: 0; width: 100%; height: 50%;
        overflow: hidden; backface-visibility: hidden;
        background: linear-gradient(180deg, #333 0%, #1a1a1a 100%);
    }}
    .top {{ 
        top: 0; border-radius: 6px 6px 0 0; border-bottom: 1px solid #000;
        display: flex; align-items: flex-start; justify-content: center;
        transform-origin: bottom; transition: transform 0.6s;
    }}
    .bottom {{ 
        bottom: 0; border-radius: 0 0 6px 6px;
        display: flex; align-items: flex-end; justify-content: center;
        background: linear-gradient(180deg, #151515 0%, #000 100%);
    }}
    /* 💡 修正半字問題：精確行高 */
    .text {{ 
        height: 200%; line-height: 168px; text-align: center; width: 100%;
    }}
    .bottom .text {{ transform: translateY(-50%); }}
    .flipping .top {{ transform: rotateX(-180deg); }}
</style>
</head>
<body>
    <div id="board"></div>
    <script>
        const chunks = {chunks};
        let currentIndex = 0;
        const board = document.getElementById('board');

        function updateBoard() {{
            const text = chunks[currentIndex];
            const chars = text.padEnd(10, ' ').split(''); // 補滿 10 格保持位置固定
            
            board.innerHTML = chars.map(c => `
                <div class="flap">
                    <div class="half top"><div class="text">${{c}}</div></div>
                    <div class="half bottom"><div class="text">${{c}}</div></div>
                </div>
            `).join('');

            // 觸發動畫
            document.querySelectorAll('.flap').forEach((el, i) => {{
                setTimeout(() => el.classList.add('flipping'), i * 100);
            }});

            currentIndex = (currentIndex + 1) % chunks.length;
        }}

        updateBoard();
        if (chunks.length > 1) {{
            setInterval(updateBoard, 4000); // 4秒換下一句
        }}
    </script>
</body>
</html>
"""

# --- 4. 關鍵修正：給予足夠的容器高度 ---
# 這裡高度設為 200，保證上半部字元不會被 Streamlit 裁切
components.html(html_code, height=200)
