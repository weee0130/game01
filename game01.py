import streamlit as st
import random
import time

# --- 頁面設定 ---
st.set_page_config(page_title="小動物記憶大挑戰", page_icon="🐶")

# --- 遊戲資料 ---
ANIMALS = ["🐶", "🐱", "🐭", "🐹", "🐰", "🦊"] * 2  # 6對動物
GRID_SIZE = 4  # 4x3 的網格

# --- 初始化遊戲狀態 ---
if 'cards' not in st.session_state:
    random.shuffle(ANIMALS)
    st.session_state.cards = ANIMALS # 隱藏的答案
    st.session_state.revealed = [False] * 12 # 目前哪些是翻開的
    st.session_state.matched = [False] * 12 # 哪些已經配對成功
    st.session_state.selection = [] # 儲存當前點擊的索引
    st.session_state.attempts = 0 # 嘗試次數

# --- 遊戲邏輯 ---
def handle_click(idx):
    # 防止重複點擊已翻開或已配對的牌
    if st.session_state.revealed[idx] or st.session_state.matched[idx]:
        return
    
    # 翻開這張牌
    st.session_state.revealed[idx] = True
    st.session_state.selection.append(idx)

    # 如果翻了兩張，檢查是否相同
    if len(st.session_state.selection) == 2:
        st.session_state.attempts += 1
        idx1, idx2 = st.session_state.selection
        
        if st.session_state.cards[idx1] == st.session_state.cards[idx2]:
            # 配對成功
            st.session_state.matched[idx1] = True
            st.session_state.matched[idx2] = True
            st.toast("太棒了！找到一對了！ 🎉")
        else:
            # 配對失敗，等一下下再翻回去 (透過頁面刷新處理)
            st.session_state.revealed[idx1] = False
            st.session_state.revealed[idx2] = False
            st.toast("再試一次看看 ✍️")
        
        # 清空選擇
        st.session_state.selection = []

# --- UI 介面 ---
st.title("🐶 小動物記憶大挑戰")
st.write(f"小朋友，找出所有成雙成對的小動物吧！你已經挑戰了 **{st.session_state.attempts}** 次。")

# 建立遊戲網格
cols = st.columns(4)

for i in range(12):
    with cols[i % 4]:
        # 決定按鈕顯示什麼圖案
        # 如果是已配對或正被選中，顯示動物；否則顯示「？」
        is_visible = st.session_state.revealed[i] or st.session_state.matched[i]
        label = st.session_state.cards[i] if is_visible else "❓"
        
        # 兒童友善：已配對成功的卡片會變色或停用
        if st.button(label, key=f"card_{i}", use_container_width=True):
            handle_click(i)
            st.rerun()

st.divider()

# 檢查是否全破
if all(st.session_state.matched):
    st.balloons()
    st.success(f"恭喜你完成挑戰！總共花了 {st.session_state.attempts} 次嘗試。")
    if st.button("再玩一次"):
        # 重置所有狀態
        del st.session_state.cards
        st.rerun()

# --- 側邊欄：遊戲說明 ---
with st.sidebar:
    st.header("遊戲說明")
    st.write("1. 點擊 ❓ 翻開小動物。")
    st.write("2. 記住牠們的位置。")
    st.write("3. 連續翻開兩隻一樣的就得分囉！")
