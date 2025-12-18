import streamlit as st
import streamlit.components.v1 as components
import math

# --- 1. 強制隱藏所有 Streamlit UI 元件 ---
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], #MainMenu, footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; background-color: transparent !important;}
    .stApp {background: transparent !important;}
    /* 移除捲軸，確保嵌入時不會出現邊條 */
    html, body {overflow: hidden !important;}
    </style>
    """, unsafe_allow_html=True)

input_text_raw = st.query_params.get("text", "質感看板")
stay_sec = float(st.query_params.get("stay", 2.5))

# --- 2. 核心 HTML (立體光影版) ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    :root {{
        --font-family: "Noto Sans TC", sans-serif;
        --flip-speed: 0.65s;
        /* 💡 核心質感：模擬受光的金屬/塑料材質 */
        --card-bg: linear-gradient(180deg, #3a3a3a 0%, #1a1a1a 49%, #000 50%, #1a1a1a 100%);
    }}
    body {{ 
        background: transparent; display: flex; justify-content: center; 
        align-items: center; height: 100vh; margin: 0; 
    }}
    #board-container {{ 
        display: grid; 
        grid-template-columns: repeat(var(--cols, 8), var(--unit-width, 70px)); 
        gap: 12px; perspective: 2500px; 
    }}
    .flap-unit {{ 
        position: relative; 
        width: var(--unit-width, 70px); 
        height: calc(var(--unit-width, 70px) * 1.4); 
        background: #000; border-radius: 8px; 
        font-family: var(--font-family); 
        font-size: calc(var(--unit-width, 70px) * 0.85); 
        font-weight: 900; color: #fff; 
        /* 💡 雙重陰影：一個深色環境遮擋，一個擴散的投影 */
        box-shadow: 0 15px 35px rgba(0,0,0,0.8), 0 5px 15px rgba(0,0,0,0.5);
    }}
    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center; 
        backface-visibility: hidden; 
    }}
    .top {{ 
        top: 0; height: calc(50% + 1px); align-items: flex-start; 
        border-radius: 8px 8px 0 0; border-bottom: 1.5px solid rgba(0,0,0,0.9);
        /* 💡 頂部邊緣高光，模擬物理反光線 */
        box-shadow: inset 0 2px 4px rgba(255,255,255,0.15);
    }}
    .bottom {{ 
        bottom: 0; height: 50%; align-items: flex-end; 
        border-radius: 0 0 8px 8px; 
        background: linear-gradient(180deg, #151515 0%, #000 100%);
    }}
    .text {{ 
        height: calc(var(--unit-width, 70px) * 1.4); width: 100%; 
        text-align: center; position: absolute; left: 0; 
        line-height: calc(var(--unit-width, 70px) * 1.4);
        text-shadow: 0 0 8px rgba(255,255,255,0.2);
    }}
    .top .text {{ top: 0; }}
    .bottom .text {{ bottom: 0; }}
    /* ... 翻轉邏輯保持不變 ... */
</style>
</head>
</html>
"""
