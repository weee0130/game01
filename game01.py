import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Mahjong Solo AI - Win Logic", layout="wide")

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
            width: 450px; height: 320px; border: 2px solid rgba(255,255,255,0.1);
            display: flex; flex-wrap: wrap; align-content: flex-start; padding: 10px;
            overflow-y: auto;
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
        
        .hand { position: absolute; display: flex; }
        #player-south { bottom: 20px; left: 50%; transform: translateX(-50%); }
        #player-north { top: 20px; left: 50%; transform: translateX(-50%) rotate(180deg); }
        #player-west { left: 20px; top: 50%; transform: translateY(-50%) rotate(90deg); }
        #player-east { right: 20px; top: 50%; transform: translateY(-50%) rotate(-90deg); }

        .river-tile { width: 26px; height: 38px; font-size: 14px; background: #eee; margin: 1px; color: black; display: flex; justify-content: center; align-items: center; border-radius: 2px; box-shadow: 1px 1px 0px #999; }
        
        #controls { position: absolute; bottom: 120px; right: 50px; display: flex; flex-direction: column; gap: 10px; }
        button { padding: 12px 24px; font-size: 20px; cursor: pointer; border: none; border-radius: 8px; font-weight: bold; box-shadow: 0 4px 0 #b8860b; transition: 0.1s; }
        button:active { transform: translateY(3px); box-shadow: none; }
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
            align-items: center; z-index: 100; flex-direction: column; 
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

        <div id="controls">
            <button id="btn-draw" onclick="playerAction('draw')">摸牌</button>
            <button id="btn-win" onclick="playerAction('win')">胡牌！</button>
        </div>

        <div id="win-overlay">
            <h1 style="font-size: 60px; color: #ffcc00;">恭喜胡牌！</h1>
            <button onclick="location.reload()" style="background: white; color: black;">再玩一局</button>
        </div>
    </div>

    <script>
        const NAMES = {'m':'萬','p':'筒','s':'條','z1':'東','z2':'南','z3':'西','z4':'北','z5':'中','z6':'發','z7':'白'};
        let wall = [], hands = [[], [], [], []], river = [];
        let turn = 0; 
        let gameLocked = false;

        // --- 胡牌判定核心邏輯 ---
        function checkWin(hand) {
            // 1. 整理牌張數量
            let counts = { m: Array(10).fill(0), p: Array(10).fill(0), s: Array(10).fill(0), z: Array(8).fill(0) };
            hand.forEach(tile => counts[tile.t][tile.v]++);

            // 2. 遍歷可能的「將」（對子）
            for (let type in counts) {
                for (let v = 1; v < counts[type].length; v++) {
                    if (counts[type][v] >= 2) {
                        // 嘗試以此為將
                        counts[type][v] -= 2;
                        if (canSub(counts)) return true;
                        counts[type][v] += 2;
                    }
                }
            }
            return false;
        }

        // 遞迴拆解順子與刻子
        function canSub(counts) {
            for (let type in counts) {
                for (let v = 1; v < counts[type].length; v++) {
                    if (counts[type][v] === 0) continue;

                    // 1. 嘗試拆解刻子
                    if (counts[type][v] >= 3) {
                        counts[type][v] -= 3;
                        if (canSub(counts)) return true;
                        counts[type][v] += 3;
                    }

                    // 2. 嘗試拆解順子 (字牌沒有順子)
                    if (type !== 'z' && v <= 7 && counts[type][v+1] > 0 && counts[type][v+2] > 0) {
                        counts[type][v]--;
                        counts[type][v+1]--;
                        counts[type][v+2]--;
                        if (canSub(counts)) return true;
                        counts[type][v]++;
                        counts[type][v+1]++;
                        counts[type][v+2]++;
                    }
                    
                    // 如果這張牌無法被消耗掉，代表這組牌不能胡
                    return false;
                }
            }
            return true;
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
            });

            const riverEl = document.getElementById('river');
            riverEl.innerHTML = '';
            river.forEach(tile => {
                const d = document.createElement('div');
                d.className = `river-tile type-${tile.t}`;
                d.innerText = tile.t==='z'?NAMES['z'+tile.v]:tile.v + NAMES[tile.t][0];
                riverEl.appendChild(d);
            });
            
            // 按鈕顯示邏輯
            document.getElementById('btn-draw').style.display = (turn === 0 && hands[0].length === 16) ? 'block' : 'none';
            
            // 判斷玩家是否胡牌
            if (hands[0].length === 17 && checkWin(hands[0])) {
                document.getElementById('btn-win').style.display = 'block';
            } else {
                document.getElementById('btn-win').style.display = 'none';
            }
        }

        async function playerAction(act, idx) {
            if(gameLocked) return;
            if(act === 'draw') {
                hands[0].push(wall.pop());
                render();
            } else if(act === 'discard') {
                if(hands[0].length < 17) return;
                river.push(hands[0].splice(idx, 1)[0]);
                sortHand(hands[0]);
                turn = 1;
                render();
                await aiCycle();
            } else if(act === 'win') {
                document.getElementById('win-overlay').style.display = 'flex';
                gameLocked = true;
            }
        }

        async function aiCycle() {
            gameLocked = true;
            while(turn !== 0) {
                await new Promise(r => setTimeout(r, 800));
                if(wall.length === 0) { alert("流局！"); location.reload(); return; }
                
                hands[turn].push(wall.pop());
                
                // AI 簡易胡牌檢測
                if (checkWin(hands[turn])) {
                    alert(`電腦 ${['南','東','北','西'][turn]}家 胡牌了！`);
                    location.reload();
                    return;
                }

                const discardIdx = Math.floor(Math.random() * hands[turn].length);
                river.push(hands[turn].splice(discardIdx, 1)[0]);
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
