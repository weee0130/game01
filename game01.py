import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Mahjong Solo AI - Complete Rules", layout="wide")

game_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { background: #0e3b22; color: white; font-family: 'Microsoft JhengHei', sans-serif; margin: 0; overflow: hidden; }
        #game-board { 
            position: relative; width: 100vw; height: 100vh; 
            background: radial-gradient(circle, #1a5e3a 0%, #0e3b22 100%);
            display: flex; justify-content: center; align-items: center;
        }
        
        #river { 
            width: 480px; height: 340px; border: 2px solid rgba(255,255,255,0.1);
            display: flex; flex-wrap: wrap; align-content: flex-start; padding: 10px;
            overflow-y: auto; background: rgba(0,0,0,0.1);
        }

        .tile { 
            width: 36px; height: 50px; background: white; border: 1px solid #333;
            border-radius: 4px; color: black; display: flex; flex-direction: column;
            justify-content: center; align-items: center; margin: 2px;
            font-weight: bold; font-size: 20px; position: relative; cursor: pointer;
            box-shadow: 2px 2px 0px #ccc; transition: transform 0.1s;
        }
        .tile:hover { transform: translateY(-8px); background: #f0f0f0; }
        .tile.ai { background: #2c5d44; color: transparent; cursor: default; box-shadow: none; border-color: #1a472a; }
        .tile.meld { background: #e0e0e0; transform: scale(0.9); cursor: default; } /* 副露 */

        .hand { position: absolute; display: flex; }
        .melds { display: flex; margin-left: 10px; } /* 顯示吃碰槓的牌 */

        #player-south { bottom: 20px; left: 50%; transform: translateX(-50%); }
        #player-north { top: 20px; left: 50%; transform: translateX(-50%) rotate(180deg); }
        #player-west { left: 20px; top: 50%; transform: translateY(-50%) rotate(90deg); }
        #player-east { right: 20px; top: 50%; transform: translateY(-50%) rotate(-90deg); }

        .river-tile { width: 28px; height: 40px; font-size: 14px; background: #eee; margin: 1px; color: black; display: flex; justify-content: center; align-items: center; border-radius: 2px; box-shadow: 1px 1px 0px #999; }
        
        #controls { position: absolute; bottom: 120px; right: 50px; display: flex; flex-direction: column; gap: 10px; z-index: 100; }
        #action-menu { 
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); 
            display: none; gap: 15px; background: rgba(0,0,0,0.7); padding: 20px; border-radius: 15px;
        }

        button { padding: 12px 24px; font-size: 20px; cursor: pointer; border: none; border-radius: 8px; font-weight: bold; box-shadow: 0 4px 0 #b8860b; transition: 0.1s; }
        button:active { transform: translateY(3px); box-shadow: none; }
        .btn-action { background: #4caf50; color: white; }
        .btn-pass { background: #888; color: white; }
        #btn-draw { background: #ffcc00; color: #333; }
        #btn-win { background: #ff4d4d; color: white; display: none; animation: pulse 1s infinite; }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }

        .type-m { color: #d32f2f; } .type-p { color: #1976d2; } .type-s { color: #388e3c; } .type-z { color: #333; }
        
        #win-overlay { 
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
            background: rgba(0,0,0,0.8); display: none; justify-content: center; 
            align-items: center; z-index: 200; flex-direction: column; 
        }
    </style>
</head>
<body>
    <div id="game-board">
        <div id="river"></div>
        
        <div id="player-north" class="hand"></div>
        <div id="player-east" class="hand"></div>
        <div id="player-west" class="hand"></div>
        <div id="player-south" class="hand"></div>

        <div id="action-menu"></div>

        <div id="controls">
            <button id="btn-draw" onclick="playerAction('draw')">摸牌</button>
            <button id="btn-win" onclick="playerAction('win')">胡牌！</button>
        </div>

        <div id="win-overlay">
            <h1 id="win-text" style="font-size: 60px; color: #ffcc00;">恭喜胡牌！</h1>
            <button onclick="location.reload()" style="background: white; color: black;">再玩一局</button>
        </div>
    </div>

    <script>
        const NAMES = {'m':'萬','p':'筒','s':'條','z1':'東','z2':'南','z3':'西','z4':'北','z5':'中','z6':'發','z7':'白'};
        let wall = [], hands = [[], [], [], []], river = [], melds = [[], [], [], []];
        let turn = 0; 
        let gameLocked = false;
        let pendingTile = null; // 待處理的捨牌（供吃碰槓判斷）

        // --- 核心胡牌邏輯 ---
        function checkWin(hand) {
            let counts = { m: Array(10).fill(0), p: Array(10).fill(0), s: Array(10).fill(0), z: Array(8).fill(0) };
            hand.forEach(tile => counts[tile.t][tile.v]++);
            for (let type in counts) {
                for (let v = 1; v < counts[type].length; v++) {
                    if (counts[type][v] >= 2) {
                        counts[type][v] -= 2;
                        if (canSub(counts)) return true;
                        counts[type][v] += 2;
                    }
                }
            }
            return false;
        }

        function canSub(counts) {
            for (let type in counts) {
                for (let v = 1; v < counts[type].length; v++) {
                    if (counts[type][v] === 0) continue;
                    if (counts[type][v] >= 3) {
                        counts[type][v] -= 3;
                        if (canSub(counts)) return true;
                        counts[type][v] += 3;
                    }
                    if (type !== 'z' && v <= 7 && counts[type][v+1] > 0 && counts[type][v+2] > 0) {
                        counts[type][v]--; counts[type][v+1]--; counts[type][v+2]--;
                        if (canSub(counts)) return true;
                        counts[type][v]++; counts[type][v+1]++; counts[type][v+2]++;
                    }
                    return false;
                }
            }
            return true;
        }

        // --- 吃碰槓判定邏輯 ---
        function checkActions(tile, isUpturn) {
            let actions = [];
            // 碰 & 槓
            let count = hands[0].filter(t => t.t === tile.t && t.v === tile.v).length;
            if (count >= 2) actions.push('碰');
            if (count === 3) actions.push('槓');
            
            // 吃 (僅限上家, 上家是 turn 3)
            if (isUpturn && tile.t !== 'z') {
                const h = hands[0].filter(t => t.t === tile.t);
                const vs = h.map(t => t.v);
                // 檢查三種組合: [v-2, v-1], [v-1, v+1], [v+1, v+2]
                if (vs.includes(tile.v-2) && vs.includes(tile.v-1)) actions.push('吃(左)');
                if (vs.includes(tile.v-1) && vs.includes(tile.v+1)) actions.push('吃(中)');
                if (vs.includes(tile.v+1) && vs.includes(tile.v+2)) actions.push('吃(右)');
            }
            return actions;
        }

        function initGame() {
            wall = [];
            ['m','p','s'].forEach(t => { for(let i=1;i<=9;i++) for(let n=0;n<4;n++) wall.push({t, v:i}); });
            for(let i=1;i<=7;i++) for(let n=0;n<4;n++) wall.push({t:'z', v:i});
            wall.sort(() => Math.random() - 0.5);

            for(let i=0; i<4; i++) {
                hands[i] = wall.splice(0, 16);
                sortHand(hands[i]);
            }
            render();
        }

        function sortHand(hand) {
            hand.sort((a,b) => {
                const order = {'m':0, 'p':1, 's':2, 'z':3};
                return order[a.t] - order[b.t] || a.v - b.v;
            });
        }

        function render() {
            const ids = ['south', 'east', 'north', 'west'];
            ids.forEach((id, i) => {
                const el = document.getElementById(`player-${id}`);
                el.innerHTML = '';
                
                // 顯示手牌
                hands[i].forEach((tile, idx) => {
                    const d = document.createElement('div');
                    if(i === 0) {
                        d.className = `tile type-${tile.t}`;
                        d.innerHTML = `<span>${tile.t==='z'?NAMES['z'+tile.v]:tile.v}</span><small style="font-size:10px">${tile.t==='z'?'':NAMES[tile.t]}</small>`;
                        d.onclick = () => playerAction('discard', idx);
                    } else {
                        d.className = 'tile ai';
                    }
                    el.appendChild(d);
                });

                // 顯示副露 (吃碰槓的牌)
                const meldBox = document.createElement('div');
                meldBox.className = 'melds';
                melds[i].forEach(m => {
                    m.forEach(tile => {
                        const d = document.createElement('div');
                        d.className = `tile meld type-${tile.t}`;
                        d.innerHTML = `<span>${tile.t==='z'?NAMES['z'+tile.v]:tile.v}</span>`;
                        meldBox.appendChild(d);
                    });
                });
                el.appendChild(meldBox);
            });

            const riverEl = document.getElementById('river');
            riverEl.innerHTML = '';
            river.forEach(tile => {
                const d = document.createElement('div');
                d.className = `river-tile type-${tile.t}`;
                d.innerText = tile.t==='z'?NAMES['z'+tile.v]:tile.v + NAMES[tile.t][0];
                riverEl.appendChild(d);
            });
            
            document.getElementById('btn-draw').style.display = (turn === 0 && hands[0].length % 3 === 1) ? 'block' : 'none';
            document.getElementById('btn-win').style.display = (hands[0].length % 3 === 2 && checkWin(hands[0])) ? 'block' : 'none';
        }

        async function playerAction(act, idx) {
            if(gameLocked) return;
            if(act === 'draw') {
                hands[0].push(wall.pop());
                render();
            } else if(act === 'discard') {
                if(hands[0].length % 3 !== 2) return;
                const tile = hands[0].splice(idx, 1)[0];
                river.push(tile);
                sortHand(hands[0]);
                turn = 1;
                render();
                await aiCycle(tile);
            } else if(act === 'win') {
                document.getElementById('win-overlay').style.display = 'flex';
                gameLocked = true;
            }
        }

        function showActionMenu(actions, tile) {
            const menu = document.getElementById('action-menu');
            menu.innerHTML = '';
            menu.style.display = 'flex';
            
            actions.forEach(a => {
                const btn = document.createElement('button');
                btn.className = 'btn-action';
                btn.innerText = a;
                btn.onclick = () => handleMeld(a, tile);
                menu.appendChild(btn);
            });

            const pass = document.createElement('button');
            pass.className = 'btn-pass';
            pass.innerText = '過';
            pass.onclick = () => {
                menu.style.display = 'none';
                gameLocked = false;
            };
            menu.appendChild(pass);
            gameLocked = true;
        }

        function handleMeld(type, tile) {
            document.getElementById('action-menu').style.display = 'none';
            river.pop(); // 從河中取回牌
            let component = [];
            
            if (type === '碰') {
                component = [tile, tile, tile];
                for(let i=0; i<2; i++) hands[0].splice(hands[0].findIndex(t => t.t===tile.t && t.v===tile.v), 1);
            } else if (type === '槓') {
                component = [tile, tile, tile, tile];
                for(let i=0; i<3; i++) hands[0].splice(hands[0].findIndex(t => t.t===tile.t && t.v===tile.v), 1);
            } else { // 吃
                let v = tile.v;
                let vs = (type==='吃(左)') ? [v-2, v-1] : (type==='吃(中)') ? [v-1, v+1] : [v+1, v+2];
                component = [tile];
                vs.forEach(val => {
                    component.push(hands[0].splice(hands[0].findIndex(t => t.t===tile.t && t.v===val), 1)[0]);
                });
            }
            
            melds[0].push(component);
            sortHand(hands[0]);
            turn = 0; // 輪到玩家出牌
            gameLocked = false;
            render();
        }

        async function aiCycle(lastDiscard) {
            gameLocked = true;
            while(turn !== 0) {
                await new Promise(r => setTimeout(r, 800));
                
                // 檢查玩家是否可以對 AI 的捨牌進行吃碰槓
                if (lastDiscard) {
                    const playerActions = checkActions(lastDiscard, turn === 3);
                    if (playerActions.length > 0) {
                        showActionMenu(playerActions, lastDiscard);
                        // 這裡會 return 並等待玩家點擊按鈕，之後會再由 handleMeld 恢復
                        return;
                    }
                }

                if(wall.length === 0) { alert("流局！"); location.reload(); return; }
                
                hands[turn].push(wall.pop());
                if (checkWin(hands[turn])) {
                    document.getElementById('win-text').innerText = `電腦 ${['南','東','北','西'][turn]}家 胡牌了！`;
                    document.getElementById('win-overlay').style.display = 'flex';
                    return;
                }

                const dIdx = Math.floor(Math.random() * hands[turn].length);
                lastDiscard = hands[turn].splice(dIdx, 1)[0];
                river.push(lastDiscard);
                sortHand(hands[turn]);
                turn = (turn + 1) % 4;
                render();
            }
            gameLocked = false;
        }

        initGame();
    </script>
</body>
</html>
"""

components.html(game_code, height=750)
