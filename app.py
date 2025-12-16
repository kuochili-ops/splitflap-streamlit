import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import textwrap
import re

st.set_page_config(page_title="Flip-board Text", page_icon="🪧", layout="centered")

# ---------- UI ----------
st.title("🪧 Flip-board / Split-flap 文字呈現")
st.caption("輸入文字 → 翻頁板風格顯示（水平/直排、動畫、色彩、尺寸、PNG下載）")

with st.sidebar:
    st.header("設定")
    text = st.text_area("輸入文字（支援中英文與數字）", "啟利，節日快樂！Happy Holidays 2025")

    orientation = st.radio("方向", ["水平", "直排"], index=0)
    animate = st.checkbox("啟用翻頁動畫", value=True)
    flap_bg = st.color_picker("面板底色", "#1A1A1A")
    flap_gap_color = st.color_picker("翻頁切縫顏色", "#0E0E0E")
    text_color = st.color_picker("字色", "#F0F0F0")
    accent_color = st.color_picker("框線/高光", "#2A2A2A")

    cols = st.slider("每列最大字數（水平）/ 每列最大字數（直排）", 4, 30, 16)
    char_w = st.slider("字格寬度 (px)", 36, 120, 72)
    char_h = st.slider("字格高度 (px)", 44, 160, 96)
    spacing = st.slider("字格間距 (px)", 0, 12, 4)
    padding = st.slider("外框邊距 (px)", 4, 40, 12)
    corner_radius = st.slider("外框圓角 (px)", 0, 24, 8)

    st.write("---")
    font_name = st.selectbox("字型（PIL 用於輸出 PNG）", ["Auto", "NotoSansTC-Regular.ttf", "JetBrainsMono-Regular.ttf"])
    font_size = st.slider("字型大小 (PNG 輸出)", 20, 96, 48)

# ---------- Utils ----------
def normalize_text(s: str) -> str:
    # 保留常見可見字符，移除控制符
    s = re.sub(r"[^\S\r\n]", " ", s)  # unify spaces
    return s

def chunk_text_horizontal(s: str, width: int):
    # 按字元切塊，非單詞換行，保留空格
    lines = []
    line = ""
    for ch in s:
        if ch == "\n":
            lines.append(line)
            line = ""
            continue
        line += ch
        if len(line) >= width:
            lines.append(line)
            line = ""
    if line:
        lines.append(line)
    return lines

def chunk_text_vertical(s: str, height: int):
    # 直排：每列只放一個字（或指定字數），以列為單位堆疊
    # 這裡仍用 cols 當「每列最大字數」，但直排會把每列視為一個「縱列」
    # 實作上：切成多列，每列最多 cols 個字
    cols_list = []
    line = ""
    for ch in s:
        if ch == "\n":
            if line:
                cols_list.append(line)
                line = ""
            continue
        line += ch
        if len(line) >= height:
            cols_list.append(line)
            line = ""
    if line:
        cols_list.append(line)
    return cols_list

def css_splitflap_container_html(lines, orientation, animate, colors, sizes):
    flap_bg, flap_gap_color, text_color, accent_color = colors
    char_w, char_h, spacing, padding, corner_radius = sizes

    # base CSS
    css = f"""
    <style>
    .board {{
      display: inline-block;
      padding: {padding}px;
      background: {accent_color};
      border-radius: {corner_radius}px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.35) inset, 0 8px 16px rgba(0,0,0,0.25);
      border: 1px solid rgba(255,255,255,0.06);
    }}
    .row {{
      display: flex;
      {'flex-direction: column;' if orientation=='直排' else 'flex-direction: row;'}
      gap: {spacing}px;
      margin-bottom: {spacing}px;
    }}
    .cell {{
      position: relative;
      width: {char_w}px;
      height: {char_h}px;
      background: {flap_bg};
      color: {text_color};
      font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: {int(char_h*0.6)}px;
      font-weight: 600;
      line-height: {char_h}px;
      text-align: center;
      text-transform: none;
      border-radius: 6px;
      box-shadow:
        0 1px 0 rgba(255,255,255,0.05) inset,
        0 -1px 0 rgba(0,0,0,0.4) inset,
        0 4px 8px rgba(0,0,0,0.45);
      overflow: hidden;
    }}
    .cell::before {{
      content: "";
      position: absolute;
      left: 0; right: 0;
      top: 50%;
      height: 1px;
      background: {flap_gap_color};
      box-shadow: 0 1px 0 rgba(255,255,255,0.06);
      transform: translateY(-0.5px);
    }}
    .gloss {{
      pointer-events: none;
      position: absolute;
      inset: 0;
      background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(0,0,0,0.25));
      mix-blend-mode: soft-light;
    }}
    .char {{
      position: relative;
      display: block;
      width: 100%;
      height: 100%;
      will-change: transform;
      transform-origin: 50% 50%;
    }}
    @keyframes flap {{
      0% {{ transform: rotateX(0deg); filter: brightness(1); }}
      49% {{ transform: rotateX(-88deg); filter: brightness(0.6); }}
      51% {{ transform: rotateX(88deg); filter: brightness(0.6); }}
      100% {{ transform: rotateX(0deg); filter: brightness(1); }}
    }}
    .anim .char {{
      animation: {"flap 0.5s ease-in-out"}; 
    }}
    </style>
    """

    # HTML
    html = ['<div class="board">']
    for line in lines:
        html.append('<div class="row">')
        for ch in line:
            safe = ch if ch.strip() != "" else "&nbsp;"
            html.append(f'''
              <div class="cell {'anim' if animate else ''}">
                <span class="char">{safe}</span>
                <span class="gloss"></span>
              </div>
            ''')
        html.append('</div>')
    html.append('</div>')
    return css + "\n" + "\n".join(html)

# ---------- Layout compute ----------
s = normalize_text(text)

if orientation == "水平":
    lines = chunk_text_horizontal(s, cols)
else:
    # 直排：用「多列」概念，一列最多 cols 個字；視覺上每列垂直排列
    lines = chunk_text_horizontal(s, cols)  # 簡化：先按 cols 切，再以 column 呈現
    # 若要更嚴謹的縱書格式，之後可將 writing-mode 改成 vertical-rl 並處理標點旋轉

# ---------- Render HTML preview ----------
colors = (flap_bg, flap_gap_color, text_color, accent_color)
sizes = (char_w, char_h, spacing, padding, corner_radius)
html = css_splitflap_container_html(lines, orientation, animate, colors, sizes)
st.markdown(html, unsafe_allow_html=True)

st.write("---")
st.subheader("下載 PNG（靜態合成）")

# ---------- PIL static render ----------
def pil_splitflap_image(lines, char_w, char_h, spacing, padding, flap_bg, flap_gap_color, text_color, accent_color, font_name, font_size):
    # 計算畫布尺寸
    max_len = max(len(line) for line in lines) if lines else 1
    rows = len(lines)
    board_w = padding*2 + max_len*char_w + (max_len-1)*spacing
    board_h = padding*2 + rows*char_h + (rows-1)*spacing

    img = Image.new("RGBA", (board_w, board_h), (0,0,0,0))
    draw = ImageDraw.Draw(img)

    # 外框
    # 簡化：用矩形替代圓角（可再優化）
    draw.rectangle([0,0,board_w,board_h], fill=accent_color)

    # 字型
    font = None
    if font_name != "Auto":
        try:
            font = ImageFont.truetype(f"assets/fonts/{font_name}", font_size)
        except:
            font = ImageFont.load_default()
    else:
        try:
            font = ImageFont.truetype("assets/fonts/NotoSansTC-Regular.ttf", font_size)
        except:
            font = ImageFont.load_default()

    # 繪製每個字格
    y = padding
    for line in lines:
        x = padding
        for ch in line:
            draw.rectangle([x, y, x+char_w, y+char_h], fill=flap_bg)
            # 中線（翻頁縫）
            mid = y + char_h//2
            draw.line([(x, mid), (x+char_w, mid)], fill=flap_gap_color, width=1)

            # 高光陰影（簡版）
            draw.line([(x, y), (x+char_w, y)], fill=(255,255,255,20), width=1)
            draw.line([(x, y+char_h), (x+char_w, y+char_h)], fill=(0,0,0,60), width=1)

            # 文字置中
            disp = ch if ch.strip() != "" else " "
            tw, th = draw.textsize(disp, font=font)
            tx = x + (char_w - tw)//2
            ty = y + (char_h - th)//2
            draw.text((tx, ty), disp, fill=text_color, font=font)

            x += char_w + spacing
        y += char_h + spacing

    return img

img = pil_splitflap_image(lines, char_w, char_h, spacing, padding, flap_bg, flap_gap_color, text_color, accent_color, font_name, font_size)
st.image(img, caption="PNG 預覽", use_column_width=True)
st.download_button("下載 PNG", data=img.to_bytes(), file_name="splitflap.png", mime="image/png")
