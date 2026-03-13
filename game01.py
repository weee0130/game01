import streamlit as st
import streamlit.components.v1 as components

# 設定頁面與風格
st.set_page_config(page_title="DaVinci 3D Extreme", page_icon="🔬", layout="wide")

st.title("🔬 達文西 3D 微創手術終端")
st.caption("Da Vinci Surgical System v4.0 - Next-Gen 3D Rendering Engine")

# 嵌入 Three.js 與 JavaScript 遊戲引擎
game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; background: #000; overflow: hidden; font-family: 'Share Tech Mono', monospace; }
        #ui-container { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 10; }
        #hud-top { position: absolute; top: 20px; left: 20px; right: 20px; display: flex; justify-content: space-between; color: #00ff41; text-shadow: 0 0 10px #00ff41; }
        #hud-bottom { position: absolute; bottom: 20px; width: 100%; text-align: center; color: #ffeb3b; }
        .crosshair { position: absolute; top: 50%; left: 50%; width: 40px; height: 40px; border: 1px solid rgba(0,255,65,0.5); border-radius: 50%; transform: translate(-50%, -50%); }
        .crosshair::before { content: ''; position: absolute; top: 50%; left: -10px; width: 10px; height: 1px; background: #00ff41; }
        .crosshair::after { content: ''; position: absolute; left: 50%; top: -10px; width: 1px; height: 10px; background: #00ff41; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="ui-container">
        <div id="hud-top">
            <div>[ SYSTEM: 3D_GASTRO_SCAN ]</div>
            <div id="timer-display">SYNCING...</div>
            <div id="score-display">REMOVED: 0</div>
        </div>
        <div class="crosshair"></div>
        <div id="hud-bottom">>> 偵測到 3D 空間異物，判斷深度後進行夾取 <<</div>
    </div>

    <script>
        let scene, camera, renderer;
        let arms = [], bug, particles;
        let mouse = new THREE.Vector2();
        let score = 0;
        let lastBugTime = Date.now();
        let gameActive = true;
        let raycaster = new THREE.Raycaster();

        window.onload = function() {
            init();
            animate();
        };

        function init() {
            // 1. Scene & Camera
            scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x1a0202, 0.05);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.z = 5;

            // 2. Renderer
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setClearColor(0x1a0202);
            document.body.appendChild(renderer.domElement);

            // 3. Lighting (手術燈效果)
            const spotLight = new THREE.SpotLight(0xffffff, 2);
            spotLight.position.set(0, 5, 5);
            spotLight.angle = Math.PI / 4;
            spotLight.penumbra = 0.1;
            scene.add(spotLight);

            const ambientLight = new THREE.AmbientLight(0x400000, 1);
            scene.add(ambientLight);

            // 4. Gastro Tunnel (腸道背景)
            const tunnelGeom = new THREE.CylinderGeometry(5, 5, 100, 32, 1, true);
            const tunnelMat = new THREE.MeshPhongMaterial({ 
                color: 0x881111, 
                side: THREE.BackSide,
                shininess: 50,
                bumpScale: 0.1
            });
            const tunnel = new THREE.Mesh(tunnelGeom, tunnelMat);
            tunnel.rotation.x = Math.PI / 2;
            scene.add(tunnel);

            // 5. Robotic Arms
            function createArm(xOffset) {
                const group = new THREE.Group();
                const baseGeom = new THREE.BoxGeometry(0.2, 0.2, 5);
                const baseMat = new THREE.MeshStandardMaterial({ color: 0x444444, metalness: 0.8 });
                const armMesh = new THREE.Mesh(baseGeom, baseMat);
                armMesh.position.z = 2.5;
                group.add(armMesh);

                const clawGeom = new THREE.ConeGeometry(0.1, 0.3, 4);
                const clawMat = new THREE.MeshStandardMaterial({ color: 0x00ff41 });
                const claw = new THREE.Mesh(clawGeom, clawMat);
                claw.rotation.x = -Math.PI / 2;
                claw.position.z = 5;
                group.add(claw);

                group.position.x = xOffset;
                group.position.y = -2;
                scene.add(group);
                return group;
            }
            arms.push(createArm(-1.5));
            arms.push(createArm(1.5));

            // 6. The Bug (3D Parasite)
            const bugGeom = new THREE.SphereGeometry(0.2, 16, 16);
            const bugMat = new THREE.MeshPhongMaterial({ color: 0x7fff00, emissive: 0x224400 });
            bug = new THREE.Mesh(bugGeom, bugMat);
            bug.visible = false;
            scene.add(bug);

            // 7. Particles (微塵/血液感)
            const pGeom = new THREE.BufferGeometry();
            const pCoords = [];
            for(let i=0; i<500; i++) {
                pCoords.push(Math.random()*20-10, Math.random()*20-10, Math.random()*20-10);
            }
            pGeom.setAttribute('position', new THREE.Float32BufferAttribute(pCoords, 3));
            const pMat = new THREE.PointsMaterial({ color: 0xaa0000, size: 0.05 });
            particles = new THREE.Points(pGeom, pMat);
            scene.add(particles);

            window.addEventListener('mousemove', onMouseMove);
            window.addEventListener('mousedown', onMouseDown);
            window.addEventListener('resize', onWindowResize);
        }

        function onMouseMove(event) {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
        }

        function onMouseDown() {
            if (!gameActive || !bug.visible) return;

            // 使用 Raycaster 檢測是否擊中 3D 蟲子
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObject(bug);

            if (intersects.length > 0) {
                score++;
                bug.visible = false;
                document.getElementById('score-display').innerText = `REMOVED: ${score}`;
            }
        }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        function updateGameLogic() {
            const now = Date.now();
            const cycleTime = 10000;
            const appearTime = 2500;
            const elapsed = (now - lastBugTime) % cycleTime;

            if (elapsed < appearTime) {
                if (!bug.visible) {
                    bug.visible = true;
                    bug.position.set(Math.random()*4-2, Math.random()*2-1, -Math.random()*5-2);
                    document.getElementById('hud-bottom').innerText = "!! 警報：發現寄生蟲，鎖定目標中 !!";
                }
                // 蟲子 3D 動態
                bug.position.x += Math.sin(now/500)*0.01;
                bug.position.y += Math.cos(now/500)*0.01;
            } else {
                if (bug.visible) {
                    bug.visible = false;
                    // 如果消失時沒抓到且不是因為被抓，可以設定失敗邏輯
                }
                document.getElementById('hud-bottom').innerText = ">> 掃描 3D 組織層面中... <<";
            }

            document.getElementById('timer-display').innerText = `NEXT_WAVE: ${((cycleTime-elapsed)/1000).toFixed(1)}s`;
        }

        function animate() {
            if (!gameActive) return;
            requestAnimationFrame(animate);

            updateGameLogic();

            // 機械手臂平滑跟隨滑鼠
            const targetX = mouse.x * 3;
            const targetY = mouse.y * 2;
            
            // 左手
            arms[0].lookAt(targetX, targetY, -5);
            // 右手 (鏡像)
            arms[1].lookAt(-targetX, targetY, -5);

            // 粒子飄動
            particles.rotation.z += 0.001;
            particles.position.z += 0.01;
            if(particles.position.z > 5) particles.position.z = 0;

            renderer.render(scene, camera);
        }
    </script>
</body>
</html>
"""

# 使用 Streamlit Component 渲染，設定 height=700 展現華麗感
components.html(game_code, height=700)

# 側邊欄與醫學數據
with st.sidebar:
    st.header("🔬 3D 內視鏡終端")
    st.markdown("---")
    st.write("### 系統規格")
    st.code("Renderer: WebGL 2.0\nEngine: Three.js r128\nDepth Support: Enabled")
    
    st.divider()
    st.info("""
    **3D 操作指南：**
    - **深度感知**：蟲子現在會在 3D 空間移動，越遠看起來越小。
    - **精準夾取**：將準星對準蟲子並點擊，系統會自動計算 3D 軌跡進行夾取。
    - **週期提醒**：觀察左上角 NEXT_WAVE 計時。
    """)
    
    if st.button("重啟系統校準"):
        st.rerun()

st.markdown("---")
st.write("💡 **開發者筆記**：這是透過 `Three.js` 實現的 GPU 加速渲染。在 GitHub 部署後，它能完美利用使用者的顯卡性能，提供極致流暢的手術體驗。")
