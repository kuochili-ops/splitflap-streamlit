import streamlit as st
import json
from flip_board_2 import render_flip_board

st.set_page_config(layout="wide")

# 假設這是妳抓取到的新聞清單
display_content = [
    "APPLE STOCK HITS NEW HIGH",
    "TAIPEI WEATHER IS SUNNY",
    "PYTHON FLIP BOARD READY",
    "今天是個寫程式的好日子"
]

st.title("新聞翻板即時看板")

# 關鍵修正點：必須將 list 轉換為 JSON 字串再傳入
render_flip_board(json.dumps(display_content), stay_sec=8.0)

st.write("看板每 8 秒自動更新新聞與時鐘")
