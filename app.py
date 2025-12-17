import streamlit as st
import streamlit.components.v1 as components
import math
import urllib.parse

# 1. 隱藏所有邊框與 UI
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0px; margin: 0px;}
    body {background-color: transparent;}
    </style>
    """, unsafe_allow_html=True)

# 2. 處理網址傳過來的中文文字
query_params = st.query_params
raw_text = query_params.get("text", "歡迎光臨")
# 強制解碼編碼過的 URL 參數
input_text = urllib.parse.unquote(raw_text)

# 文字拆分邏輯
chars = list(input_text)
mid = math.ceil(len(chars) / 2)
s1, s2 = chars[:mid], chars[mid:]
max_l = max(len(s1), len(s2))
s1 += [" "] * (max_l - len(s1))
s2 += [" "] * (max_l - len(s2))

# 3. 核心 HTML (加入關鍵的 meta 標籤)
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8"> <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
        :root {{
            --unit-width: calc(min(70px, 94vw / {max_l} - 6px));
            --unit-height: calc(var(--unit-width) * 1.5);
            --font-size: calc(var(--unit-width) * 0.85);
        }}
        body {{ background: transparent; display: flex; justify-content: center; margin: 0; overflow: hidden; }}
        .board {{ display: grid; grid-template-columns: repeat({max_l}, var(--unit-width)); gap: 6px; perspective: 2000px; padding: 20px 0; }}
        .flap-unit {{ position: relative; width: var(--unit-width); height: var(--unit-height); background: #000; border-radius: 6px; font-family: 'Noto Sans TC', sans-serif; font-size: var(--font-size); font-weight: 900; color: #fff; }}
        .half {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%); display: flex; justify-content: center; backface-visibility: hidden; -webkit-backface-visibility: hidden; }}
        .top {{ top: 0; align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 1.5px solid #000; }}
        .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 6px 6px; }}
        .text {{ height: var(--unit-height); line-height: var(--unit-height); text-align: center; }}
        .leaf {{ position: absolute; top: 0; left: 0; width: 100%; height: 50%; z-index: 15; transform-origin: bottom; transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; will-change: transform; }}
        .leaf-front {{ z-index: 16; background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%); }} 
        .leaf-back {{ transform: rotateX(-180deg); z-index: 15; background: #1a1a1a; }}
        .flipping {{ transform: rotateX(-180deg); }}
    </style>
</head>
<body>
    <div class="board" id="board"></div>
    <script>
        const tA = {s1}, tB = {s2};
        let currentIsA = true;
        let isAnimating = false;

        function init() {{
            document.getElementById('board').innerHTML = tA.map((c, i) => `
                <div class="flap-unit">
                    <div class="half top base-top"><div class="text">${{c}}</div></div>
                    <div class="half bottom base-bottom"><div class="text">${{c}}</div></div>
                    <div class="leaf">
                        <div class="half top leaf-front"><div class="text">${{c}}</div></div>
                        <div class="half bottom leaf-back"><div class="text">${{c}}</div></div>
                    </div>
                </div>`).join('');
        }}

        function flip() {{
            if (isAnimating) return;
            isAnimating = true;
            const units = document.querySelectorAll('.flap-unit');
            const nextArr = currentIsA ? tB : tA;
            units.forEach((u, i) => {{
                setTimeout(() => {{
                    const leaf = u.querySelector('.leaf');
                    u.querySelector('.base-top .text').innerText = nextArr[i];
                    u.querySelector('.leaf-back .text').innerText = nextArr[i];
                    leaf.classList.add('flipping');
                    leaf.addEventListener('transitionend', function onEnd() {{
                        leaf.removeEventListener('transitionend', onEnd);
                        u.querySelector('.base-bottom .text').innerText = nextArr[i];
                        u.querySelector('.leaf-front .text').innerText = nextArr[i];
                        leaf.style.transition = 'none';
                        leaf.classList.remove('flipping');
                        leaf.offsetHeight;
                        leaf.style.transition = '';
                        if (i === units.length - 1) {{ currentIsA = !currentIsA; isAnimating = false; }}
                    }});
                }}, i * 50);
            }});
        }}
        document.body.addEventListener('click', flip);
        init();
    </script>
</body>
</html>
"""
components.html(html_code, height=350)
