import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Pro Max", layout="centered")

# --- 側邊欄配置 ---
st.sidebar.header("📟 看板設定")
mode = st.sidebar.selectbox("展示模式", ["單行拆分 (A+B)", "多行排列 (長句)"])
col_count = st.sidebar.slider("每行字數 (僅多行模式)", 2, 10, 4)

st.title("📟 物理翻板：極致穩定版")
st.caption("支援模式切換，且所有翻轉動作均維持物理下翻。")

# --- 處理文字邏輯 ---
if mode == "單行拆分 (A+B)":
    raw_input = st.text_input("輸入句子", "謝謝光臨歡迎再來")
    chars = list(raw_input)
    mid = math.ceil(len(chars) / 2)
    s1 = chars[:mid]
    s2 = chars[mid:]
    max_l = max(len(s1), len(s2))
    s1 += [" "] * (max_l - len(s1))
    s2 += [" "] * (max_l - len(s2))
    display_cols = max_l
else:
    s1_input = st.text_input("第一句 (初始)", "往事就是我的安慰")
    s2_input = st.text_input("第二句 (翻轉後)", "妳無愛我無所謂啦")
    
    s1 = list(s1_input)
    s2 = list(s2_input)
    max_l = max(len(s1), len(s2))
    s1 += [" "] * (max_l - len(s1))
    s2 += [" "] * (max_l - len(s2))
    display_cols = col_count

# --- HTML/JavaScript ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    
    body {{ 
        background: transparent; 
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        padding: 20px 0; 
        overflow: hidden;
    }}
    
    .board {{
        display: grid;
        grid-template-columns: repeat({display_cols}, 75px);
        gap: 12px;
        perspective: 1500px;
        justify-content: center;
    }}

    .flap-unit {{
        position: relative; width: 70px; height: 100px;
        background-color: #111; border-radius: 6px;
        font-family: 'Noto Sans TC', sans-serif; font-size: 55px; font-weight: 900; color: #fff;
        transform-style: preserve-3d;
    }}

    /* 半格基礎樣式 */
    .half {{
        position: absolute; left: 0; width: 100%; height: 50%;
        overflow: hidden; background: #1a1a1a; display: flex; justify-content: center;
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }}
    .top {{ top: 0; align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 1px solid #000; }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 6px 6px; }}
    .text {{ height: 100px; line-height: 100px; text-align: center; }}

    /* 層級設計 (始終保持下翻關鍵) */
    .base-top {{ z-index: 1; }}    /* 下一個字的上半 */
    .base-bottom {{ z-index: 2; }} /* 當前字的下半 */
    
    .leaf {{
        position: absolute; top: 0; left: 0; width: 100%; height: 50%;
        z-index: 10; transform-origin: bottom;
        transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        transform-style: preserve-3d;
    }}
    .leaf-front {{ z-index: 11; }} /* 當前字的上半 */
    .leaf-back {{ transform: rotateX(-180deg); z-index: 10; }} /* 下一個字的下半 */

    /* 動畫類別 */
    .flipping {{ transform: rotateX(-180deg); }}

    .flap-unit::after {{
        content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
        background: #000; transform: translateY(-50%) translateZ(10px); z-index: 20;
    }}
</style>
</head>
<body>
<div class="board" id="board"></div>

<script>
    const textA = {s1};
    const textB = {s2};
    let currentText = [...textA];
    let targetText = [...textB];
    let isAnimating = false;

    const board = document.getElementById('board');

    // 初始化看板
    function init() {{
        board.innerHTML = currentText.map((char, i) => `
            <div class="flap-unit" id="unit-${{i}}">
                <div class="half top base-top"><div class="text">${{targetText[i]}}</div></div>
                <div class="half bottom base-bottom"><div class="text">${{char}}</div></div>
                <div class="leaf">
                    <div class="half top leaf-front"><div class="text">${{char}}</div></div>
                    <div class="half bottom leaf-back"><div class="text">${{targetText[i]}}</div></div>
                </div>
            </div>
        `).join('');
    }}

    // 核心下翻邏輯
    function flipAll() {{
        if (isAnimating) return;
        isAnimating = true;

        const units = document.querySelectorAll('.flap-unit');
        
        units.forEach((u, i) => {{
            setTimeout(() => {{
                const leaf = u.querySelector('.leaf');
                leaf.classList.add('flipping');
                
                // 動畫結束後：靜默重置
                setTimeout(() => {{
                    // 1. 將當前格的底座內容更新為目標字
                    u.querySelector('.base-bottom .text').innerText = targetText[i];
                    u.querySelector('.leaf-front .text').innerText = targetText[i];
                    
                    // 2. 瞬間重置葉片位置 (無動畫)
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    
                    // 3. 準備下一次的目標
                    const nextTarget = (targetText === textB) ? textA[i] : textB[i];
                    u.querySelector('.base-top .text').innerText = nextTarget;
                    u.querySelector('.leaf-back .text').innerText = nextTarget;

                    // 4. 恢復動畫效果
                    setTimeout(() => {{ leaf.style.transition = ''; }}, 50);
                    
                    if (i === units.length - 1) {{
                        // 交換狀態
                        const temp = currentText;
                        currentText = targetText;
                        targetText = (targetText === textB) ? textA : textB;
                        isAnimating = false;
                    }}
                }}, 650); 
            }}, i * 60);
        }});
    }}

    board.addEventListener('click', flipAll);
    init();
</script>
</body>
</html>
"""

components.html(html_code, height=600)

if mode == "單行拆分 (A+B)":
    st.info("💡 模式：單行拆分。將輸入的句子平分為兩段進行下翻切換。")
else:
    st.info(f"💡 模式：多行排列。在「第一句」與「第二句」之間進行下翻循環。目前設定每行 {col_count} 個字。")
