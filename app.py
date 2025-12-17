import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Split-Flap Absolute", layout="centered")

# --- 側邊欄配置 ---
st.sidebar.header("📟 看板模式設定")
mode = st.sidebar.radio("展示方式", ["單行拆句", "多行列顯示"])
col_count = st.sidebar.slider("每行字數", 2, 10, 4 if mode == "多行列顯示" else 8)

st.title("📟 物理翻板：絕對隔離版")
st.caption("強制渲染刷新，徹底解決字元拼合與上下不一致問題。")

# --- 文字邏輯 ---
if mode == "單行拆句":
    raw_input = st.text_input("輸入句子", "謝謝光臨歡迎再來")
    chars = list(raw_input)
    mid = math.ceil(len(chars) / 2)
    s1, s2 = chars[:mid], chars[mid:]
    max_l = max(len(s1), len(s2))
    s1 += [" "] * (max_l - len(s1))
    s2 += [" "] * (max_l - len(s2))
    display_cols = max_l
else:
    s1_input = st.text_input("第一句", "往事就是我的安慰")
    s2_input = st.text_input("第二句", "妳無愛我無所謂啦")
    s1, s2 = list(s1_input), list(s2_input)
    max_l = max(len(s1), len(s2))
    s1 += [" "] * (max_l - len(s1))
    s2 += [" "] * (max_l - len(s2))
    display_cols = col_count

# --- HTML/JS ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    body {{ background: transparent; display: flex; flex-direction: column; align-items: center; padding: 20px 0; overflow: hidden; }}
    
    .board {{
        display: grid; grid-template-columns: repeat({display_cols}, 72px);
        gap: 12px; perspective: 2000px; justify-content: center;
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
    .top {{ top: 0; align-items: flex-start; border-radius: 4px 4px 0 0; border-bottom: 1px solid #000; }}
    .bottom {{ bottom: 0; align-items: flex-end; border-radius: 0 0 4px 4px; }}
    .text {{ height: 100px; line-height: 100px; text-align: center; width: 100%; }}

    /* 物理隔離層級 */
    .base-top {{ z-index: 1; }} 
    .base-bottom {{ z-index: 2; }}
    
    .leaf {{
        position: absolute; top: 0; left: 0; width: 100%; height: 50%;
        z-index: 10; transform-origin: bottom;
        transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        transform-style: preserve-3d;
    }}
    .leaf-front {{ z-index: 11; }} 
    .leaf-back {{ transform: rotateX(-180deg); z-index: 10; }}

    .flipping {{ transform: rotateX(-180deg); }}

    .flap-unit::after {{
        content: ""; position: absolute; top: 50%; left: 0; width: 100%; height: 2px;
        background: #000; transform: translateY(-50%) translateZ(30px); z-index: 50;
    }}
</style>
</head>
<body>
<div class="board" id="board"></div>

<script>
    const tA = {s1}, tB = {s2};
    let currentIsA = true, isAnimating = false;

    function init() {{
        document.getElementById('board').innerHTML = tA.map((c, i) => `
            <div class="flap-unit" id="unit-${{i}}">
                <div class="half top base-top"><div class="text">${{tB[i]}}</div></div>
                <div class="half bottom base-bottom"><div class="text">${{c}}</div></div>
                <div class="leaf">
                    <div class="half top leaf-front"><div class="text">${{c}}</div></div>
                    <div class="half bottom leaf-back"><div class="text">${{tB[i]}}</div></div>
                </div>
            </div>`).join('');
    }}

    function flip() {{
        if (isAnimating) return;
        isAnimating = true;

        const units = document.querySelectorAll('.flap-unit');
        const nextArr = currentIsA ? tB : tA;
        const futureArr = currentIsA ? tA : tB;

        units.forEach((u, i) => {{
            setTimeout(() => {{
                const leaf = u.querySelector('.leaf');
                leaf.classList.add('flipping');

                // 核心：在動畫一半時(0.3s)，強制將被遮住的舊字隱藏
                setTimeout(() => {{
                   u.querySelector('.base-bottom .text').style.visibility = 'hidden';
                }}, 300);

                // 動畫結束處理
                leaf.addEventListener('transitionend', function handler() {{
                    leaf.removeEventListener('transitionend', handler);
                    
                    // 1. 同步更換所有文字內容
                    u.querySelector('.base-bottom .text').innerText = nextArr[i];
                    u.querySelector('.base-bottom .text').style.visibility = 'visible';
                    u.querySelector('.leaf-front .text').innerText = nextArr[i];
                    
                    // 2. 靜默歸位葉片
                    leaf.style.transition = 'none';
                    leaf.classList.remove('flipping');
                    
                    // 3. 預填下一次內容
                    u.querySelector('.base-top .text').innerText = futureArr[i];
                    u.querySelector('.leaf-back .text').innerText = futureArr[i];

                    // 4. 強制刷新
                    void leaf.offsetWidth;
                    leaf.style.transition = '';
                    
                    if (i === units.length - 1) {{
                        currentIsA = !currentIsA;
                        isAnimating = false;
                    }}
                }}, {{ once: true }});
            }}, i * 40);
        }});
    }}

    document.body.addEventListener('click', flip);
    init();
</script>
</body>
</html>
"""

components.html(html_code, height=600)
