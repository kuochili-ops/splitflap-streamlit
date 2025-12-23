import streamlit.components.v1 as components
import time  # 必須放在最上方

def render_flip_board(text, stay_sec=4.0):
    # 確保 text 必定為字串，避免傳入 list 導致 hash 失敗
    if isinstance(text, list):
        text = text[0] if text else ""
    
    # 背景圖邏輯
    img_data = "https://upload.wikimedia.org/wikipedia/en/2/21/Girl_with_Balloon.jpg"
    
    # (中間的 HTML 與 CSS 碼保持不變...)
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        /* ... 保持之前的 CSS ... */
    </style>
    </head>
    <body>
        <div class="acrylic-board">
            <div class="screw tl"></div><div class="screw tr"></div>
            <div class="screw bl"></div><div class="screw br"></div>
            <div id="row-msg" class="row-container"></div>
            <div id="row-info" style="display: flex; flex-direction: column; gap: 10px; width: 100%; align-items: center;">
                <div id="row-date" class="row-container"></div>
                <div id="row-clock" class="row-container"></div>
            </div>
        </div>
    <script>
        const fullText = "{text.upper()}";
        // ... 保持之前的 JavaScript ...
    </script>
    </body>
    </html>
    """
    
    # 修正 key 的生成方式，確保傳入的是字串
    # 使用 timestamp 確保每次點擊「更新」時都會重啟 iframe
    component_key = f"flip_{int(time.time())}"
    components.html(html_code, height=850, scrolling=False, key=component_key)
