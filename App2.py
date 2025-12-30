import streamlit as st
import json
import feedparser
from flip_board_2 import render_flip_board

# --- 1. 配置與 UI 隱藏 ---
st.set_page_config(page_title="白六新聞告示牌", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    header, [data-testid="stHeader"], footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; margin: 0 !important;}
    
    /* 懸浮調控面板：置於底部，預設隱藏 */
    .console-fixed {
        position: fixed; bottom: -280px; left: 50%; transform: translateX(-50%);
        width: 90%; max-width: 750px; background: rgba(25,25,25,0.98);
        padding: 20px; border-radius: 15px 15px 0 0; z-index: 9999;
        transition: 0.4s ease-in-out; border: 1px solid #444; color: white;
    }
    .console-fixed:hover, .console-fixed:focus-within { bottom: 0 !important; }
    
    /* 底部觸發區域 */
    .bottom-trigger { position: fixed; bottom: 0; width: 100%; height: 30px; z-index: 9998; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 數據獲取 ---
@st.cache_data(ttl=600)
def fetch_news():
    try:
        f = feedparser.parse("https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant")
        return [e.title.split(' - ')[0] for e in f.entries[:10]]
    except:
        return ["NEWS LOAD ERROR"]

# --- 3. 渲染控制面板 ---
st.markdown('<div class="bottom-trigger"></div>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="console-fixed">', unsafe_allow_html=True)
    st.markdown("<p style='color:gray; font-size:12px;'>⚙️ 設定面板 (滑鼠移至最下方開啟)</p>", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        mode = st.radio("模式", ["自動新聞", "手動訊息"], horizontal=True)
    with c2:
        stay = st.slider("每頁秒數", 3, 15, 7)
    
    if mode == "手動訊息":
        txt = st.text_area("自訂訊息 (每行一則)", "HELLO WORLD\\nSTAY CURIOUS", height=100)
        data = txt.split('\\n')
    else:
        data = fetch_news()
        if st.button("🔄 強制重新整理"): st.cache_data.clear()
        
    if st.button("🚀 套用設定並播放", use_container_width=True): st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. 看板顯示 ---
st.markdown("<h2 style='text-align: center; color: #444; margin-top: 30px; font-family: Microsoft JhengHei;'>𓃥 白六新聞告示牌</h2>", unsafe_allow_html=True)

# 第一則固定為標題
final_list = ["WHITE SIX NEWS"] + [s.strip().upper() for s in data if s.strip()]
render_flip_board(json.dumps(final_list), stay_sec=stay)
