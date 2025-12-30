import streamlit as st
import json
import feedparser
from flip_board_2 import render_flip_board

# --- 頁面配置 ---
st.set_page_config(page_title="白六新聞告示牌", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    header, [data-testid="stHeader"], footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; margin: 0 !important;}
    
    .console-fixed {
        position: fixed; bottom: -280px; left: 50%; transform: translateX(-50%);
        width: 90%; max-width: 750px; background: rgba(25,25,25,0.98);
        padding: 20px; border-radius: 15px 15px 0 0; z-index: 9999;
        transition: 0.4s ease-in-out; border: 1px solid #444; color: white;
    }
    .console-fixed:hover, .console-fixed:focus-within { bottom: 0 !important; }
    .bottom-trigger { position: fixed; bottom: 0; width: 100%; height: 30px; z-index: 9998; }
    </style>
    """, unsafe_allow_html=True)

def fetch_news():
    try:
        f = feedparser.parse("https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant")
        return [e.title.split(' - ')[0] for e in f.entries[:10]]
    except:
        return ["NEWS LOAD ERROR"]

# --- 調控面板 ---
st.markdown('<div class="bottom-trigger"></div>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="console-fixed">', unsafe_allow_html=True)
    st.markdown("<p style='color:gray; font-size:12px;'>⚙️ 設定面板 (滑鼠移至最下方開啟)</p>", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        mode = st.radio("模式", ["自動新聞", "手動輸入"], horizontal=True)
    with c2:
        stay = st.slider("切換速度", 3, 15, 7)
    
    if mode == "手動輸入":
        txt = st.text_area("訊息內容", "HELLO WORLD\\nSTAY COOL", height=100)
        data = txt.split('\\n')
    else:
        data = fetch_news()
        if st.button("🔄 刷新"): st.cache_data.clear()
        
    if st.button("🚀 套用", use_container_width=True): st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 顯示看板 ---
st.markdown("<h2 style='text-align: center; color: #444; margin-top: 30px;'>𓃥 白六新聞告示牌</h2>", unsafe_allow_html=True)

final_list = ["WHITE SIX NEWS"] + [s.strip().upper() for s in data if s.strip()]
render_flip_board(json.dumps(final_list), stay_sec=stay)
