import streamlit as st
import time
import random

# --- 頁面設定 ---
st.set_page_config(page_title="節奏打鐵匠", page_icon="⚒️")

# --- 初始化遊戲狀態 ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'combo' not in st.session_state:
    st.session_state.combo = 0
if 'feedback' not in st.session_state:
    st.session_state.feedback = "準備好打鐵了嗎？"
if 'target_pos' not in st.session_state:
    st.session_state.target_pos = random.randint(70, 90) # 目標完美區間

# --- 遊戲邏輯 ---
def hit_anvil(val):
    target = st.session_state.target_pos
    diff = abs(val - target)
    
    if diff <= 3:
        st.session_state.score += 100 * (st.session_state.combo + 1)
        st.session_state.combo += 1
        st.session_state.feedback = "🔥 PERFECT! 完美的打擊！"
    elif diff <= 8:
        st.session_state.score += 50
        st.session_state.combo += 1
        st.session_state.feedback = "🔨 GOOD! 力道不錯。"
    else:
        st.session_state.combo = 0
        st.session_state.feedback = "💨 MISS... 揮空了。"
    
    # 每次打擊後隨機移動目標區
    st.session_state.target_pos = random.randint(10, 90)

# --- UI 介面 ---
st.title("⚒️ 節奏打鐵匠 (Rhythm Blacksmith)")
st.write(f"運用你的技藝，打造傳說級武器吧！")

# 顯示分數看板
col1, col2 = st.columns(2)
col1.metric("當前分數", st.session_state.score)
col2.metric("連擊 (Combo)", st.session_state.combo)

st.divider()

# 遊戲核心元件：滑桿模擬節奏（在 Streamlit 中，我們利用 slider 的動態感）
# 玩家需要將滑桿拉到正確位置並點擊「打擊」
st.write(f"### 目標精準度：{st.session_state.target_pos}% 附近")
current_val = st.slider("調整力道與角度", 0, 100, 50, help="嘗試對準目標區間！")

if st.button("⚒️ 落槌打擊！", use_container_width=True):
    hit_anvil(current_val)

# 顯示回饋
if "PERFECT" in st.session_state.feedback:
    st.success(st.session_state.feedback)
elif "GOOD" in st.session_state.feedback:
    st.info(st.session_state.feedback)
else:
    st.warning(st.session_state.feedback)

# --- 遊戲進度視覺化 ---
st.progress(st.session_state.target_pos / 100)
st.caption("上方進度條顯示下一錘的「完美點」位置")

# 重置按鈕
if st.sidebar.button("重置遊戲"):
    st.session_state.score = 0
    st.session_state.combo = 0
    st.session_state.feedback = "重新開始..."
    st.rerun()
