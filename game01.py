import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Mahjong Logic Sim", layout="wide")

st.title("🀄 台灣麻將邏輯模擬器")
st.caption("這是一個展示麻將發牌、排序與摸牌邏輯的開發原型。")

game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background: #1a472a; color: white; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; margin: 0; }
        #table { width: 90vw; height: 400px; border: 10px solid #0d2b1a; border-radius: 20px; position: relative; margin-top: 20px; display: flex; justify-content: center; align-items: flex-end; padding-bottom: 20px; }
        .tile { width: 50px; height: 70px; background: white; border: 2px solid #333; border-radius: 5px; color: black; display: flex; flex-direction: column; justify-content: center; align-items: center; margin: 2px; cursor: pointer; transition: 0.2s; font-weight: bold; font-size: 24px; }
        .tile:hover { transform: translateY(-10px); background: #eee; }
        .tile.discarded { width: 35px; height: 50px; font-size: 16px; cursor: default; }
        #discard-pile { position: absolute; top: 50px; width: 60%; display: flex; flex-wrap: wrap; justify-content: center; }
        #controls { margin-top: 20px; }
        button { padding: 10px 20px; font-size: 16px; cursor: pointer; background: #c6a664; border: none; border-radius: 5px; font-weight: bold; }
        .tile-type-m { color: #d32f2f; } /* 萬 */
        .tile-type-p { color: #1976d2; } /* 筒 */
        .tile-type-s { color: #388e3c; } /* 條 */
        .tile-type-z { color: #7b1fa2; } /* 字 */
    </style>
</head>
<body>
    <div id="table">
        <div id="discard-pile"></div>
        <div id="player-hand" style="display: flex;"></div>
    </div>
    <div id="controls">
        <button onclick="drawTile()">摸牌</button>
        <button onclick="resetGame()">重新洗牌</button>
    </div>

    <script>
        const TYPES = ['m', 'p', 's', 'z']; // 萬, 筒, 條, 字
        const NAMES = {
            'm': '萬', 'p': '筒', 's': '條',
            'z1': '東', 'z2': '南', 'z3': '西', 'z4': '北', 'z5': '中', 'z6': '發', 'z7': '白'
        };
        
        let wall = [];
        let hand = [];
        let discards = [];

        function initWall() {
            wall = [];
            // 萬筒條 1-9
            for (let t of ['m', 'p', 's']) {
                for (let i = 1; i <= 9; i++) {
                    for (let n = 0; n < 4; n++) wall.push({type: t, val: i});
                }
            }
            // 字牌 東南西北中發白
            for (let i = 1; i <= 7; i++) {
                for (let n = 0; n < 4; n++) wall.push({type: 'z', val: i});
            }
            // 洗牌
            wall.sort(() => Math.random() - 0.5);
        }

        function sortHand() {
            hand.sort((a, b) => {
                if (a.type !== b.type) return TYPES.indexOf(a.type) - TYPES.indexOf(b.type);
                return a.val - b.val;
            });
        }

        function render() {
            const handEl = document.getElementById('player-hand');
            handEl.innerHTML = '';
            hand.forEach((tile, index) => {
                const div = document.createElement('div');
                div.className = `tile tile-type-${tile.type}`;
                div.innerHTML = `<span>${tile.type === 'z' ? NAMES['z'+tile.val] : tile.val}</span><small>${tile.type !== 'z' ? NAMES[tile.type] : ''}</small>`;
                div.onclick = () => discard(index);
                handEl.appendChild(div);
            });

            const discardEl = document.getElementById('discard-pile');
            discardEl.innerHTML = '';
            discards.forEach(tile => {
                const div = document.createElement('div');
                div.className = `tile discarded tile-type-${tile.type}`;
                div.innerHTML = tile.type === 'z' ? NAMES['z'+tile.val] : tile.val;
                discardEl.appendChild(div);
            });
        }

        function drawTile() {
            if (wall.length > 0 && hand.length < 17) {
                hand.push(wall.pop());
                sortHand();
                render();
            }
        }

        function discard(index) {
            discards.push(hand.splice(index, 1)[0]);
            render();
        }

        function resetGame() {
            initWall();
            hand = [];
            discards = [];
            for (let i = 0; i < 16; i++) hand.push(wall.pop());
            sortHand();
            render();
        }

        resetGame();
    </script>
</body>
</html>
"""

components.html(game_code, height=600)

st.sidebar.markdown("""
### 🀄 麻將開發手冊
這是一個「台灣麻將 (16張)」的邏輯原型：
1. **洗牌演算法**：使用 `Math.random() - 0.5` 對 144 張牌進行亂數排序。
2. **排序邏輯**：自動依照「萬、筒、條、字」進行手牌整理。
3. **互動機制**：
   - 點擊按鈕 **摸牌**。
   - 點擊手牌即可 **出牌** 到牌桌中央。

### 接下來的挑戰：
一個完整的麻將遊戲還需要：
- **聽牌判定**：計算 $3n+2$ 的結構（刻子、順子、雀瑟）。
- **胡牌算法**：判斷平胡、大三元等台數。
- **多人連線**：使用 WebSocket 處理四人即時對戰。
""")
