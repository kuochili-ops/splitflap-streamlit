import streamlit as st
import json
import feedparser
from flip_board_2 import render_flip_board

# --- 1. 頁面配置 ---
st.set_page_config(page_title="白六新聞告示牌", layout="wide", initial_sidebar_state="collapsed")

# 隱藏原生標籤並設定底部感應面板
st.markdown("""
    <style>
    header, [data-testid="stHeader"], footer {visibility: hidden; display: none;}
    .block-container {padding: 0 !important; margin: 0 !important;}
    
    /* 底部面板預設隱藏 */
    .console-fixed {
        position: fixed; bottom: -300px; left: 50%; transform: translateX(-50%);
        width: 90%; max-width: 750px; background: rgba(20,20,20,0.95);
        padding: 20px; border-radius: 20px 20px 0 0; z-index: 9999;
        transition: 0.5s ease; border: 1px solid #333;
    }
    .console-fixed:hover, .console-fixed:focus-within { bottom: 0px !important; }
    
    /* 底部感應區 */
    .trigger-zone { position: fixed; bottom: 0; width: 100%; height: 30px; z-index: 9998; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 獲取資料 ---
def fetch_news():
    try:
        f = feedparser.parse("https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant")
        return [e.title.split(' - ')[0] for e in f.entries[:10]]
    except:
        return ["新聞載入中..."]

# --- 3. 懸浮面板 UI ---
st.markdown('<div class="trigger-zone"></div>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="console-fixed">', unsafe_allow_html=True)
    st.markdown("<p style='color:gray; margin:0;'>⚙️ 設定面板 (滑鼠移入開啟)</p>", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        mode = st.radio("模式", ["自動新聞", "手動訊息"], horizontal=True)
    with c2:
        stay = st.slider("切換速度", 3, 15, 7)
    
    if mode == "手動訊息":
        txt = st.text_area("訊息(每行一則)", "HELLO WORLD\\nWELCOME")
        data_list = txt.split('\\n')
    else:
        data_list = fetch_news()
        if st.button("🔄 刷新新聞"): st.cache_data.clear()
        
    if st.button("🚀 套用並重新載入", use_container_width=True): st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. 數據處理 ---
title_msg = "𓃥 WHITE SIX NEWS"
processed = [title_msg] + [s.strip().upper() for s in data_list if s.strip()]

# --- 5. 渲染 ---
st.markdown("<h2 style='text-align: center; color: #444; margin: 30px 0;'>𓃥 白六新聞告示牌</h2>", unsafe_allow_html=True)
render_flip_board(json.dumps(processed), stay_sec=stay)
