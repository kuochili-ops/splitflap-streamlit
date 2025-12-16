import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os, re, io

# ---------- 字型設定 ----------
font_dir = "fonts"
if not os.path.exists(font_dir):
    os.makedirs(font_dir)

weights = {
    "Thin": "NotoSansTC-Thin.ttf",
    "Regular": "NotoSansTC-Regular.ttf",
    "Medium": "NotoSansTC-Medium.ttf",
    "SemiBold": "NotoSansTC-SemiBold.ttf"
}

with st.sidebar:
    st.header("字型設定")
    selected_weight = st.selectbox("選擇字重", list(weights.keys()))
    font_size = st.slider("字型大小 (PNG 輸出)", 20, 96, 48)

def load_font(weight_key, size):
    font_file = weights.get(weight_key)
    font_path = os.path.join(font_dir, font_file)
    try:
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        else:
            st.warning(f"找不到字型檔：{font_file}，改用預設字型")
            return ImageFont.load_default()
    except OSError:
        st.warning(f"字型載入失敗：{font_file}，改用預設字型")
        return ImageFont.load_default()

font = load_font(selected_weight, font_size)

# ---------- 字型即時預覽 ----------
with st.sidebar:
    st.write("字型預覽：")
    preview_img = Image.new("RGB", (400, 100), "white")
    draw = ImageDraw.Draw(preview_img)
    test_text = "測試字型 ABC123"
    bbox = font.getbbox(test_text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (400 - tw)//2
    ascent, descent = font.getmetrics()
    ty = (100 - ascent)//2
    draw.text((tx, ty), test_text, fill="black", font=font)
    st.image(preview_img, use_column_width=True)

# ---------- UI ----------
st.title("🪧 Flip-board / Split-flap 文字呈現")
st.caption("輸入文字 → 翻頁板風格顯示（水平/直排、動畫、色彩、尺寸、PNG下載）")

with st.sidebar:
    st.header("設定")
    text = st.text_area("輸入文字（支援中英文與數字）", "啟利，節日快樂！Happy Holidays 2025")

    orientation = st.radio("方向", ["水平", "直排"], index=0)
    flap_bg = st.color_picker("面板底色", "#1A1A1A")
    flap_gap_color = st.color_picker("翻頁切縫顏色", "#0E0E0E")
    text_color = st.color_picker("字色", "#F0F0F0")
    accent_color = st.color_picker("框線/高光", "#2A2A2A")

    cols = st.slider("每列最大字數（水平/直排）", 4, 30, 16)
    char_w = st.slider("字格寬度 (px)", 36, 120, 72)
    char_h = st.slider("字格高度 (px)", 44, 160, 96)
    spacing = st.slider("字格間距 (px)", 0, 12, 4)
    padding = st.slider("外框邊距 (px)", 4, 40, 12)
    corner_radius = st.slider("外框圓角 (px)", 0, 24, 8)

    # 新增控制項
    gloss_strength = st.slider("面板反光強度", 0.0, 0.5, 0.2, step=0.05)
    flip_enabled = st.checkbox("啟動翻板動畫", value=True)

# ---------- Utils ----------
def normalize_text(s: str) -> str:
    return re.sub(r"[^\S\r\n]", " ", s)

def chunk_text_horizontal(s: str, width: int):
    lines, line = [], ""
    for ch in s:
        if ch == "\n":
            lines.append(line); line = ""; continue
        line += ch
        if len(line) >= width:
            lines.append(line); line = ""
    if line: lines.append(line)
    return lines

# ---------- HTML 預覽 ----------
def css_splitflap_container_html(lines, orientation, colors, sizes, gloss_strength, flip_enabled):
    flap_bg, flap_gap_color, text_color, accent_color = colors
    char_w, char_h, spacing, padding, corner_radius = sizes

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
      font-family: "JetBrains Mono", monospace;
      font-size: {int(char_h*0.6)}px;
      font-weight: 600;
      text-align: center;
      border-radius: 6px;
      overflow: hidden;
    }}
    .cell::before {{
      content: "";
      position: absolute;
      left: 0; right: 0;
      top: 50%;
      height: 1px;
      background: {flap_gap_color};
    }}
    .char-top, .char-bottom {{
      display: block;
      height: 50%;
      overflow: hidden;
      backface-visibility: hidden;
    }}
    .char-top {{
      transform-origin: bottom;
    }}
    .char-bottom {{
      transform-origin: top;
    }}
    @keyframes flipTop {{
      0%   {{ transform: rotateX(0deg); }}
      100% {{ transform: rotateX(-90deg); }}
    }}
    @keyframes flipBottom {{
      0%   {{ transform: rotateX(90deg); }}
      100% {{ transform: rotateX(0deg); }}
    }}
    .flip .char-top {{
      animation: flipTop 0.3s ease-in forwards;
    }}
    .flip .char-bottom {{
      animation: flipBottom 0.3s ease-out forwards;
      animation-delay: 0.3s;
    }}
    .gloss {{
      pointer-events: none;
      position: absolute;
      inset: 0;
      background: linear-gradient(180deg, rgba(255,255,255,{gloss_strength}), rgba(0,0,0,0.4));
      mix-blend-mode: overlay;
    }}
    </style>
    """

    html = ['<div class="board">']
    for line in lines:
        html.append('<div class="row">')
        for ch in line:
            safe = ch if ch.strip() else "&nbsp;"
            if flip_enabled and ch in ["2","0","2","5"]:
                cell_class = "flip"
            else:
                cell_class = ""
            html.append(f'''
              <div class="cell {cell_class}">
                <span class="char-top">{safe}</span>
                <span class="char-bottom">{safe}</span>
                <span class="gloss"></span>
              </div>
            ''')
        html.append('</div>')
    html.append('</div>')
    return css + "\n" + "\n".join(html)

# ---------- Render HTML ----------
s = normalize_text(text)
lines = chunk_text_horizontal(s, cols)
colors = (flap_bg, flap_gap_color, text_color, accent_color)
sizes = (char_w, char_h, spacing, padding, corner_radius)
html = css_splitflap_container_html(lines, orientation, colors, sizes, gloss_strength, flip_enabled)
st.components.v1.html(html, height=400, scrolling=False)

st.write("---")
st.subheader("下載 PNG（靜態合成）")

# ---------- PIL 靜態合成 ----------
def pil_splitflap_image(lines, char_w, char_h, spacing, padding,
                        flap_bg, flap_gap_color, text_color,
                        accent_color, font, font_size,
                        orientation="水平"):
    if orientation == "水平":
        max_len = max(len(line) for line in lines) if lines else 1
        rows = len(lines)
        board_w = padding*2 + max_len*char_w + (max_len-1)*spacing
        board_h = padding*2 + rows*char_h + (rows-1)*spacing
    else:  # 直排
        max_len = len(lines)
        rows = max(len(line) for line in lines) if lines else 1
        board_w = padding*2 + rows*char_w + (rows-1)*spacing
        board_h = padding*2 + max_len*char_h + (max_len-1)*spacing

    img = Image.new("RGBA", (board_w, board_h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0,0,board_w,board_h], fill=accent_color)

    if orientation == "水平":
        y = padding
        for line in lines:
            x = padding
            for ch in line:
                draw.rectangle([x, y, x+char_w, y+char_h], fill=flap_bg)
                mid = y + char_h//2
                draw.line([(x, mid), (x+char_w, mid)], fill=flap_gap_color, width=1)

                disp = ch if ch.strip() else " "
                bbox = font.getbbox(disp)
                tw = bbox[2] - bbox[0]
                ascent, descent = font.getmetrics()
                tx = x + (char_w - tw)//2
                is_ascii = all(ord(c) < 128 for c in disp)
                ty = y + (char_h - ascent)//2 - (int(font_size*0.08) if is_ascii else 0)
                draw.text((tx, ty), disp, fill=text_color, font=font)

                x += char_w + spacing
            y += char_h + spacing
    else:  # 直排
        x = padding
        for line in lines:
            y = padding
            for ch in line:
                draw.rectangle([x, y, x+char_w, y+char_h], fill=flap_bg)
                mid = y + char_h//2
                draw.line([(x, mid), (x+char_w, mid)], fill=flap_gap_color, width=1)

                disp = ch if ch.strip() else " "
                bbox = font.getbbox(disp)
                tw = bbox[2] - bbox[0]
                ascent, descent = font.getmetrics()
                tx = x + (char_w - tw)//2
                is_ascii = all(ord(c) < 128 for c in disp)
                ty = y + (char_h - ascent)//2 - (int(font_size*0.08) if is_ascii else 0)
                draw.text((tx, ty), disp, fill=text_color, font=font)

                y += char_h + spacing
            x += char_w + spacing

    return img

# ---------- 呼叫 PIL 合成 ----------
img = pil_splitflap_image(
    lines, char_w, char_h, spacing, padding,
    flap_bg, flap_gap_color, text_color, accent_color,
    font, font_size, orientation
)

st.image(img, caption="PNG 預覽", use_column_width=True)

buf = io.BytesIO()
img.save(buf, format="PNG")
st.download_button("下載 PNG", data=buf.getvalue(),
                   file_name="splitflap.png", mime="image/png")

# ---------- 四字重比較 ----------
def preview_all_weights(test_text="字重比較 ABC123", size=48):
    img = Image.new("RGB", (600, 300), "white")
    draw = ImageDraw.Draw(img)
    y = 20
    for weight_name, font_file in weights.items():
        font_path = os.path.join(font_dir, font_file)
        try:
            font = ImageFont.truetype(font_path, size)
        except:
            font = ImageFont.load_default()
        draw.text((20, y), f"{weight_name}: {test_text}", fill="black", font=font)
        y += size + 20
    return img

st.subheader("四字重比較預覽")
all_weights_img = preview_all_weights(size=font_size)
st.image(all_weights_img, use_column_width=True)
