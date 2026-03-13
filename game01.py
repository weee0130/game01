import streamlit as st
import streamlit.components.v1 as components

# 設定頁面
st.set_page_config(page_title="醫療大冒險：達文西手術版", page_icon="🏥", layout="centered")

st.title("🏥 醫療大冒險：達文西手術系統")
st.write("點擊按鈕切換任務，特別挑戰全新的「達文西微創手術」模式！")

# 遊戲的核心 HTML 與 JavaScript 代碼
game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; background: #111; display: flex; flex-direction: column; justify-content: center; align-items: center; overflow: hidden; font-family: 'Courier New', Courier, monospace; cursor: none; }
        canvas { border: 5px solid #333; background-color: #000; border-radius: 20px; box-shadow: 0 0 30px rgba(0,255,100,0.2); }
        #ui { position: absolute; top: 10px; width: 500px; display: flex; justify-content: space-between; color: #00ff41; font-weight: bold; font-size: 18px; text-shadow: 0 0 5px #00ff41; pointer-events: none; z-index: 20; }
        
        #game-selector { margin-bottom: 10px; display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; }
        .game-btn { padding: 6px 12px; background: #222; color: #00ff41; border: 1px solid #00ff41; border-radius: 4px; cursor: pointer; font-size: 12px; }
        .game-btn.active { background: #00ff41; color: #000; font-weight: bold; }

        #toolbar { position: absolute; bottom: 20px; display: flex; gap: 10px; background: rgba(0,0,0,0.8); padding: 10px; border-radius: 15px; border: 1px solid #444; }
        .tool { width: 55px; height: 55px; background: #222; border: 2px solid #444; border-radius: 10px; display: flex; justify-content: center; align-items: center; font-size: 24px; cursor: pointer; transition: 0.2s; color: white; }
        .tool.active { background: #333; border-color: #00ff41; transform: translateY(-3px); box-shadow: 0 0 10px #00ff41; }
        
        #instruction { position: absolute; top: 45px; color: #00ff41; background: rgba(0,0,0,0.7); padding: 5px 15px; border-radius: 5px; font-size: 13px; border: 1px solid #00ff41; }
    </style>
</head>
<body>
    <div id="game-selector">
        <button class="game-btn" onclick="switchGame('SURGERY')">外科手術</button>
        <button class="game-btn" onclick="switchGame('DENTAL')">牙科拔牙</button>
        <button class="game-btn" onclick="switchGame('EYE')">眼科清除</button>
        <button class="game-btn active" onclick="switchGame('DAVINCI')">達文西手術</button>
    </div>

    <div id="ui">
        <div>❤️ HP: <span id="hp">100</span></div>
        <div>[SYSTEM ONLINE]</div>
        <div>⏱️ <span id="timer">60</span>s</div>
    </div>
    
    <div id="instruction">系統啟動中...</div>
    
    <canvas id="gameCanvas"></canvas>

    <div id="toolbar"></div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const hpEl = document.getElementById('hp');
        const timerEl = document.getElementById('timer');
        const instEl = document.getElementById('instruction');
        const toolbar = document.getElementById('toolbar');

        canvas.width = 600;
        canvas.height = 400;

        let currentGame = 'DAVINCI';
        let hp = 100;
        let timeLeft = 60;
        let currentTool = '';
        let isMouseDown = false;
        let gameActive = true;
        let mouseX = 300, mouseY = 200;

        // 機械手臂狀態
        let armL = { x: 100, y: 400 };
        let armR = { x: 500, y: 400 };

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
            ],
            'DAVINCI': [
                { id: 'grab', icon: '🦾', name: '機械夾' },
                { id: 'cautery', icon: '⚡', name: '電燒' }
            ]
        };

        function switchGame(type) {
            currentGame = type;
            document.querySelectorAll('.game-btn').forEach(b => {
                b.classList.toggle('active', b.onclick.toString().includes(type));
            });
            initGame();
        }

        function initGame() {
            hp = 100;
            timeLeft = 60;
            gameActive = true;
            
            toolbar.innerHTML = '';
            TOOL_CONFIG[currentGame].forEach((t, index) => {
                const div = document.createElement('div');
                div.className = 'tool' + (index === 0 ? ' active' : '');
                if(index === 0) currentTool = t.id;
                div.id = 'tool-' + t.id;
                div.innerHTML = t.icon;
                div.onclick = () => {
                    document.querySelectorAll('.tool').forEach(el => el.classList.remove('active'));
                    div.classList.add('active');
                    currentTool = t.id;
                };
                toolbar.appendChild(div);
            });

            if (currentGame === 'SURGERY') {
                instEl.innerText = "任務：切開 -> 取出玻璃 -> 燒灼 -> 噴藥";
                gameState = {
                    shards: [{ x: 200, y: 150, r: 15, removed: false }, { x: 400, y: 200, r: 15, removed: false }],
                    wound: { cut: false, cauterized: false, healed: false }
                };
            } else if (currentGame === 'DENTAL') {
                instEl.innerText = "任務：鑽開 -> 拔牙 -> 沖洗";
                gameState = {
                    teeth: [{ x: 150, y: 200, status: 'bad', drilled: false, pulled: false }, { x: 300, y: 220, status: 'bad', drilled: false, pulled: false }, { x: 450, y: 200, status: 'bad', drilled: false, pulled: false }],
                    cleaned: false
                };
            } else if (currentGame === 'EYE') {
                instEl.innerText = "任務：點藥 -> 清灰塵 -> 雷射";
                gameState = {
                    dusts: [{ x: 280, y: 180, r: 10, removed: false }, { x: 320, y: 210, r: 8, removed: false }],
                    redness: 100, moist: 0
                };
            } else if (currentGame === 'DAVINCI') {
                instEl.innerText = "任務：使用雙臂夾除寄生蟲 🐛";
                gameState = {
                    bugs: [
                        { x: 100, y: 100, tx: 200, ty: 150, active: true },
                        { x: 400, y: 300, tx: 300, ty: 250, active: true },
                        { x: 500, y: 100, tx: 450, ty: 200, active: true }
                    ],
                    scale: 0
                };
            }
        }

        window.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            mouseX = e.clientX - rect.left;
            mouseY = e.clientY - rect.top;
        });

        canvas.addEventListener('mousedown', (e) => { isMouseDown = true; handleAction(e); });
        canvas.addEventListener('mouseup', () => isMouseDown = false);

        function handleAction(e) {
            if (!gameActive) return;
            if (currentGame === 'DAVINCI') {
                if (currentTool === 'grab') {
                    gameState.bugs.forEach(b => {
                        // 判斷左手或右手夾到
                        if (b.active && (Math.hypot(mouseX - b.x, mouseY - b.y) < 30 || Math.hypot((600 - mouseX) - b.x, mouseY - b.y) < 30)) {
                            b.active = false;
                        }
                    });
                }
            } else {
                // 延用舊版邏輯
                const rect = canvas.getBoundingClientRect();
                const mx = e.clientX - rect.left;
                const my = e.clientY - rect.top;
                if (currentGame === 'SURGERY') {
                    if (currentTool === 'knife' && Math.abs(my - 200) < 20) gameState.wound.cut = true;
                    if (currentTool === 'pincer') gameState.shards.forEach(s => { if (Math.hypot(mx - s.x, my - s.y) < 30) s.removed = true; });
                    if (currentTool === 'fire' && gameState.wound.cut) gameState.wound.cauterized = true;
                    if (currentTool === 'gel' && gameState.wound.cauterized) gameState.wound.healed = true;
                } else if (currentGame === 'DENTAL') {
                    gameState.teeth.forEach(t => {
                        if (Math.hypot(mx - t.x, my - t.y) < 40) {
                            if (currentTool === 'drill') t.drilled = true;
                            if (currentTool === 'puller' && t.drilled) t.pulled = true;
                        }
                    });
                    if (currentTool === 'water') gameState.cleaned = true;
                } else if (currentGame === 'EYE') {
                    if (currentTool === 'dropper') gameState.moist = Math.min(100, gameState.moist + 5);
                    if (currentTool === 'swab' && gameState.moist > 50) gameState.dusts.forEach(d => { if (Math.hypot(mx - d.x, my - d.y) < 30) d.removed = true; });
                    if (currentTool === 'laser' && gameState.redness > 0) gameState.redness -= 2;
                }
            }
        }

        function update() {
            if (!gameActive) return;
            hp -= 0.04;
            timeLeft -= (1/60);
            if (hp <= 0 || timeLeft <= 0) endGame(false);

            if (currentGame === 'DAVINCI') {
                // 蟲蟲蠕動
                gameState.bugs.forEach(b => {
                    if (!b.active) return;
                    b.x += (b.tx - b.x) * 0.02;
                    b.y += (b.ty - b.y) * 0.02;
                    if (Math.hypot(b.x - b.tx, b.y - b.ty) < 5) {
                        b.tx = Math.random() * 400 + 100;
                        b.ty = Math.random() * 200 + 100;
                    }
                });
                // 機械臂平滑跟隨
                armL.x += (mouseX - armL.x) * 0.2;
                armL.y += (mouseY - armL.y) * 0.2;
                armR.x += ((600 - mouseX) - armR.x) * 0.2;
                armR.y += (mouseY - armR.y) * 0.2;

                if (gameState.bugs.every(b => !b.active)) endGame(true);
            } else {
                // 原有勝出邏輯
                let win = false;
                if (currentGame === 'SURGERY') win = gameState.shards.every(s => s.removed) && gameState.wound.healed;
                if (currentGame === 'DENTAL') win = gameState.teeth.every(t => t.pulled) && gameState.cleaned;
                if (currentGame === 'EYE') win = gameState.dusts.every(d => d.removed) && gameState.redness <= 0;
                if (win) endGame(true);
            }

            hpEl.innerText = Math.floor(hp);
            timerEl.innerText = Math.ceil(timeLeft);
        }

        function drawRobotArm(x, y, isLeft) {
            const baseSide = isLeft ? 0 : 600;
            ctx.strokeStyle = '#666';
            ctx.lineWidth = 10;
            ctx.beginPath();
            ctx.moveTo(baseSide, 400);
            ctx.lineTo(x, y);
            ctx.stroke();

            // 夾具
            ctx.fillStyle = '#999';
            ctx.save();
            ctx.translate(x, y);
            ctx.rotate(isLeft ? Math.atan2(y-400, x) : Math.atan2(y-400, x-600));
            ctx.fillRect(-10, -5, 20, 10);
            // 夾爪
            ctx.strokeStyle = '#00ff41';
            ctx.lineWidth = 3;
            ctx.beginPath();
            const open = isMouseDown ? 0 : 0.5;
            ctx.moveTo(10, 0); ctx.lineTo(25, -10 * open);
            ctx.moveTo(10, 0); ctx.lineTo(25, 10 * open);
            ctx.stroke();
            ctx.restore();
            
            // 目標鎖定框
            ctx.strokeStyle = 'rgba(0,255,65,0.3)';
            ctx.strokeRect(x-20, y-20, 40, 40);
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            if (currentGame === 'DAVINCI') {
                // 背景 (暗紅器官感)
                ctx.fillStyle = '#300';
                ctx.fillRect(0,0,600,400);
                // 網格線
                ctx.strokeStyle = 'rgba(0,255,65,0.1)';
                ctx.lineWidth = 1;
                for(let i=0; i<600; i+=40) { ctx.beginPath(); ctx.moveTo(i,0); ctx.lineTo(i,400); ctx.stroke(); }
                for(let i=0; i<400; i+=40) { ctx.beginPath(); ctx.moveTo(0,i); ctx.lineTo(600,i); ctx.stroke(); }

                // 畫蟲
                gameState.bugs.forEach(b => {
                    if (!b.active) return;
                    ctx.fillStyle = '#4a0';
                    ctx.beginPath();
                    ctx.ellipse(b.x, b.y, 15, 8, Math.sin(Date.now()/200)*0.2, 0, Math.PI*2);
                    ctx.fill();
                    ctx.fillStyle = 'white';
                    ctx.fillRect(b.x+8, b.y-4, 3, 3); // 眼睛
                });

                // 畫機械手臂
                drawRobotArm(armL.x, armL.y, true);
                drawRobotArm(armR.x, armR.y, false);

                // 內視鏡邊框
                const gradient = ctx.createRadialGradient(300, 200, 150, 300, 200, 350);
                gradient.addColorStop(0, 'rgba(0,0,0,0)');
                gradient.addColorStop(1, 'rgba(0,0,0,0.8)');
                ctx.fillStyle = gradient;
                ctx.fillRect(0,0,600,400);

            } else {
                // 原有繪圖邏輯
                if (currentGame === 'SURGERY') {
                    ctx.fillStyle = '#f5d0b0'; ctx.fillRect(0,0,600,400);
                    ctx.strokeStyle = gameState.wound.healed ? 'white' : gameState.wound.cauterized ? '#421' : gameState.wound.cut ? '#800' : 'rgba(255,0,0,0.3)';
                    ctx.lineWidth = 15; ctx.beginPath(); ctx.moveTo(100, 200); ctx.lineTo(500, 200); ctx.stroke();
                    gameState.shards.forEach(s => { if(!s.removed) { ctx.fillStyle = 'cyan'; ctx.fillRect(s.x-10, s.y-10, 20, 20); } });
                } else if (currentGame === 'DENTAL') {
                    ctx.fillStyle = '#ffcccc'; ctx.fillRect(0,0,600,400);
                    gameState.teeth.forEach(t => { if (!t.pulled) { ctx.fillStyle = t.drilled ? '#ddd' : (t.status === 'bad' ? '#654' : 'white'); ctx.beginPath(); ctx.arc(t.x, t.y, 30, 0, Math.PI, true); ctx.fill(); } });
                } else if (currentGame === 'EYE') {
                    ctx.fillStyle = 'white'; ctx.beginPath(); ctx.ellipse(300, 200, 200, 120, 0, 0, Math.PI*2); ctx.fill();
                    ctx.fillStyle = '#4B2C20'; ctx.beginPath(); ctx.arc(300, 200, 60, 0, Math.PI*2); ctx.fill();
                    if (gameState.redness > 0) { ctx.strokeStyle = `rgba(255,0,0, ${gameState.redness/100})`; ctx.lineWidth = 2; for(let i=0; i<10; i++) { ctx.beginPath(); ctx.moveTo(300, 200); ctx.lineTo(300 + Math.cos(i)*150, 200 + Math.sin(i)*80); ctx.stroke(); } }
                    gameState.dusts.forEach(d => { if(!d.removed) { ctx.fillStyle = 'gray'; ctx.beginPath(); ctx.arc(d.x, d.y, d.r, 0, Math.PI*2); ctx.fill(); } });
                }
            }
        }

        function endGame(win) {
            gameActive = false;
            alert(win ? "SYSTEM MESSAGE: 治療完成。效率等級：優。" : "SYSTEM FAILURE: 治療中斷。");
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
### 🏥 醫療大冒險更新說明

#### 🆕 達文西手術 (Da Vinci)
- **雙臂連動**：滑鼠控制左臂，右臂會鏡像運動。
- **夾取模式**：切換至 🦾，點擊滑鼠夾取移動中的寄生蟲。
- **擬真感**：帶有機械延遲與內視鏡暗角效果。

#### 其他經典模式
- **外科手術**：🔪 -> ✂️ -> 🔥 -> 🧪
- **牙科拔牙**：⚙️ -> 🔧 -> 💧
- **眼科清除**：💧 -> 🧹 -> 🔦

**注意**：請在高科技介面下保持冷靜，精準操作機械手臂！
""")
