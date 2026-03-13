import streamlit as st
import random
import time

# 設定網頁標題與風格
st.set_page_config(page_title="奇幻森林尋寶記", page_icon="🌳", layout="centered")

# 自定義 CSS 讓按鈕看起來更大、更適合點擊
st.markdown("""
    <style>
    div.stButton > button {
        height: 100px;
        width: 100%;
        font-size: 50px !important;
        border-radius: 15px;
        border: 2px solid #4CAF50;
        background-color: #f0f9f0;
        transition: transform 0.2s;
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        border-color: #2E7D32;
    }
    .main-title {
        text-align: center;
        color: #2E7D32;
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }
    .score-box {
        background-color: #e8f5e9;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        color: #1b5e20;
    }
    </style>
    """, unsafe_allow_html=True)

# 1. 準備寶藏圖案 (8對 = 16張)
TREASURES = ["🍎", "🐶", "🎈", "🚗", "🧸", "🍦", "🌈", "🦋"] * 2

# 2. 初始化遊戲狀態
if 'board' not in st.session_state:
    random.shuffle(TREASURES)
    st.session_state.board = TREASURES          # 寶藏位置
    st.session_state.flipped = [False] * 16     # 目前翻開的
    st.session_state.matched = [False] * 16     # 已成功配對的
    st.session_state.selected_indices = []      # 當前選中的索引
    st.session_state.clicks = 0                 # 總點擊次數
    st.session_state.game_over = False

# 遊戲邏輯函數
def click_card(idx):
    # 點擊限制：不能點已配對的、不能點已翻開的、不能在一次點超過兩張
    if st.session_state.matched[idx] or st.session_state.flipped[idx] or len(st.session_state.selected_indices) >= 2:
        return

    # 翻開當前卡片
    st.session_state.flipped[idx] = True
    st.session_state.selected_indices.append(idx)
    st.session_state.clicks += 1

    # 當翻開兩張時
    if len(st.session_state.selected_indices) == 2:
        idx1, idx2 = st.session_state.selected_indices
        
        if st.session_state.board[idx1] == st.session_state.board[idx2]:
            # 配對成功！
            st.session_state.matched[idx1] = True
            st.session_state.matched[idx2] = True
            st.session_state.selected_indices = []
            if all(st.session_state.matched):
                st.session_state.game_over = True
        else:
            # 配對失敗，由前端按鈕邏輯處理或手動重置
            pass

def reset_mismatched():
    # 如果選了兩張且沒配對成功，將它們翻回去
    if len(st.session_state.selected_indices) == 2:
        idx1, idx2 = st.session_state.selected_indices
        if not (st.session_state.board[idx1] == st.session_state.board[idx2]):
            time.sleep(0.6) # 給小朋友一點時間記住圖案
            st.session_state.flipped[idx1] = False
            st.session_state.flipped[idx2] = False
        st.session_state.selected_indices = []
        st.rerun()

# --- 主畫面 UI ---
st.markdown("<h1 class='main-title'>🌳 奇幻森林尋寶記</h1>", unsafe_allow_html=True)

col_info1, col_info2 = st.columns(2)
with col_info1:
    st.markdown(f"<div class='score-box'>總共點擊了：{st.session_state.clicks} 次</div>", unsafe_allow_html=True)
with col_info2:
    matches_found = sum(st.session_state.matched) // 2
    st.markdown(f"<div class='score-box'>找到寶藏：{matches_found} / 8</div>", unsafe_allow_html=True)

st.write("") # 空行

# 建立 4x4 遊戲網格
for row in range(4):
    cols = st.columns(4)
    for col in range(4):
        idx = row * 4 + col
        
        # 決定顯示內容
        if st.session_state.matched[idx]:
            btn_label = "✅" # 已配對
            btn_key = f"matched_{idx}"
            cols[col].button(btn_label, key=btn_key, disabled=True)
        elif st.session_state.flipped[idx]:
            btn_label = st.session_state.board[idx] # 顯示圖案
            cols[col].button(btn_label, key=f"flip_{idx}")
        else:
            # 未翻開，顯示草叢
            if cols[col].button("🌿", key=f"hide_{idx}"):
                click_card(idx)
                st.rerun()

# 檢查是否需要翻回去
if len(st.session_state.selected_indices) == 2:
    reset_mismatched()

# --- 遊戲結束 ---
if st.session_state.game_over:
    st.balloons()
    st.success("🎉 太厲害了！你找齊了所有森林寶藏！")
    
    # 評價系統
    if st.session_state.clicks <= 24:
        st.info("🏆 稱號：森林記憶大師 (超級聰明！)")
    elif st.session_state.clicks <= 36:
        st.info("🏅 稱號：森林小偵探 (表現優異！)")
    else:
        st.info("🌱 稱號：森林實習生 (多練習會更棒喔！)")

    if st.button("再玩一次！"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# 側邊欄
with st.sidebar:
    st.header("遊戲小秘訣")
    st.write("1. 點擊草叢 🌿 尋找寶藏。")
    st.write("2. 兩兩一組，找到一樣的寶藏。")
    st.write("3. 看看你能用幾次就完成挑戰！")
    if st.button("重新洗牌"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
