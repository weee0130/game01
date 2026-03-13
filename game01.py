import streamlit as st
import streamlit.components.v1 as components

# 設定頁面與風格
st.set_page_config(page_title="DaVinci Surgery Sim", page_icon="🦾", layout="centered")

st.title("🦾 達文西微創手術中心")
st.caption("Da Vinci Surgical System - Gastroenterology Dept.")

# 嵌入 HTML5 / JavaScript 遊戲引擎
game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; background: #050505; color: #00ff41; font-family: 'Share Tech Mono', monospace; display: flex; justify-content: center; align-items: center; overflow: hidden; }
        /* 背景改為更具腸胃道感的放射狀漸層 (深粉紅到暗紅) */
        canvas { background: radial-gradient(circle, #4d0a0a 0%, #1a0202 100%); border: 2px solid #00ff41; border-radius: 10px; cursor: none; }
        #overlay { position: absolute; top: 20px; width: 580px; display: flex; justify-content: space-between; pointer-events: none; z-index: 100; font-size: 14px; text-shadow: 0 0 5px #00ff41; }
        #info-panel { position: absolute; bottom: 80px; width: 580px; text-align: center; pointer-events: none; opacity: 0.9; font-size: 14px; color: #ffeb3b; }
        .hud-line { position: absolute; width: 100%; height: 1px; background: rgba(0,255,65,0.2); pointer-events: none; }
    </style>
</head>
<body>
    <div id="overlay">
        <div>STATUS: GASTRO_SCOPING</div>
        <div>ARM_SYNC: 100%</div>
        <div>TISSUE_TEMP: 37.2°C</div>
    </div>
    
    <div id="info-panel">>> 等待異物浮現... <<</div>
    
    <canvas id="gameCanvas"></canvas>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const infoPanel = document.getElementById('info-panel');
        canvas.width = 600;
        canvas.height = 450;

        let mouseX = 300, mouseY = 225;
        let isClicking = false;
        let score = 0;
        let gameActive = true;

        // 腸胃道背景細節 (血管感)
        const veins = [];
        for(let i=0; i<5; i++) {
            veins.push({
                x1: Math.random()*600, y1: Math.random()*450,
                x2: Math.random()*600, y2: Math.random()*450
            });
        }

        // 寄生蟲邏輯：10秒一個週期，隨機出現2秒
        class Parasite {
            constructor() {
                this.cycleDuration = 10000; // 10秒一個週期
                this.appearDuration = 2000; // 出現2秒
                this.lastCycleStart = Date.now();
                this.appearOffset = Math.random() * (this.cycleDuration - this.appearDuration);
                this.reset();
                this.visible = false;
                this.caughtThisCycle = false;
            }
            reset() {
                this.x = Math.random() * 300 + 150;
                this.y = Math.random() * 200 + 100;
                this.vx = (Math.random() - 0.5) * 1.5;
                this.vy = (Math.random() - 0.5) * 1.5;
                this.size = 18;
            }
            update() {
                const now = Date.now();
                const elapsedInCycle = (now - this.lastCycleStart) % this.cycleDuration;

                // 判斷是否在出現時間窗內
                if (elapsedInCycle >= this.appearOffset && elapsedInCycle <= this.appearOffset + this.appearDuration) {
                    if (!this.visible && !this.caughtThisCycle) {
                        this.visible = true;
                        this.reset(); // 每次出現換個位置
                        infoPanel.innerText = "!! 偵測到活動：立刻夾取 !!";
                        infoPanel.style.color = "#f44336";
                    }
                } else {
                    // 如果出現時間結束且沒夾到，且剛剛是可見狀態 -> 失敗
                    if (this.visible && !this.caughtThisCycle) {
                        this.failGame();
                    }
                    this.visible = false;
                    this.caughtThisCycle = false; // 重置週期抓取狀態
                    infoPanel.innerText = ">> 掃描組織中... <<";
                    infoPanel.style.color = "#ffeb3b";
                }

                if (this.visible) {
                    this.x += this.vx;
                    this.y += this.vy;
                }
            }
            draw() {
                if (!this.visible) return;
                
                // 畫蟲 (更長更像腸道蟲)
                ctx.fillStyle = '#7FFF00'; // 亮綠色對比紅色背景
                ctx.beginPath();
                ctx.ellipse(this.x, this.y, this.size, this.size/3, Math.atan2(this.vy, this.vx), 0, Math.PI*2);
                ctx.fill();
                
                // 節點細節
                ctx.strokeStyle = '#458b00';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.arc(this.x, this.y, 4, 0, Math.PI*2);
                ctx.stroke();
            }
            failGame() {
                gameActive = false;
                alert("任務失敗：寄生蟲已鑽入組織深處！");
                location.reload();
            }
        }

        const bug = new Parasite();

        class RobotArm {
            constructor(baseX, isRight) {
                this.baseX = baseX;
                this.baseY = 450;
                this.isRight = isRight;
            }
            draw(targetX, targetY) {
                ctx.strokeStyle = '#555';
                ctx.lineWidth = 10;
                ctx.beginPath();
                ctx.moveTo(this.baseX, this.baseY);
                let midX = (this.baseX + targetX) / 2 + (this.isRight ? -40 : 40);
                let midY = (this.baseY + targetY) / 2 - 30;
                ctx.lineTo(midX, midY);
                ctx.stroke();

                ctx.strokeStyle = '#aaa';
                ctx.lineWidth = 6;
                ctx.beginPath();
                ctx.moveTo(midX, midY);
                ctx.lineTo(targetX, targetY);
                ctx.stroke();

                ctx.fillStyle = '#00ff41';
                ctx.save();
                ctx.translate(targetX, targetY);
                ctx.rotate(Math.atan2(targetY - midY, targetX - midX));
                const gap = isClicking ? 1 : 14;
                ctx.fillRect(0, -3, 18, 3);
                ctx.beginPath();
                ctx.moveTo(12, -3); ctx.lineTo(22, -gap);
                ctx.moveTo(12, 3); ctx.lineTo(22, gap);
                ctx.stroke();
                ctx.restore();
            }
        }

        const armL = new RobotArm(-20, false);
        const armR = new RobotArm(620, true);

        canvas.onmousemove = (e) => {
            const rect = canvas.getBoundingClientRect();
            mouseX = e.clientX - rect.left;
            mouseY = e.clientY - rect.top;
        };

        canvas.onmousedown = () => {
            if (!gameActive) return;
            isClicking = true;
            if (bug.visible) {
                let dL = Math.hypot(bug.x - mouseX, bug.y - mouseY);
                let dR = Math.hypot(bug.x - (600 - mouseX), bug.y - mouseY);
                if(dL < 30 || dR < 30) {
                    score += 1;
                    bug.visible = false;
                    bug.caughtThisCycle = true;
                    infoPanel.innerText = "SUCCESS: 目標已移除！";
                }
            }
        };
        canvas.onmouseup = () => isClicking = false;

        function drawHUD() {
            // 十字準星
            ctx.strokeStyle = 'rgba(0, 255, 65, 0.4)';
            ctx.beginPath();
            ctx.moveTo(mouseX, 0); ctx.lineTo(mouseX, 450);
            ctx.moveTo(0, mouseY); ctx.lineTo(600, mouseY);
            ctx.stroke();

            // 數據顯示
            ctx.fillStyle = '#00ff41';
            ctx.font = '12px Share Tech Mono';
            ctx.fillText(`CAPTURE_COUNT: ${score}`, 480, 430);
            
            // 繪製計時條 (顯示10秒週期的進度)
            const now = Date.now();
            const elapsed = (now - bug.lastCycleStart) % bug.cycleDuration;
            ctx.fillStyle = 'rgba(0, 255, 65, 0.2)';
            ctx.fillRect(150, 425, 300, 5);
            ctx.fillStyle = '#00ff41';
            ctx.fillRect(150, 425, (elapsed/bug.cycleDuration)*300, 5);
        }

        function loop() {
            if (!gameActive) return;
            ctx.clearRect(0, 0, 600, 450);
            
            // 畫腸道背景細節 (微血管)
            ctx.strokeStyle = 'rgba(255, 0, 0, 0.15)';
            ctx.lineWidth = 3;
            veins.forEach(v => {
                ctx.beginPath(); ctx.moveTo(v.x1, v.y1); ctx.lineTo(v.x2, v.y2); ctx.stroke();
            });

            bug.update();
            bug.draw();

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
    st.header("遠端手術系統")
    st.error("⚠️ 警告：腸道寄生蟲具備高度警覺性。")
    st.info("""
    **當前環境：腸胃道內視鏡模式**
    
    **任務邏輯：**
    1. **潛伏機制**：蟲子每 10 秒出現一次。
    2. **出現視窗**：每次僅出現 **2 秒**。
    3. **失敗條件**：若在出現期間未成功夾取，蟲子會鑽入深處導致手術失敗。
    
    **操作：**
    - 移動滑鼠控制雙臂。
    - 點擊左鍵精準夾取。
    """)
    
    st.divider()
    st.write("### 醫學數據")
    st.progress(100, "內視鏡連線中")
    st.success("光學傳感器校準正常")

st.markdown("---")
st.write("💡 **臨床筆記**：寄生蟲在受驚時會迅速逃逸。觀察畫面下方的計時條，預判蟲子可能出現的時間點。")
