import streamlit as st
import json
import feedparser
from flip_board_2 import render_flip_board

# --- 1. 頁面配置 ---
st.set_page_config(page_title="白六新聞告示牌", layout="wide")

# 強制隱藏 UI 並設定隱藏面板 CSS
st.markdown("""
    <style>
    header, footer, [data-testid="stHeader"] {visibility: hidden; display: none;}
    .block-container {padding: 0 !important;}
    
    /* 底部懸浮面板：預設隱藏 (-260px) */
    .console-panel {
        position: fixed; bottom: -260px; left: 50%; transform: translateX(-50%);
        width: 90%; max-width: 700px; background: rgba(30,30,30,0.98);
        padding: 20px; border-radius: 20px 20px 0 0; z-index: 999;
        transition: 0.4s; border: 1px solid #444;
    }
    .console-panel:hover, .console-panel:focus-within { bottom: 0; }
    
    /* 感應區 */
    .trigger { position: fixed; bottom: 0; width: 100%; height: 20px; z-index: 998; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 抓取新聞 ---
def fetch_news():
    try:
        f = feedparser.parse("https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant")
        return [e.title.split(' - ')[0] for e in f.entries[:8]]
    except:
        return ["新聞載入失敗"]

# --- 3. 懸浮控制面板 ---
st.markdown('<div class="trigger"></div>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="console-panel">', unsafe_allow_html=True)
    st.markdown("<small style='color:gray'>⚙️ 觸碰此處調整設定</small>", unsafe_allow_html=True)
    mode = st.radio("模式", ["即時新聞", "手動輸入"], horizontal=True)
    stay = st.slider("切換秒數", 3, 15, 7)
    
    raw_list = []
    if mode == "手動輸入":
        txt = st.text_area("每行一則訊息", "HELLO WORLD\nSTREAMLIT FLIP")
        raw_list = txt.split('\n')
    else:
        raw_list = fetch_news()
    
    if st.button("🚀 套用設定"):
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. 顯示看板 ---
st.markdown("<h3 style='text-align:center; color:#555;'>𓃥 白六新聞 / 訊息告示牌</h3>", unsafe_allow_html=True)

processed = ["WHITE SIX NEWS"] + [s.strip().upper() for s in raw_list if s.strip()]
render_flip_board(json.dumps(processed), stay_sec=stay)
