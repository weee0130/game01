import streamlit as st
import streamlit.components.v1 as components

# 設定頁面
st.set_page_config(page_title="瘋狂醫生：急診大挑戰", page_icon="🏥", layout="centered")

st.title("🏥 瘋狂醫生：急診大挑戰")
st.write("身為一名業餘醫生，你需要使用各種工具來挽救病人的生命！")

# 遊戲的核心 HTML 與 JavaScript 代碼
game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; background: #222; display: flex; justify-content: center; align-items: center; overflow: hidden; font-family: 'Arial', sans-serif; cursor: crosshair; }
        canvas { border: 5px solid #444; background-color: #f5d0b0; border-radius: 20px; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
        #ui { position: absolute; top: 10px; width: 500px; display: flex; justify-content: space-between; color: #ff0000; font-weight: bold; font-size: 20px; text-shadow: 1px 1px 2px black; pointer-events: none; }
        #toolbar { position: absolute; bottom: 20px; display: flex; gap: 10px; background: rgba(0,0,0,0.7); padding: 10px; border-radius: 15px; }
        .tool { width: 60px; height: 60px; background: #eee; border: 3px solid #666; border-radius: 10px; display: flex; justify-content: center; align-items: center; font-size: 30px; cursor: pointer; transition: 0.2s; }
        .tool.active { background: #fff; border-color: #00ff00; transform: translateY(-5px); box-shadow: 0 5px 10px rgba(0,255,0,0.3); }
    </style>
</head>
<body>
    <div id="ui">
        <div>❤️ HP: <span id="hp">100</span></div>
        <div>⏱️ TIME: <span id="timer">60</span>s</div>
    </div>
    
    <canvas id="gameCanvas"></canvas>

    <div id="toolbar">
        <div class="tool active" id="tool-knife" title="手術刀 - 切開傷口">🔪</div>
        <div class="tool" id="tool-pincer" title="鑷子 - 取出異物">✂️</div>
        <div class="tool" id="tool-fire" title="火機 - 燒灼止血">🔥</div>
        <div class="tool" id="tool-gel" title="癒合噴霧 - 修復皮膚">🧪</div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const hpEl = document.getElementById('hp');
        const timerEl = document.getElementById('timer');

        canvas.width = 600;
        canvas.height = 450;

        let hp = 100;
        let timeLeft = 60;
        let currentTool = 'knife';
        let isMouseDown = false;
        let gameActive = true;

        // 任務目標
        let glassShards = [
            { x: 200, y: 150, width: 40, height: 10, angle: 0.5, removed: false },
            { x: 350, y: 250, width: 30, height: 15, angle: -0.2, removed: false },
            { x: 250, y: 300, width: 35, height: 12, angle: 1.2, removed: false }
        ];
        
        let wounds = [
            { x1: 150, y1: 100, x2: 450, y2: 120, cut: false, healed: false, cauterized: false }
        ];

        // 切換工具
        const tools = {
            'knife': document.getElementById('tool-knife'),
            'pincer': document.getElementById('tool-pincer'),
            'fire': document.getElementById('tool-fire'),
            'gel': document.getElementById('tool-gel')
        };

        Object.keys(tools).forEach(id => {
            tools[id].addEventListener('click', () => {
                Object.values(tools).forEach(t => t.classList.remove('active'));
                tools[id].classList.add('active');
                currentTool = id;
            });
        });

        // 滑鼠事件
        canvas.addEventListener('mousedown', (e) => { isMouseDown = true; handleAction(e); });
        canvas.addEventListener('mouseup', () => isMouseDown = false);
        canvas.addEventListener('mousemove', (e) => { if(isMouseDown) handleAction(e); });

        function handleAction(e) {
            if (!gameActive) return;
            const rect = canvas.getBoundingClientRect();
            const mx = e.clientX - rect.left;
            const my = e.clientY - rect.top;

            if (currentTool === 'knife') {
                wounds.forEach(w => {
                    if (mx > w.x1 && mx < w.x2 && Math.abs(my - w.y1) < 20) w.cut = true;
                });
            } else if (currentTool === 'pincer') {
                glassShards.forEach(s => {
                    if (!s.removed && Math.abs(mx - s.x) < 20 && Math.abs(my - s.y) < 20) {
                        s.removed = true;
                    }
                });
            } else if (currentTool === 'fire') {
                wounds.forEach(w => {
                    if (w.cut && !w.cauterized && mx > w.x1 && mx < w.x2 && Math.abs(my - w.y1) < 20) w.cauterized = true;
                });
            } else if (currentTool === 'gel') {
                wounds.forEach(w => {
                    if (w.cauterized && !w.healed && mx > w.x1 && mx < w.x2 && Math.abs(my - w.y1) < 20) w.healed = true;
                });
            }
        }

        function update() {
            if (!gameActive) return;

            // HP 自然下降 (難度機制)
            hp -= 0.05;
            
            // 檢查未處理的異物導致流血
            glassShards.forEach(s => { if(!s.removed) hp -= 0.02; });

            if (hp <= 0) endGame(false);
            
            // 計時
            if (Math.random() < 0.016) { // 大約每秒
                timeLeft -= (1/60);
                timerEl.innerText = Math.ceil(timeLeft);
                if (timeLeft <= 0) endGame(false);
            }

            // 檢查勝出
            if (glassShards.every(s => s.removed) && wounds.every(w => w.healed)) {
                endGame(true);
            }

            hpEl.innerText = Math.max(0, Math.floor(hp));
        }

        function draw() {
            // 背景（病人腹部皮膚）
            ctx.fillStyle = '#f5d0b0';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // 畫傷口
            wounds.forEach(w => {
                ctx.beginPath();
                ctx.lineWidth = 10;
                ctx.lineCap = 'round';
                if (!w.cut) {
                    ctx.strokeStyle = 'rgba(255,0,0,0.3)'; // 切割虛線
                    ctx.setLineDash([10, 5]);
                } else if (!w.cauterized) {
                    ctx.strokeStyle = '#800'; // 鮮紅傷口
                    ctx.setLineDash([]);
                } else if (!w.healed) {
                    ctx.strokeStyle = '#421'; // 焦黑傷口
                    ctx.setLineDash([]);
                } else {
                    ctx.strokeStyle = 'rgba(255,255,255,0.5)'; // 癒合疤痕
                    ctx.setLineDash([]);
                }
                ctx.moveTo(w.x1, w.y1);
                ctx.lineTo(w.x2, w.y2);
                ctx.stroke();
            });

            // 畫異物 (玻璃)
            glassShards.forEach(s => {
                if (s.removed) return;
                ctx.save();
                ctx.translate(s.x, s.y);
                ctx.rotate(s.angle);
                ctx.fillStyle = 'rgba(200,230,255,0.7)';
                ctx.strokeStyle = 'white';
                ctx.beginPath();
                ctx.moveTo(-s.width/2, -s.height/2);
                ctx.lineTo(s.width/2, 0);
                ctx.lineTo(-s.width/2, s.height/2);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();
                ctx.restore();
            });

            // 如果是在燒灼或噴藥，畫出粒子特效（簡單版）
            if (isMouseDown) {
                const rect = canvas.getBoundingClientRect();
                // 這裡可以加一些粒子效果，目前先省略以保持簡潔
            }
        }

        function endGame(win) {
            gameActive = false;
            alert(win ? "恭喜！病人脫離危險了！" : "手術失敗... 病人宣告不治。");
            location.reload();
        }

        function loop() {
            update();
            draw();
            requestAnimationFrame(loop);
        }

        loop();
    </script>
</body>
</html>
"""

# 渲染遊戲
components.html(game_code, height=600)

st.sidebar.markdown("""
### 🏥 手術指南
1. **診斷**：觀察傷口和異物。
2. **切開**：使用 **手術刀 🔪** 沿虛線切開。
3. **移除**：使用 **鑷子 ✂️** 點擊移除所有玻璃碎屑。
4. **止血**：使用 **火機 🔥** 燒灼切口直到變深色。
5. **縫合**：使用 **噴霧 🧪** 修復皮膚。

**注意**：病人的 HP 會隨時間和傷情下降，動作要快！
""")
