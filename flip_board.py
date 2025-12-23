import streamlit.components.v1 as components
import base64

def render_flip_board(text, stay_sec=4.0):
    # ... 妳原本所有的 img_data, html_code 邏輯保持不動 ...
    # ... (請保留妳原本那段長長的 html_code 變數內容) ...
    
    # --- 關鍵修正：將字串轉換成二進位 Base64 ---
    b64_content = base64.b64encode(html_code.encode("utf-8")).decode("utf-8")
    
    # 構造一個 Data URI
    data_uri = f"data:text/html;base64,{b64_content}"
    
    # 這裡改成使用 iframe 載入 URI，這在 Python 3.13 是唯一能避開 TypeError 的方法
    components.iframe(data_uri, height=850, scrolling=False, key="final-ultra-stable-board")
