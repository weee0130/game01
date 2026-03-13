import streamlit as st
import streamlit.components.v1 as components

# 設定頁面
st.set_page_config(page_title="經典坦克大戰", page_icon="🚜", layout="centered")

st.title("🚜 經典坦克大戰 (Retro Tank)")
st.write("使用 **方向鍵 (Arrow Keys)** 移動，**空白鍵 (Space)** 射擊！")

# 遊戲的核心 HTML 與 JavaScript 代碼
# 這裡使用 HTML5 Canvas 實現流暢的遊戲體驗
game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; background: #000; display: flex; justify-content: center; align-items: center; overflow: hidden; font-family: 'Courier New', Courier, monospace; }
        canvas { border: 4px solid #555; background-color: #000; }
        #ui { position: absolute; top: 10px; left: 10px; color: white; }
    </style>
</head>
<body>
    <div id="ui">Score: <span id="score">0</span></div>
    <canvas id="gameCanvas"></canvas>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreEl = document.getElementById('score');

        // 遊戲常數
        const TILE_SIZE = 32;
        const ROWS = 15;
        const COLS = 15;
        canvas.width = COLS * TILE_SIZE;
        canvas.height = ROWS * TILE_SIZE;

        let score = 0;
        const keys = {};

        // 地圖數據: 0:空地, 1:磚塊, 2:鋼鐵
        const map = [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,1,1,0,1,1,0,2,0,1,1,0,1,1,0],
            [0,1,1,0,1,1,0,2,0,1,1,0,1,1,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,1,1,0,2,2,0,1,0,2,2,0,1,1,0],
            [0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
            [2,0,1,1,0,1,1,1,1,1,0,1,1,0,2],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [2,0,1,1,0,1,1,0,1,1,0,1,1,0,2],
            [0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
            [0,1,1,0,2,2,0,1,0,2,2,0,1,1,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,1,1,0,1,1,0,2,0,1,1,0,1,1,0],
            [0,1,1,0,1,1,0,0,0,1,1,0,1,1,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ];

        class Bullet {
            constructor(x, y, dx, dy, owner) {
                this.x = x;
                this.y = y;
                this.dx = dx;
                this.dy = dy;
                this.owner = owner;
                this.radius = 3;
                this.speed = 5;
            }
            update() {
                this.x += this.dx * this.speed;
                this.y += this.dy * this.speed;
                
                // 碰撞牆壁
                let gridX = Math.floor(this.x / TILE_SIZE);
                let gridY = Math.floor(this.y / TILE_SIZE);
                
                if(gridX >= 0 && gridX < COLS && gridY >= 0 && gridY < ROWS) {
                    if(map[gridY][gridX] === 1) { // 擊中磚塊
                        map[gridY][gridX] = 0;
                        return false;
                    } else if(map[gridY][gridX] === 2) { // 擊中鋼鐵
                        return false;
                    }
                }
                
                return !(this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height);
            }
            draw() {
                ctx.fillStyle = "yellow";
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        class Tank {
            constructor(x, y, color, isPlayer) {
                this.x = x;
                this.y = y;
                this.color = color;
                this.isPlayer = isPlayer;
                this.dir = { x: 0, y: -1 };
                this.speed = 2;
                this.lastShot = 0;
            }
            draw() {
                ctx.fillStyle = this.color;
                // 畫坦克主體
                ctx.fillRect(this.x + 4, this.y + 4, TILE_SIZE - 8, TILE_SIZE - 8);
                // 畫砲管
                ctx.strokeStyle = this.color;
                ctx.lineWidth = 4;
                ctx.beginPath();
                ctx.moveTo(this.x + TILE_SIZE/2, this.y + TILE_SIZE/2);
                ctx.lineTo(this.x + TILE_SIZE/2 + this.dir.x * 15, this.y + TILE_SIZE/2 + this.dir.y * 15);
                ctx.stroke();
            }
            move(dx, dy) {
                this.dir = { x: dx, y: dy };
                let nextX = this.x + dx * this.speed;
                let nextY = this.y + dy * this.speed;
                
                if(!this.checkCollision(nextX, nextY)) {
                    this.x = nextX;
                    this.y = nextY;
                }
            }
            checkCollision(nx, ny) {
                const margin = 4;
                const points = [
                    {x: nx + margin, y: ny + margin},
                    {x: nx + TILE_SIZE - margin, y: ny + margin},
                    {x: nx + margin, y: ny + TILE_SIZE - margin},
                    {x: nx + TILE_SIZE - margin, y: ny + TILE_SIZE - margin}
                ];
                for(let p of points) {
                    let gx = Math.floor(p.x / TILE_SIZE);
                    let gy = Math.floor(p.y / TILE_SIZE);
                    if(gx < 0 || gx >= COLS || gy < 0 || gy >= ROWS || map[gy][gx] !== 0) return true;
                }
                return false;
            }
            shoot() {
                const now = Date.now();
                if(now - this.lastShot > 500) {
                    bullets.push(new Bullet(this.x + TILE_SIZE/2, this.y + TILE_SIZE/2, this.dir.x, this.dir.y, this));
                    this.lastShot = now;
                }
            }
        }

        const player = new Tank(TILE_SIZE * 7, TILE_SIZE * 13, "#00ff00", true);
        const enemies = [
            new Tank(TILE_SIZE * 1, TILE_SIZE * 1, "#ff0000", false),
            new Tank(TILE_SIZE * 13, TILE_SIZE * 1, "#ff0000", false)
        ];
        let bullets = [];

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        function update() {
            // 玩家控制
            if(keys['ArrowUp']) player.move(0, -1);
            else if(keys['ArrowDown']) player.move(0, 1);
            else if(keys['ArrowLeft']) player.move(-1, 0);
            else if(keys['ArrowRight']) player.move(1, 0);
            
            if(keys['Space']) player.shoot();

            // 更新子彈
            bullets = bullets.filter(b => {
                const active = b.update();
                if(!active) return false;
                
                // 檢查是否擊中坦克
                if(!b.owner.isPlayer && Math.abs(b.x - (player.x + TILE_SIZE/2)) < 15 && Math.abs(b.y - (player.y + TILE_SIZE/2)) < 15) {
                    alert("遊戲結束！");
                    location.reload();
                    return false;
                }
                
                for(let i=enemies.length-1; i>=0; i--) {
                    let e = enemies[i];
                    if(b.owner.isPlayer && Math.abs(b.x - (e.x + TILE_SIZE/2)) < 15 && Math.abs(b.y - (e.y + TILE_SIZE/2)) < 15) {
                        enemies.splice(i, 1);
                        score += 100;
                        scoreEl.innerText = score;
                        // 補充敵人
                        setTimeout(() => {
                            enemies.push(new Tank(Math.random() < 0.5 ? TILE_SIZE : TILE_SIZE*13, TILE_SIZE, "#ff0000", false));
                        }, 2000);
                        return false;
                    }
                }
                return true;
            });

            // 敵人 AI
            enemies.forEach(e => {
                if(Math.random() < 0.02) {
                    const r = Math.random();
                    if(r < 0.25) e.aiDir = {x:0, y:-1};
                    else if(r < 0.5) e.aiDir = {x:0, y:1};
                    else if(r < 0.75) e.aiDir = {x:-1, y:0};
                    else e.aiDir = {x:1, y:0};
                }
                if(e.aiDir) e.move(e.aiDir.x, e.aiDir.y);
                if(Math.random() < 0.01) e.shoot();
            });
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // 畫地圖
            for(let r=0; r<ROWS; r++) {
                for(let c=0; c<COLS; c++) {
                    if(map[r][c] === 1) {
                        ctx.fillStyle = "#a52a2a"; // 磚塊
                        ctx.fillRect(c*TILE_SIZE+2, r*TILE_SIZE+2, TILE_SIZE-4, TILE_SIZE-4);
                    } else if(map[r][c] === 2) {
                        ctx.fillStyle = "#888"; // 鋼鐵
                        ctx.fillRect(c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE);
                    }
                }
            }
            
            player.draw();
            enemies.forEach(e => e.draw());
            bullets.forEach(b => b.draw());
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

# 將遊戲嵌入 Streamlit
components.html(game_code, height=550)

st.sidebar.markdown("""
### 🎮 遊戲說明
- **目標**：消滅所有紅色坦克。
- **磚塊**：可以被子彈擊碎。
- **鋼鐵**：子彈無法擊穿。
- **控制**：
    - 鍵盤方向鍵移動。
    - 空白鍵發射子彈。
""")
