import streamlit as st
import streamlit.components.v1 as components

# --- 1. 頁面配置 ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: transparent !important;}
    .stApp {background: #000 !important;}
    iframe {border: none; width: 100%; height: 100vh; overflow: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 參數獲取 ---
input_text_raw = st.query_params.get("text", "聖誕快樂")
# 強制只取第一段，且最多 10 個字
display_text = input_text_raw.replace('，', ',').split(',')[0][:10]

# --- 3. 純淨看板 HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    :root {{
        --font-family: "PingFang TC", "Microsoft JhengHei", sans-serif;
        --card-bg: linear-gradient(180deg, #3a3a3a 0%, #1a1a1a 50%, #000 51%, #222 100%);
    }}
    body {{ 
        background: #000; display: flex; flex-direction: column; justify-content: center; 
        align-items: center; height: 100vh; margin: 0; padding: 10px; box-sizing: border-box; 
        overflow: hidden;
    }}
    #board-container {{ 
        display: grid; 
        grid-template-columns: repeat({len(display_text)}, var(--unit-width, 40px)); 
        gap: 8px; 
        perspective: 1000px;
        transform: scale(1.1);
    }}
    .flap-unit {{ 
        position: relative; 
        width: var(--unit-width, 40px); 
        height: calc(var(--unit-width, 40px) * 1.4); 
        background: #000; border-radius: 6px; 
        font-family: var(--font-family); 
        font-size: calc(var(--unit-width, 40px) * 1.0); 
        font-weight: 900; color: #fff; 
        box-shadow: 0 12px 30px rgba(0,0,0,0.9);
    }}
    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center; 
        backface-visibility: hidden;
    }}
    .top {{ top: 0; height: calc(50% + 0.5px); align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 0.5px solid #000; }}
    .bottom {{ bottom: 0; height: 50%; align-items: flex-end; border-radius: 0 0 6px 6px; background: linear-gradient(180deg, #111 0%, #000 100%); }}
    .text {{ height: calc(var(--unit-width, 40px) * 1.4); width: 100%; text-align: center; position: absolute; line-height: calc(var(--unit-width, 40px) * 1.4); }}
    
    /* 中間切線 */
    .flap-unit::before {{ 
        content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px; 
        background: rgba(0,0,0,1); transform: translateY(-50%); z-index: 60; 
    }}

    .footer-note {{ margin-top: 50px; font-family: var(--font-family); font-size: 14px; color: rgba(255, 255, 255, 0.35); letter-spacing: 3px; }}
</style>
</head>
<body>
    <div id="board-container">
        {"".join([f'''
        <div class="flap-unit">
            <div class="half top"><div class="text">{char}</div></div>
            <div class="half bottom"><div class="text">{char}</div></div>
        </div>
        ''' for char in display_text])}
    </div>
    <div class="footer-note">𓃥白六訊息告示牌</div>

<script>
    function adjustSize() {{
        const winW = window.innerWidth - 40;
        const charCount = {len(display_text)};
        // 根據字數動態計算最適合的寬度
        const calculatedW = Math.floor((winW - (8 * (charCount - 1))) / charCount);
        // 單行最大寬度限制在 85px 以防平板上太大
        const finalUnitW = Math.min(85, calculatedW);
        document.documentElement.style.setProperty('--unit-width', finalUnitW + 'px');
    }}
    window.onload = adjustSize;
    window.onresize = adjustSize;
</script>
</body>
</html>
"""

components.html(html_code, height=800)
