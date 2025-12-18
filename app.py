import streamlit as st
import streamlit.components.v1 as components
import math

# --- 1. 頁面極簡化設定 ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; margin: 0 !important;}
    body {overflow: hidden; background-color: transparent !important;}
    iframe {border: none;}
    </style>
    """, unsafe_allow_html=True)

# 獲取參數
full_text = st.query_params.get("text", "質感看板正常運作中")

# --- 2. 分段邏輯 ---
# 規則：每段最多 10 字，超過就切到下一幕
chunk_size = 10
chunks = [full_text[i:i + chunk_size] for i in range(0, len(full_text), chunk_size)]

# --- 3. 核心 HTML (解決半字問題) ---
# 我們放棄 vh/vw，改用固定像素 (px) 搭配 CSS scale，確保在 iframe 內絕對不切字
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    body {{ 
        margin: 0; padding: 0; 
        display: flex; justify-content: center; align-items: center; 
        height: 100vh; background: transparent;
        font-family: 'Noto Sans TC', sans-serif;
    }}
    #board {{
        display: grid; gap: 8px;
        grid-template-columns: repeat({chunk_size}, 60px);
        /* 💡 縮放補償：如果手機螢幕太窄，自動縮小看板 */
        transform: scale(min(1, calc(95vw / {chunk_size * 68}))); 
    }}
    .flap {{
        position: relative; width: 60px; height: 90px;
        background: #000; border-radius: 4px;
        font-size: 54px; font-weight: 900; color: #fff;
        perspective: 1000px;
    }}
    .half {{
        position: absolute; left: 0; width: 100%; height: 50%;
        overflow: hidden; backface-visibility: hidden;
        background: linear-gradient(180deg, #333 0%, #1a1a1a 100%);
    }}
    .top {{ 
        top: 0; border-radius: 4px 4px 0 0; border-bottom: 1px solid #000;
        display: flex; align-items: flex-start; justify-content: center;
        transform-origin: bottom; transition: transform 0.6s;
    }}
    .bottom {{ 
        bottom: 0; border-radius: 0 0 4px 4px;
        display: flex; align-items: flex-end; justify-content: center;
        background: linear-gradient(180deg, #151515 0%, #000 100%);
    }}
    /* 💡 徹底解決半字：使用固定的 line-height 讓文字強制垂直居中 */
    .text {{ 
        height: 180px; line-height: 180px; text-align: center; width: 100%;
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

        function draw() {{
            const text = chunks[currentIndex];
            // 補齊 10 格，讓版面不跳動
            const chars = text.padEnd(10, ' ').split(''); 
            
            board.innerHTML = chars.map(c => `
                <div class="flap">
                    <div class="half top"><div class="text">${{c}}</div></div>
                    <div class="half bottom"><div class="text">${{c}}</div></div>
                </div>
            `).join('');

            // 觸發翻轉動畫
            setTimeout(() => {{
                document.querySelectorAll('.flap').forEach((el, i) => {{
                    setTimeout(() => el.classList.add('flipping'), i * 80);
                }});
            }}, 50);

            currentIndex = (currentIndex + 1) % chunks.length;
        }}

        draw();
        if (chunks.length > 1) {{
            setInterval(draw, 4000); // 4秒換一幕
        }}
    </script>
</body>
</html>
"""

# --- 4. 關鍵：給予足夠的 iframe 高度預算 ---
# 設定 height=250，確保上半部 45px + 下半部 45px 加上陰影空間完全不被切除
components.html(html_code, height=250)
