import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Pro Max", layout="centered")

# --- 側邊欄配置 ---
st.sidebar.header("📟 看板模式設定")
mode = st.sidebar.radio("展示方式", ["單行拆句 (前段變後段)", "多行列顯示 (長句循環)"])

if mode == "單行拆句 (前段變後段)":
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
    col_count = st.sidebar.slider("每行顯示字數", 2, 10, 4)
    s1_input = st.text_input("第一句內容", "往事就是我的安慰")
    s2_input = st.text_input("第二句內容", "妳無愛我無所謂啦")
    s1 = list(s1_input)
    s2 = list(s2_input)
    max_l = max(len(s1), len(s2))
    s1 += [" "] * (max_l - len(s1))
    s2 += [" "] * (max_l - len(s2))
    display_cols = col_count

# --- HTML/JavaScript 終極邏輯 ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    body {{ background: transparent; display: flex; flex-direction: column; align-items: center; padding: 20px 0; overflow: hidden; }}
    
    .board {{
        display: grid;
        grid-template-columns: repeat({display_cols}, 72px);
        gap: 12px;
        perspective: 1500px;
        justify-content: center;
    }}

    .flap-unit {{
        position: relative; width: 68px; height: 100px;
        background-color: #111; border-radius: 4px;
        font-family: 'Noto Sans TC', sans-serif; font-size: 52px; font-weight: 900; color: #fff;
    }}

    .half {{
        position: absolute; left: 0; width: 100%; height: 50%;
        overflow: hidden; background: #1a1a1a; display: flex; justify-content: center;
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }}
    /* 強制文字對齊，確保拼合不出錯 */
    .top {{ top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 1px solid #000; }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; }}
    .text {{ height: 100px; line-height: 100px; text-align: center; width: 100%; }}

    /* 物理分層：底層固定，葉片翻轉 */
    .base-top {{ z-index: 1; }}
    .base-bottom {{ z-index: 2; }}
    
    .leaf {{
        position: absolute; top: 0; left: 0; width: 100%; height: 50%;
        z-index: 10; transform-origin: bottom;
        transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        transform-style: preserve-3d;
    }}
    .leaf-front {{ z-index: 11; }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 10; background: #1a1a1a; }}

    .flipping {{ transform: rotateX(-180deg); }}

    /* 中間細線裝飾 */
    .flap-unit::after {{
        content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 1px;
        background: rgba(0,0,0,0.6); transform: translateY(-50%) translateZ(20px); z-index: 30;
    }}
</style>
</head>
<body>
<div class="board" id="board"></div>

<script>
    const textA = {s1};
    const textB = {s2};
    let currentIsA = true;
    let isAnimating = false;

    function init() {{
        const board = document.getElementById('board');
        board.innerHTML = textA.map((char, i) => `
            <div class="flap-unit" id="unit-${{i}}">
                <div class="half top base-top"><div class="text">${{textB[i]}}</div></div>
                <div class="half bottom base-bottom"><div class="text">${{char}}</div></div>
                <div class="leaf">
                    <div class="half top leaf-front"><div class="text">${{char}}</div></div>
                    <div class="half bottom leaf-back"><div class="text">${{textB[i]}}</div></div>
                </div>
            </div>`).join('');
    }}

    function flip() {{
        if (isAnimating) return;
        isAnimating = true;

        const units = document.querySelectorAll('.flap-unit');
        const nowArr = currentIsA ? textA : textB;
        const nextArr = currentIsA ? textB : textA;
        const futureArr = currentIsA ? textA : textB; 

        units.forEach((u, i) => {{
            setTimeout(() => {{
                const leaf = u.querySelector('.leaf');
                leaf.classList.add('flipping');

                // 核心修復：在動畫執行到 90% 時才更換文字，避免肉眼看到拼合跳動
                setTimeout(() => {{
                    // 更新所有靜態面
                    u.querySelector('.base-bottom .text').innerText = nextArr[i];
                    u.querySelector('.leaf-front .text').innerText = nextArr[i];
                    
                    // 瞬間重置葉片位置
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    
                    // 預填下一次要翻出來的字
                    u.querySelector('.base-top .text').innerText = futureArr[i];
                    u.querySelector('.leaf-back .text').innerText = futureArr[i];

                    // 強制瀏覽器重繪
                    void leaf.offsetWidth;
                    leaf.style.transition = '';
                    
                    if (i === units.length - 1) {{
                        currentIsA = !currentIsA;
                        isAnimating = false;
                    }}
                }}, 550); // 略早於 0.6s 動畫結束
            }}, i * 50);
        }});
    }}

    document.body.addEventListener('click', flip);
    init();
</script>
</body>
</html>
"""

components.html(html_code, height=600)
