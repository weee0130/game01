import streamlit as st
import streamlit.components.v1 as components

# 設定頁面
st.set_page_config(page_title="醫療大冒險：三合一急診室", page_icon="🏥", layout="centered")

st.title("🏥 醫療大冒險：三合一急診室")
st.write("點擊下方按鈕切換不同的醫療任務，挑戰你的專業技術！")

# 遊戲的核心 HTML 與 JavaScript 代碼
game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; background: #222; display: flex; flex-direction: column; justify-content: center; align-items: center; overflow: hidden; font-family: 'Arial', sans-serif; cursor: crosshair; }
        canvas { border: 5px solid #444; background-color: #f5d0b0; border-radius: 20px; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
        #ui { position: absolute; top: 10px; width: 500px; display: flex; justify-content: space-between; color: #ff0000; font-weight: bold; font-size: 20px; text-shadow: 1px 1px 2px black; pointer-events: none; }
        
        #game-selector { margin-bottom: 10px; display: flex; gap: 10px; }
        .game-btn { padding: 8px 15px; background: #444; color: white; border: 2px solid #666; border-radius: 5px; cursor: pointer; }
        .game-btn.active { background: #2E7D32; border-color: #4CAF50; }

        #toolbar { position: absolute; bottom: 20px; display: flex; gap: 10px; background: rgba(0,0,0,0.7); padding: 10px; border-radius: 15px; }
        .tool { width: 60px; height: 60px; background: #eee; border: 3px solid #666; border-radius: 10px; display: flex; justify-content: center; align-items: center; font-size: 30px; cursor: pointer; transition: 0.2s; }
        .tool.active { background: #fff; border-color: #00ff00; transform: translateY(-5px); box-shadow: 0 5px 10px rgba(0,255,0,0.3); }
        
        #instruction { position: absolute; top: 50px; color: white; background: rgba(0,0,0,0.5); padding: 5px 10px; border-radius: 5px; font-size: 14px; }
    </style>
</head>
<body>
    <div id="game-selector">
        <button class="game-btn active" onclick="switchGame('SURGERY')">外科手術</button>
        <button class="game-btn" onclick="switchGame('DENTAL')">牙科拔牙</button>
        <button class="game-btn" onclick="switchGame('EYE')">眼科清除</button>
    </div>

    <div id="ui">
        <div>❤️ HP: <span id="hp">100</span></div>
        <div>⏱️ TIME: <span id="timer">60</span>s</div>
    </div>
    
    <div id="instruction">任務：切開傷口並取出玻璃</div>
    
    <canvas id="gameCanvas"></canvas>

    <div id="toolbar">
        <!-- 工具會根據遊戲模式動態變化 -->
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const hpEl = document.getElementById('hp');
        const timerEl = document.getElementById('timer');
        const instEl = document.getElementById('instruction');
        const toolbar = document.getElementById('toolbar');

        canvas.width = 600;
        canvas.height = 400;

        let currentGame = 'SURGERY';
        let hp = 100;
        let timeLeft = 60;
        let currentTool = '';
        let isMouseDown = false;
        let gameActive = true;

        // 遊戲數據
        let gameState = {};

        const TOOL_CONFIG = {
            'SURGERY': [
                { id: 'knife', icon: '🔪', name: '手術刀' },
                { id: 'pincer', icon: '✂️', name: '鑷子' },
                { id: 'fire', icon: '🔥', name: '火機' },
                { id: 'gel', icon: '🧪', name: '噴霧' }
            ],
            'DENTAL': [
                { id: 'drill', icon: '⚙️', name: '鑽頭' },
                { id: 'puller', icon: '🔧', name: '拔牙鉗' },
                { id: 'water', icon: '💧', name: '沖洗' }
            ],
            'EYE': [
                { id: 'dropper', icon: '💧', name: '眼藥水' },
                { id: 'swab', icon: '🧹', name: '棉花棒' },
                { id: 'laser', icon: '🔦', name: '雷射' }
            ]
        };

        function switchGame(type) {
            currentGame = type;
            document.querySelectorAll('.game-btn').forEach(b => {
                b.classList.toggle('active', b.innerText.includes(type === 'SURGERY' ? '外科' : type === 'DENTAL' ? '牙科' : '眼科'));
            });
            initGame();
        }

        function initGame() {
            hp = 100;
            timeLeft = 60;
            gameActive = true;
            
            // 初始化工具欄
            toolbar.innerHTML = '';
            TOOL_CONFIG[currentGame].forEach((t, index) => {
                const div = document.createElement('div');
                div.className = 'tool' + (index === 0 ? ' active' : '');
                if(index === 0) currentTool = t.id;
                div.id = 'tool-' + t.id;
                div.innerHTML = t.icon;
                div.title = t.name;
                div.onclick = () => {
                    document.querySelectorAll('.tool').forEach(el => el.classList.remove('active'));
                    div.classList.add('active');
                    currentTool = t.id;
                };
                toolbar.appendChild(div);
            });

            // 初始化各關卡數據
            if (currentGame === 'SURGERY') {
                instEl.innerText = "任務：切開 -> 取出玻璃 -> 燒灼 -> 噴藥";
                gameState = {
                    shards: [
                        { x: 200, y: 150, r: 15, removed: false },
                        { x: 400, y: 200, r: 15, removed: false }
                    ],
                    wound: { cut: false, cauterized: false, healed: false }
                };
            } else if (currentGame === 'DENTAL') {
                instEl.innerText = "任務：鑽開蛀牙 -> 拔除爛牙 -> 沖洗傷口";
                gameState = {
                    teeth: [
                        { x: 150, y: 200, status: 'bad', drilled: false, pulled: false },
                        { x: 300, y: 220, status: 'bad', drilled: false, pulled: false },
                        { x: 450, y: 200, status: 'bad', drilled: false, pulled: false }
                    ],
                    cleaned: false
                };
            } else if (currentGame === 'EYE') {
                instEl.innerText = "任務：點藥水 -> 擦除灰塵 -> 雷射血絲";
                gameState = {
                    dusts: [
                        { x: 280, y: 180, r: 10, removed: false },
                        { x: 320, y: 210, r: 8, removed: false }
                    ],
                    redness: 100, // 0 為健康
                    moist: 0      // 100 為濕潤
                };
            }
        }

        canvas.addEventListener('mousedown', (e) => { isMouseDown = true; handleAction(e); });
        canvas.addEventListener('mouseup', () => isMouseDown = false);
        canvas.addEventListener('mousemove', (e) => { if(isMouseDown) handleAction(e); });

        function handleAction(e) {
            if (!gameActive) return;
            const rect = canvas.getBoundingClientRect();
            const mx = e.clientX - rect.left;
            const my = e.clientY - rect.top;

            if (currentGame === 'SURGERY') {
                if (currentTool === 'knife' && my > 180 && my < 220) gameState.wound.cut = true;
                if (currentTool === 'pincer') {
                    gameState.shards.forEach(s => {
                        if (Math.hypot(mx - s.x, my - s.y) < 30) s.removed = true;
                    });
                }
                if (currentTool === 'fire' && gameState.wound.cut) gameState.wound.cauterized = true;
                if (currentTool === 'gel' && gameState.wound.cauterized) gameState.wound.healed = true;
            } 
            else if (currentGame === 'DENTAL') {
                gameState.teeth.forEach(t => {
                    if (Math.hypot(mx - t.x, my - t.y) < 40) {
                        if (currentTool === 'drill') t.drilled = true;
                        if (currentTool === 'puller' && t.drilled) t.pulled = true;
                    }
                });
                if (currentTool === 'water') gameState.cleaned = true;
            }
            else if (currentGame === 'EYE') {
                if (currentTool === 'dropper') gameState.moist = Math.min(100, gameState.moist + 5);
                if (currentTool === 'swab' && gameState.moist > 50) {
                    gameState.dusts.forEach(d => {
                        if (Math.hypot(mx - d.x, my - d.y) < 30) d.removed = true;
                    });
                }
                if (currentTool === 'laser' && gameState.redness > 0) gameState.redness -= 2;
            }
        }

        function update() {
            if (!gameActive) return;
            hp -= 0.05;
            timeLeft -= (1/60);
            
            if (hp <= 0 || timeLeft <= 0) endGame(false);

            // 檢查勝出條件
            let win = false;
            if (currentGame === 'SURGERY') {
                win = gameState.shards.every(s => s.removed) && gameState.wound.healed;
            } else if (currentGame === 'DENTAL') {
                win = gameState.teeth.every(t => t.pulled) && gameState.cleaned;
            } else if (currentGame === 'EYE') {
                win = gameState.dusts.every(d => d.removed) && gameState.redness <= 0;
            }
            if (win) endGame(true);

            hpEl.innerText = Math.floor(hp);
            timerEl.innerText = Math.ceil(timeLeft);
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            if (currentGame === 'SURGERY') {
                ctx.fillStyle = '#f5d0b0';
                ctx.fillRect(0,0,600,400);
                ctx.strokeStyle = gameState.wound.healed ? 'white' : gameState.wound.cauterized ? '#421' : gameState.wound.cut ? '#800' : 'rgba(255,0,0,0.3)';
                ctx.lineWidth = 15;
                ctx.beginPath();
                ctx.moveTo(100, 200); ctx.lineTo(500, 200);
                ctx.stroke();
                gameState.shards.forEach(s => {
                    if(!s.removed) {
                        ctx.fillStyle = 'cyan';
                        ctx.fillRect(s.x-10, s.y-10, 20, 20);
                    }
                });
            } 
            else if (currentGame === 'DENTAL') {
                ctx.fillStyle = '#ffcccc'; // 嘴巴內部
                ctx.fillRect(0,0,600,400);
                gameState.teeth.forEach(t => {
                    if (!t.pulled) {
                        ctx.fillStyle = t.drilled ? '#ddd' : (t.status === 'bad' ? '#654' : 'white');
                        ctx.beginPath();
                        ctx.arc(t.x, t.y, 30, 0, Math.PI, true);
                        ctx.fill();
                    }
                });
            }
            else if (currentGame === 'EYE') {
                ctx.fillStyle = 'white'; // 眼球
                ctx.beginPath();
                ctx.ellipse(300, 200, 200, 120, 0, 0, Math.PI*2);
                ctx.fill();
                // 虹膜
                ctx.fillStyle = '#4B2C20';
                ctx.beginPath();
                ctx.arc(300, 200, 60, 0, Math.PI*2);
                ctx.fill();
                // 血絲
                if (gameState.redness > 0) {
                    ctx.strokeStyle = `rgba(255,0,0, ${gameState.redness/100})`;
                    ctx.lineWidth = 2;
                    for(let i=0; i<10; i++) {
                        ctx.beginPath();
                        ctx.moveTo(300, 200);
                        ctx.lineTo(300 + Math.cos(i)*150, 200 + Math.sin(i)*80);
                        ctx.stroke();
                    }
                }
                gameState.dusts.forEach(d => {
                    if(!d.removed) {
                        ctx.fillStyle = 'gray';
                        ctx.beginPath(); ctx.arc(d.x, d.y, d.r, 0, Math.PI*2); ctx.fill();
                    }
                });
            }
        }

        function endGame(win) {
            gameActive = false;
            alert(win ? "恭喜！完成治療！" : "失敗了，再接再厲。");
            initGame();
        }

        function loop() {
            update();
            draw();
            requestAnimationFrame(loop);
        }

        initGame();
        loop();
    </script>
</body>
</html>
"""

# 渲染遊戲
components.html(game_code, height=600)

st.sidebar.markdown("""
### 🏥 急診室操作指南

#### 1. 外科手術 (Surgery)
- 順序：🔪 (切開) -> ✂️ (拔玻璃) -> 🔥 (止血) -> 🧪 (癒合)

#### 2. 牙科拔牙 (Dental)
- 順序：⚙️ (鑽開牙齒) -> 🔧 (拔掉它) -> 💧 (清潔口腔)

#### 3. 眼科清除 (Eye)
- 順序：💧 (滋潤眼球) -> 🧹 (清除灰塵) -> 🔦 (雷射血絲)

**注意**：病人的生命值正在流失，請迅速切換關卡進行治療！
""")
