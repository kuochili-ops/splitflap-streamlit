import streamlit as st
import streamlit.components.v1 as components

# 設定頁面配置
st.set_page_config(page_title="Split-Flap Display", layout="centered")

def smart_split_text(text):
    """
    智慧斷句邏輯：
    1. 嘗試尋找中間點附近的空格或標點。
    2. 如果找不到，則強制從中間切斷。
    """
    if not text:
        return "", ""
        
    length = len(text)
    mid = length // 2
    
    # 如果句子太短，直接放第一行
    if length <= 5:
        return text, ""

    # 尋找最佳切分點 (優先找空格)
    # 在中間點前後搜尋空格
    left_space = text.rfind(' ', 0, mid + 3)
    right_space = text.find(' ', mid - 2)
    
    split_index = mid
    
    if left_space != -1:
        split_index = left_space
    elif right_space != -1:
        split_index = right_space
    else:
        # 如果是中文或無空格，直接切中點
        split_index = mid

    part1 = text[:split_index].strip()
    part2 = text[split_index:].strip()
    
    return part1, part2

# --- Streamlit UI ---

st.title("🔠 Split-Flap Message Board")
st.markdown("輸入一句話，生成復古機場告示牌效果")

# 輸入區
user_input = st.text_input("請輸入文字 (例如: 今晚我想來點 鼎泰豐的小籠包)", "Departure Time 12:00")

if st.button("Display Message"):
    # 執行斷句
    line1, line2 = smart_split_text(user_input)
    
    # --- HTML/CSS 嵌入 ---
    # 這裡我們手寫一個簡單的 HTML/CSS 來模擬翻牌效果
    # 為了讓效果更像，我們將每個字元分開處理
    
    def generate_flap_html(text_row):
        chars = list(text_row)
        # 補滿空格以維持版面平衡 (假設一行最多 12 字)
        max_chars = 12
        while len(chars) < max_chars:
            chars.append("&nbsp;")
        
        html_chars = ""
        for char in chars[:max_chars]: # 截斷超過長度的字
            html_chars += f"""
            <div class="flap-container">
                <div class="flap upper">{char}</div>
                <div class="flap lower">{char}</div>
                <div class="line"></div>
            </div>
            """
        return html_chars

    html_row1 = generate_flap_html(line1)
    html_row2 = generate_flap_html(line2)

    # 完整的 HTML 字串
    html_code = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&display=swap');
        
        .board {{
            background-color: #222;
            padding: 20px;
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            gap: 15px;
            align-items: center;
            border: 4px solid #444;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
        
        .row {{
            display: flex;
            gap: 4px;
        }}
        
        .flap-container {{
            width: 40px;
            height: 60px;
            background-color: #333;
            color: #eee;
            position: relative;
            font-family: 'Roboto Mono', monospace;
            font-size: 36px;
            font-weight: bold;
            border-radius: 4px;
            perspective: 600px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .flap {{
            position: absolute;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #1a1a1a;
        }}
        
        /* 視覺上的分割線 */
        .line {{
            position: absolute;
            top: 50%;
            left: 0;
            width: 100%;
            height: 2px;
            background-color: rgba(0,0,0,0.6);
            z-index: 10;
        }}
        
        /* 簡單的進場動畫 */
        .flap-container {{
            animation: flipIn 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
            opacity: 0;
            transform: rotateX(-90deg);
        }}
        
        /* 讓每個字稍微錯開時間出現，製造機械感 */
        .row:nth-child(1) .flap-container:nth-child(1) {{ animation-delay: 0.1s; }}
        .row:nth-child(1) .flap-container:nth-child(2) {{ animation-delay: 0.15s; }}
        .row:nth-child(1) .flap-container:nth-child(3) {{ animation-delay: 0.2s; }}
        .row:nth-child(1) .flap-container:nth-child(4) {{ animation-delay: 0.25s; }}
        .row:nth-child(1) .flap-container:nth-child(5) {{ animation-delay: 0.3s; }}
        .row:nth-child(1) .flap-container:nth-child(6) {{ animation-delay: 0.35s; }}
        .row:nth-child(1) .flap-container:nth-child(7) {{ animation-delay: 0.4s; }}
        
        .row:nth-child(2) .flap-container:nth-child(1) {{ animation-delay: 0.4s; }}
        .row:nth-child(2) .flap-container:nth-child(2) {{ animation-delay: 0.45s; }}
        .row:nth-child(2) .flap-container:nth-child(3) {{ animation-delay: 0.5s; }}
        .row:nth-child(2) .flap-container:nth-child(4) {{ animation-delay: 0.55s; }}
        
        @keyframes flipIn {{
            0% {{ opacity: 0; transform: rotateX(-90deg); }}
            100% {{ opacity: 1; transform: rotateX(0deg); }}
        }}
        
    </style>

    <div class="board">
        <div class="row">
            {html_row1}
        </div>
        <div class="row">
            {html_row2}
        </div>
    </div>
    """

    # 渲染 HTML 到 Streamlit
    components.html(html_code, height=200)

else:
    st.info("👆 輸入文字並按下按鈕查看效果")
