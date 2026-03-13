import streamlit as st
import streamlit.components.v1 as components

# 設定頁面與風格
st.set_page_config(page_title="DaVinci Surgery Sim", page_icon="🦾", layout="centered")

st.title("🦾 達文西微創手術中心")
st.caption("Da Vinci Surgical System - Remote Operation Terminal")

# 嵌入 HTML5 / JavaScript 遊戲引擎
game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; background: #050505; color: #00ff41; font-family: 'Share Tech Mono', monospace; display: flex; justify-content: center; align-items: center; overflow: hidden; }
        canvas { background: radial-gradient(circle, #2a0505 0%, #050505 100%); border: 2px solid #00ff41; border-radius: 10px; cursor: none; }
        #overlay { position: absolute; top: 20px; width: 580px; display: flex; justify-content: space-between; pointer-events: none; z-index: 100; font-size: 14px; text-shadow: 0 0 5px #00ff41; }
        #info-panel { position: absolute; bottom: 80px; width: 580px; text-align: center; pointer-events: none; opacity: 0.7; font-size: 12px; }
        .hud-line { position: absolute; width: 100%; height: 1px; background: rgba(0,255,65,0.2); pointer-events: none; }
    </style>
</head>
<body>
    <div id="overlay">
        <div>STATUS: OPERATION IN PROGRESS</div>
        <div>ARM_SYNC: 98.4%</div>
        <div>TEMP: 36.5°C</div>
    </div>
    
    <div id="info-panel">>> 偵測到異物活動... 使用 [滑鼠點擊] 進行夾取 <<</div>
    
    <canvas id="gameCanvas"></canvas>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        canvas.width = 600;
        canvas.height = 450;

        let mouseX = 300, mouseY = 225;
        let isClicking = false;
        let score = 0;
        let lives = 100;

        // 蟲子 (目標)
        class Parasite {
            constructor() {
                this.reset();
            }
            reset() {
                this.x = Math.random() * 400 + 100;
                this.y = Math.random() * 250 + 100;
                this.vx = (Math.random() - 0.5) * 2;
                this.vy = (Math.random() - 0.5) * 2;
                this.size = 12;
            }
            update() {
                this.x += this.vx;
                this.y += this.vy;
                if(this.x < 100 || this.x > 500) this.vx *= -1;
                if(this.y < 50 || this.y > 350) this.vy *= -1;
            }
            draw() {
                ctx.fillStyle = '#ff3300';
                ctx.beginPath();
                ctx.ellipse(this.x, this.y, this.size, this.size/2, Math.atan2(this.vy, this.vx), 0, Math.PI*2);
                ctx.fill();
                // 腳
                ctx.strokeStyle = '#ff3300';
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(this.x, this.y);
                ctx.lineTo(this.x + Math.sin(Date.now()/100)*10, this.y + 10);
                ctx.stroke();
            }
        }

        const bugs = [new Parasite(), new Parasite(), new Parasite()];

        // 機械臂類別
        class RobotArm {
            constructor(baseX, isRight) {
                this.baseX = baseX;
                this.baseY = 450;
                this.isRight = isRight;
                this.jointX = baseX;
                this.jointY = 225;
            }
            draw(targetX, targetY) {
                // 模擬機械關節：連桿 1 (底座到中間關節)
                ctx.strokeStyle = '#444';
                ctx.lineWidth = 8;
                ctx.beginPath();
                ctx.moveTo(this.baseX, this.baseY);
                // 關節點計算 (簡單的插值模擬連桿)
                let midX = (this.baseX + targetX) / 2 + (this.isRight ? -30 : 30);
                let midY = (this.baseY + targetY) / 2 - 20;
                ctx.lineTo(midX, midY);
                ctx.stroke();

                // 連桿 2 (關節到末端)
                ctx.strokeStyle = '#888';
                ctx.lineWidth = 5;
                ctx.beginPath();
                ctx.moveTo(midX, midY);
                ctx.lineTo(targetX, targetY);
                ctx.stroke();

                // 夾頭
                ctx.fillStyle = '#00ff41';
                ctx.save();
                ctx.translate(targetX, targetY);
                ctx.rotate(Math.atan2(targetY - midY, targetX - midX));
                
                // 繪製爪子
                const gap = isClicking ? 2 : 12;
                ctx.fillRect(0, -2, 15, 2);
                ctx.beginPath();
                ctx.moveTo(10, -2); ctx.lineTo(20, -gap);
                ctx.moveTo(10, 2); ctx.lineTo(20, gap);
                ctx.stroke();
                ctx.restore();
                
                // 掃描線
                ctx.strokeStyle = 'rgba(0, 255, 65, 0.2)';
                ctx.setLineDash([5, 5]);
                ctx.strokeRect(targetX - 25, targetY - 25, 50, 50);
                ctx.setLineDash([]);
            }
        }

        const armL = new RobotArm(50, false);
        const armR = new RobotArm(550, true);

        canvas.onmousemove = (e) => {
            const rect = canvas.getBoundingClientRect();
            mouseX = e.clientX - rect.left;
            mouseY = e.clientY - rect.top;
        };

        canvas.onmousedown = () => {
            isClicking = true;
            // 檢查是否夾到蟲
            bugs.forEach(bug => {
                let dL = Math.hypot(bug.x - mouseX, bug.y - mouseY);
                let dR = Math.hypot(bug.x - (600 - mouseX), bug.y - mouseY);
                if(dL < 25 || dR < 25) {
                    bug.reset();
                    score += 10;
                }
            });
        };
        canvas.onmouseup = () => isClicking = false;

        function drawHUD() {
            // 十字準星
            ctx.strokeStyle = 'rgba(0, 255, 65, 0.5)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(mouseX, 0); ctx.lineTo(mouseX, 450);
            ctx.moveTo(0, mouseY); ctx.lineTo(600, mouseY);
            ctx.stroke();

            // 圓形內視鏡邊框
            ctx.strokeStyle = '#00ff41';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(300, 225, 210, 0, Math.PI*2);
            ctx.stroke();

            // 數據顯示
            ctx.fillStyle = '#00ff41';
            ctx.fillText(`X: ${mouseX.toFixed(0)}`, 20, 430);
            ctx.fillText(`Y: ${mouseY.toFixed(0)}`, 80, 430);
            ctx.fillText(`SCORE: ${score}`, 500, 430);
        }

        function loop() {
            ctx.clearRect(0, 0, 600, 450);
            
            // 繪製背景標記
            ctx.fillStyle = 'rgba(255, 0, 0, 0.05)';
            ctx.beginPath();
            ctx.ellipse(300, 225, 180, 100, 0, 0, Math.PI*2);
            ctx.fill();

            bugs.forEach(b => {
                b.update();
                b.draw();
            });

            // 左手追蹤滑鼠，右手鏡像追蹤
            armL.draw(mouseX, mouseY);
            armR.draw(600 - mouseX, mouseY);

            drawHUD();
            requestAnimationFrame(loop);
        }

        loop();
    </script>
</body>
</html>
"""

# 使用 Streamlit Component 渲染
components.html(game_code, height=520)

# 側邊欄與說明
with st.sidebar:
    st.header("操作終端")
    st.info("""
    **操作說明：**
    1. **移動滑鼠**：同步控制雙機械手臂。
    2. **點擊左鍵**：執行夾取動作。
    3. **目標**：清除紅色寄生蟲。
    """)
    
    st.divider()
    
    st.write("### 系統狀態")
    st.progress(85, "伺服器連接穩定")
    st.success("機械連桿校準完成")

st.markdown("---")
st.write("💡 **開發提示**：這是一個基於 HTML5 Canvas 的即時渲染環境。與傳統的 Streamlit 元件相比，它能提供零延遲的手感，非常適合模擬精密手術的操作。")
