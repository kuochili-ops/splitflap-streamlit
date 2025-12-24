# 在 App2.py 呼叫端加入此判斷
if "last_content" not in st.session_state:
    st.session_state.last_content = ""

# 只有當內容真的改變時，才重新計算 safe_content
current_json = json.dumps(safe_content)
if current_json != st.session_state.last_content:
    st.session_state.last_content = current_json
    
render_flip_board(current_json, stay_sec=8.0)
