import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Ultimate", layout="centered")

# --- 側邊欄配置 ---
st.sidebar.header("📟 看板設定")
mode = st.sidebar.selectbox("展示模式", ["單行拆分 (A+B)", "多行排列 (長句)"])
col_count = st.sidebar.slider("每行字數", 2, 10, 4 if mode == "多行排列 (長句)" else 8)

st.title("📟 物理翻板：極致穩定版")
st.caption("無論前進後退，永遠保持流暢下翻動態。")

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
    s2_input = st.text_input("第二句 (目標)", "妳無愛我無所謂啦")
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
    body {{ background: transparent; display: flex; flex-direction: column; align-items: center; padding: 20px 0; overflow: hidden; }}
    
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
    }}

    /* 統一文字定位，解決拼合錯位問題 */
    .half {{
        position: absolute; left: 0; width: 100%; height: 50%;
        overflow: hidden; background: #1a1a1a; display: flex; justify-content: center;
        backface-visibility: hidden; -webkit-backface-visibility: hidden;
    }}
    .top {{ top: 0; align-items: flex-start; border-radius: 6px 6px 0 0; border-bottom: 1px solid #000; }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 6px 6px; }}
    .text {{ height: 100px; line-height: 100px; text-align: center; }}

    /* 結構層級 */
    .base-top {{ z-index: 1; }}    /* 下一格上半 */
    .base-bottom {{ z-index: 2; }} /* 當前格下半 */
    
    .leaf {{
        position: absolute; top: 0; left: 0; width: 100%; height: 50%;
        z-index: 10; transform-origin: bottom;
        transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        transform-style: preserve-3d;
    }}
    .leaf-front {{ transform: rotateX(0deg); z-index: 11; }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 10; }}

    .flipping {{ transform: rotateX(-180deg); }}

    .flap-unit::after {{
        content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
        background: #000; transform: translateY(-50%) translateZ(20px); z-index: 30;
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

    function createUnit(charNow, charNext, i) {{
        return `
            <div class="flap-unit" id="unit-${{i}}">
                <div class="half top base-top"><div class="text">${{charNext}}</div></div>
                <div class="half bottom base-bottom"><div class="text">${{charNow}}</div></div>
                <div class="leaf">
                    <div class="half top leaf-front"><div class="text">${{charNow}}</div></div>
                    <div class="half bottom leaf-back"><div class="text">${{charNext}}</div></div>
                </div>
            </div>`;
    }}

    function init() {{
        document.getElementById('board').innerHTML = textA.map((c, i) => createUnit(c, textB[i], i)).join('');
    }}

    function flip() {{
        if (isAnimating) return;
        isAnimating = true;

        const units = document.querySelectorAll('.flap-unit');
        const nowArr = currentIsA ? textA : textB;
        const nextArr = currentIsA ? textB : textA;
        const futureArr = currentIsA ? textA : textB; // 翻完後，下一格底座要預備的字

        units.forEach((u, i) => {{
            setTimeout(() => {{
                const leaf = u.querySelector('.leaf');
                leaf.classList.add('flipping');

                // 關鍵：在動畫完全結束後才進行資料交換
                leaf.addEventListener('transitionend', function handler() {{
                    leaf.removeEventListener('transitionend', handler);
                    
                    // 1. 更新底層內容為已完成翻轉的字
                    u.querySelector('.base-bottom .text').innerText = nextArr[i];
                    u.querySelector('.leaf-front .text').innerText = nextArr[i];
                    
                    // 2. 靜默歸位葉片
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    
                    // 3. 預填下一次要翻出的字 (達成永遠下翻)
                    u.querySelector('.base-top .text').innerText = futureArr[i];
                    u.querySelector('.leaf-back .text').innerText = futureArr[i];

                    // 4. 強制瀏覽器重繪
                    void leaf.offsetWidth;
                    leaf.style.transition = '';
                    
                    if (i === units.length - 1) {{
                        currentIsA = !currentIsA;
                        isAnimating = false;
                    }}
                }}, {{ once: true }});
            }}, i * 60);
        }});
    }}

    document.body.addEventListener('click', flip);
    init();
</script>
</body>
</html>
"""

components.html(html_code, height=600)
