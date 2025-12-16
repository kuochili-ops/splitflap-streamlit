import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os, re, io

# ---------- 字型設定 ----------
font_dir = "fonts"
if not os.path.exists(font_dir):
    os.makedirs(font_dir)

# 四種字重
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
with st.sidebar:
    st.write("字型預覽：")
    preview_img = Image.new("RGB", (400, 100), "white")
    draw = ImageDraw.Draw(preview_img)
    test_text = "測試字型 ABC123"
    try:
        bbox = font.getbbox(test_text)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        tw, th = font.getsize(test_text)
    tx = (400 - tw)//2
    ty = (100 - th)//2
    draw.text((tx, ty), test_text, fill="black", font=font)
    st.image(preview_img, use_column_width=True)
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

    cols = st.slider("每列最大字數（水平/直排）", 4, 30, 16)
    char_w = st.slider("字格寬度 (px)", 36, 120, 72)
    char_h = st.slider("字格高度 (px)", 44, 160, 96)
    spacing = st.slider("字格間距 (px)", 0, 12, 4)
    padding = st.slider("外框邊距 (px)", 4, 40, 12)
    corner_radius = st.slider("外框圓角 (px)", 0, 24, 8)
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
def css_splitflap_container_html(lines, orientation, animate, colors, sizes):
    flap_bg, flap_gap_color, text_color, accent_color = colors
    char_w, char_h, spacing, padding, corner_radius = sizes

    css = f"""<style> ... </style>"""  # 省略 CSS 詳細內容（同你原本的）

    html = ['<div class="board">']
    for line in lines:
        html.append('<div class="row">')
        for ch in line:
            safe = ch if ch.strip() else "&nbsp;"
            html.append(f'''
              <div class="cell {'anim' if animate else ''}">
                <span class="char">{safe}</span>
                <span class="gloss"></span>
              </div>
            ''')
        html.append('</div>')
    html.append('</div>')
    return css + "\n" + "\n".join(html)

s = normalize_text(text)
lines = chunk_text_horizontal(s, cols)

colors = (flap_bg, flap_gap_color, text_color, accent_color)
sizes = (char_w, char_h, spacing, padding, corner_radius)
html = css_splitflap_container_html(lines, orientation, animate, colors, sizes)
st.markdown(html, unsafe_allow_html=True)
def pil_splitflap_image(lines, char_w, char_h, spacing, padding,
                        flap_bg, flap_gap_color, text_color,
                        accent_color, font, font_size,
                        orientation="水平"):
    # 計算版面大小
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
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                tx = x + (char_w - tw)//2
                ty = y + (char_h - th)//2
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
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                tx = x + (char_w - tw)//2
                ty = y + (char_h - th)//2
                draw.text((tx, ty), disp, fill=text_color, font=font)

                y += char_h + spacing
            x += char_w + spacing

    return img

# 呼叫 PIL 合成
img = pil_splitflap_image(
    lines, char_w, char_h, spacing, padding,
    flap_bg, flap_gap_color, text_color, accent_color,
    font, font_size, orientation
)

# 顯示 PNG 預覽
st.image(img, caption="PNG 預覽", use_column_width=True)

# 下載按鈕：轉成 bytes
buf = io.BytesIO()
img.save(buf, format="PNG")
st.download_button(
    "下載 PNG",
    data=buf.getvalue(),
    file_name="splitflap.png",
    mime="image/png"
)

# 額外功能：四字重比較
def preview_all_weights(test_text="字重比較 ABC123", size=48):
    # 建立一張圖片，四行文字，每行一個字重
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

# 顯示四字重比較
st.subheader("四字重比較預覽")
all_weights_img = preview_all_weights(size=font_size)
st.image(all_weights_img, use_column_width=True)
