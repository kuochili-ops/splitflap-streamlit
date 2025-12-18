# --- 4. 核心 HTML 內容 (強化光影質感) ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900&display=swap');
    :root {{
        --unit-width: calc(min(80px, 95vw / {cols} - 6px));
        --unit-height: calc(var(--unit-width) * 1.5);
        --font-size: calc(var(--unit-width) * 1.05);
        --flip-speed: 0.6s;
        /* 深色質感背景 */
        --card-bg: linear-gradient(180deg, #333 0%, #111 50%, #000 51%, #222 100%);
    }}
    body {{ 
        background: transparent !important; 
        display: flex; justify-content: center; align-items: center; 
        height: 100vh; margin: 0; overflow: hidden; 
    }}
    #board-container {{ 
        display: grid; grid-template-columns: repeat({cols}, var(--unit-width)); 
        gap: 10px; perspective: 2000px; 
    }}
    /* 單個翻板的立體陰影 */
    .flap-unit {{ 
        position: relative; width: var(--unit-width); height: var(--unit-height); 
        background: #000; border-radius: 6px; 
        font-family: 'Noto Sans TC', sans-serif; font-size: var(--font-size); font-weight: 900; 
        color: #fff;
        /* 增加底部環境遮擋陰影 (Ambient Occlusion) */
        box-shadow: 0 10px 20px rgba(0,0,0,0.5), 0 6px 6px rgba(0,0,0,0.5);
    }}
    .half {{ 
        position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden; 
        background: var(--card-bg); display: flex; justify-content: center; 
        backface-visibility: hidden; 
    }}
    .top {{ 
        top: 0; height: calc(50% + 1px); align-items: flex-start; 
        border-radius: 6px 6px 0 0; 
        border-bottom: 1px solid rgba(0,0,0,0.7);
        /* 上半部增加一點頂部反光 */
        box-shadow: inset 0 2px 3px rgba(255,255,255,0.1);
    }}
    .bottom {{ 
        bottom: 0; height: 50%; align-items: flex-end; 
        border-radius: 0 0 6px 6px; 
        /* 下半部增加深色漸層 */
        background: linear-gradient(180deg, #111 0%, #050505 100%);
    }}
    .text {{ 
        height: var(--unit-height); width: 100%; text-align: center; 
        position: absolute; left: 0; line-height: var(--unit-height);
        /* 字體增加微弱的發光感 */
        text-shadow: 0 0 10px rgba(255,255,255,0.2);
    }}
    .top .text {{ top: 0; }}
    .bottom .text {{ bottom: 0; }}
    
    /* 翻轉葉片的光影變化 */
    .leaf {{ 
        position: absolute; top: 0; left: 0; width: 100%; height: 50%; 
        z-index: 15; transform-origin: bottom; 
        transition: transform var(--flip-speed) cubic-bezier(0.4, 0, 0.2, 1); 
        transform-style: preserve-3d; 
    }}
    .leaf-front {{ z-index: 16; background: var(--card-bg); border-radius: 6px 6px 0 0; }} 
    .leaf-back {{ 
        transform: rotateX(-180deg); z-index: 15; background: #111; 
        display: flex; justify-content: center; align-items: flex-end; 
        overflow: hidden; border-radius: 0 0 6px 6px;
    }}
    .flipping {{ transform: rotateX(-180deg); }}
    
    /* 中間的轉軸陰影線 */
    .flap-unit::before {{ 
        content: ""; position: absolute; top: 50%; left: 0; 
        width: 100%; height: 2px; background: rgba(0,0,0,0.8); 
        transform: translateY(-50%); z-index: 60; 
        box-shadow: 0 1px 2px rgba(255,255,255,0.05);
    }}
</style>
</head>
