import urllib.request # 加入這個庫來處理請求標頭

def get_combined_news(selected_sources):
    """抓取多個來源的新聞並合併"""
    all_titles = []
    if not selected_sources:
        return ["請選擇新聞來源"]

    # 模擬瀏覽器的 Header，防止被伺服器阻擋
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    for name in selected_sources:
        url = NEWS_SOURCES[name]
        # 只有非公視的來源才加時間戳記，避免公視伺服器報錯
        if "pts.org.tw" not in url:
            url += f"?t={int(time.time())}"
        
        try:
            time.sleep(0.5) # 稍微增加延遲
            
            # 使用 urllib 抓取內容，手動加入 Headers
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                xml_data = response.read()
                
            # 解析抓到的 XML
            feed = feedparser.parse(xml_data)
            
            if not feed.entries:
                # 偵錯用：如果還是沒資訊，嘗試抓取另一種公視 RSS 格式
                continue
                
            source_tag = name.split('-')[1]
            count = 0
            for entry in feed.entries:
                if count >= 5: break
                
                # 優先抓取標題，並處理 HTML 標籤
                title_text = entry.get('title', '')
                clean_title = re.sub(r'<[^>]+>', '', title_text)
                clean_title = re.sub(r'[^\u4e00-\u9fa5A-Z0-9\s]', '', clean_title).upper()
                
                if clean_title.strip():
                    all_titles.append(f"[{source_tag}] {clean_title}")
                    count += 1
        except Exception as e:
            # st.error(f"抓取 {name} 失敗: {e}") # 需要測試時可以打開這行
            continue
            
    return all_titles if all_titles else ["暫無新聞資料，請點擊下方按鈕刷新"]
