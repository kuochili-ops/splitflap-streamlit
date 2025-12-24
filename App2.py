# 在 App2.py 頂部加入這個
import datetime

# 修改 fetch_multi_news 函數
@st.cache_data(ttl=300) # 縮短為 5 分鐘
def fetch_multi_news(sources_tuple):
    # 這裡我們不改 get_combined_news，但縮短 ttl
    return get_combined_news(list(sources_tuple))

# --- 在控制面板（expander）裡加入一個強大的刷新按鈕 ---
if st.button("🔥 徹底清除快取並更新新聞"):
    st.cache_data.clear()  # 這一行會強制刪除所有暫存的新聞
    st.rerun()
