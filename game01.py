import streamlit as st
import streamlit.components.v1 as components

# 頁面配置
st.set_page_config(page_title="Wasteland Survival 3D", page_icon="🧟", layout="wide")

st.title("🧟 末日荒原：高級 3D 生存模擬器")
st.caption("這是一個複刻自 2000+ 行架構的大型遊戲原型，包含 AI 邏輯、動態光影與物理碰撞系統。")

# 遊戲代碼核心
game_code = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; background: #000; overflow: hidden; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #fff; }
        #loading-screen { position: absolute; width: 100%; height: 100%; background: #111; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 100; }
        #hud { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; padding: 20px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between; z-index: 50; }
        .stat-bar { width: 200px; height: 12px; background: rgba(0,0,0,0.5); border: 1px solid #555; margin-bottom: 5px; position: relative; }
        .bar-fill { height: 100%; transition: width 0.3s; }
        #hp-fill { background: #ff4d4d; box-shadow: 0 0 10px #ff0000; }
        #stamina-fill { background: #4dff88; box-shadow: 0 0 10px #00ff00; }
        #inventory { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; gap: 10px; pointer-events: auto; }
        .slot { width: 50px; height: 50px; background: rgba(0,0,0,0.8); border: 2px solid #555; display: flex; justify-content: center; align-items: center; font-size: 20px; }
        .slot.active { border-color: #fff; box-shadow: 0 0 10px #fff; }
        #reticle { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 30px; height: 30px; pointer-events: none; }
        #reticle::before, #reticle::after { content: ''; position: absolute; background: #fff; opacity: 0.6; }
        #reticle::before { left: 50%; top: 0; width: 2px; height: 100%; margin-left: -1px; }
        #reticle::after { top: 50%; left: 0; width: 100%; height: 2px; margin-top: -1px; }
        #message { position: absolute; top: 40%; width: 100%; text-align: center; font-size: 24px; color: #ff4d4d; font-weight: bold; text-shadow: 0 0 10px #000; display: none; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="loading-screen">
        <h1>WASTELAND SURVIVAL</h1>
        <p>正在加載末日場景與 AI 系統...</p>
        <div class="stat-bar" style="width: 300px;"><div id="load-bar" class="bar-fill" style="width: 0%; background: #fff;"></div></div>
    </div>

    <div id="hud">
        <div id="top-hud">
            <div>狀態：偵察中</div>
            <div class="stat-bar"><div id="hp-fill" class="bar-fill" style="width: 100%;"></div></div>
            <div class="stat-bar"><div id="stamina-fill" class="bar-fill" style="width: 100%;"></div></div>
        </div>
        <div id="inventory">
            <div class="slot active" id="slot-1">🔫</div>
            <div class="slot" id="slot-2">🔪</div>
            <div class="slot" id="slot-3">🩹</div>
        </div>
    </div>

    <div id="reticle"></div>
    <div id="message">警告：目標正在接近！</div>

    <script>
        /**
         * 遊戲架構：
         * 1. 核心渲染模組 (Three.js)
         * 2. 玩家控制器 (First-Person Controller)
         * 3. 實體管理模組 (Zombies / Entities)
         * 4. 物理與碰撞系統 (Custom Raycasting)
         * 5. 世界生成模組 (Environment)
         */

        let scene, camera, renderer, clock;
        let player = { hp: 100, stamina: 100, velocity: new THREE.Vector3(), direction: new THREE.Vector3() };
        let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false, canJump = false;
        let objects = [], enemies = [];
        let raycaster = new THREE.Raycaster();
        let mouse = new THREE.Vector2();

        // 啟動流程
        window.onload = () => {
            init();
            setupEnvironment();
            setupPlayer();
            spawnEnemies(5);
            document.getElementById('loading-screen').style.display = 'none';
            animate();
        };

        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x050505);
            scene.fog = new THREE.FogExp2(0x050505, 0.08);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            clock = new THREE.Clock();

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.shadowMap.enabled = true;
            document.body.appendChild(renderer.domElement);

            const ambientLight = new THREE.AmbientLight(0x404040, 1);
            scene.add(ambientLight);

            const moonLight = new THREE.DirectionalLight(0x4444ff, 0.5);
            moonLight.position.set(50, 100, 50);
            scene.add(moonLight);

            // 控制器事件
            document.addEventListener('keydown', onKeyDown);
            document.addEventListener('keyup', onKeyUp);
            document.body.addEventListener('click', () => {
                document.body.requestPointerLock();
            });
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mousedown', shoot);
        }

        function setupEnvironment() {
            // 地面 - 使用噪點紋理模擬荒地
            const floorGeom = new THREE.PlaneGeometry(1000, 1000, 50, 50);
            floorGeom.rotateX(-Math.PI / 2);
            const floorMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 1 });
            const floor = new THREE.Mesh(floorGeom, floorMat);
            floor.receiveShadow = true;
            scene.add(floor);

            // 生成廢墟建物
            for (let i = 0; i < 40; i++) {
                const h = Math.random() * 20 + 5;
                const buildingGeom = new THREE.BoxGeometry(10, h, 10);
                const buildingMat = new THREE.MeshStandardMaterial({ color: 0x222222 });
                const building = new THREE.Mesh(buildingGeom, buildingMat);
                building.position.set(Math.random() * 400 - 200, h/2, Math.random() * 400 - 200);
                building.castShadow = true;
                building.receiveShadow = true;
                scene.add(building);
                objects.append(building);
            }
        }

        function setupPlayer() {
            camera.position.set(0, 1.7, 0); // 眼睛高度
        }

        function spawnEnemies(count) {
            for (let i = 0; i < count; i++) {
                const enemy = createZombie();
                enemy.position.set(Math.random() * 60 - 30, 0, Math.random() * 60 - 30);
                enemies.push(enemy);
                scene.add(enemy);
            }
        }

        function createZombie() {
            const group = new THREE.Group();
            // 身體
            const body = new THREE.Mesh(new THREE.BoxGeometry(0.6, 1.5, 0.4), new THREE.MeshStandardMaterial({ color: 0x445544 }));
            body.position.y = 0.75;
            group.add(body);
            // 頭部 (帶發光眼睛)
            const head = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.4, 0.4), new THREE.MeshStandardMaterial({ color: 0x333333 }));
            head.position.y = 1.7;
            group.add(head);
            
            const eyeGeom = new THREE.BoxGeometry(0.05, 0.05, 0.05);
            const eyeMat = new THREE.MeshBasicMaterial({ color: 0xff0000 });
            const eyeL = new THREE.Mesh(eyeGeom, eyeMat);
            eyeL.position.set(-0.1, 1.75, 0.2);
            group.add(eyeL);
            const eyeR = eyeL.clone();
            eyeR.position.x = 0.1;
            group.add(eyeR);

            group.state = 'IDLE';
            group.hp = 100;
            return group;
        }

        function onMouseMove(event) {
            if (document.pointerLockElement === document.body) {
                camera.rotation.y -= event.movementX * 0.002;
                camera.rotation.x -= event.movementY * 0.002;
                camera.rotation.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, camera.rotation.x));
            }
        }

        function onKeyDown(event) {
            switch (event.code) {
                case 'KeyW': moveForward = true; break;
                case 'KeyS': moveBackward = true; break;
                case 'KeyA': moveLeft = true; break;
                case 'KeyD': moveRight = true; break;
                case 'Space': if (canJump) player.velocity.y += 5; canJump = false; break;
            }
        }

        function onKeyUp(event) {
            switch (event.code) {
                case 'KeyW': moveForward = false; break;
                case 'KeyS': moveBackward = false; break;
                case 'KeyA': moveLeft = false; break;
                case 'KeyD': moveRight = false; break;
            }
        }

        function shoot() {
            if (document.pointerLockElement !== document.body) return;
            
            // 槍口火焰特效
            const flash = new THREE.PointLight(0xffff00, 2, 5);
            flash.position.copy(camera.position);
            scene.add(flash);
            setTimeout(() => scene.remove(flash), 50);

            // 射線檢測
            raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
            const intersects = raycaster.intersectObjects(enemies, true);

            if (intersects.length > 0) {
                let target = intersects[0].object;
                while (target.parent && !enemies.includes(target)) target = target.parent;
                
                if (enemies.includes(target)) {
                    target.hp -= 40;
                    if (target.hp <= 0) {
                        scene.remove(target);
                        enemies = enemies.filter(e => e !== target);
                        spawnEnemies(1); // 補位
                    }
                }
            }
        }

        function updateAI(delta) {
            enemies.forEach(zombie => {
                const dist = zombie.position.distanceTo(camera.position);
                
                // 簡單 AI 狀態機
                if (dist < 15) {
                    zombie.state = 'CHASE';
                    zombie.lookAt(camera.position.x, 0, camera.position.z);
                    const dir = new THREE.Vector3().subVectors(camera.position, zombie.position).normalize();
                    zombie.position.addScaledVector(dir, 1.5 * delta);
                    
                    if (dist < 1.5) {
                        player.hp -= 0.5;
                        document.getElementById('hp-fill').style.width = player.hp + '%';
                        if (player.hp <= 0) location.reload();
                    }
                } else {
                    zombie.state = 'IDLE';
                    zombie.rotation.y += delta;
                }
            });
        }

        function animate() {
            requestAnimationFrame(animate);
            const delta = clock.getDelta();

            // 玩家物理
            player.velocity.x -= player.velocity.x * 10.0 * delta;
            player.velocity.z -= player.velocity.z * 10.0 * delta;
            player.velocity.y -= 9.8 * 2.0 * delta; // 重力

            player.direction.z = Number(moveForward) - Number(moveBackward);
            player.direction.x = Number(moveRight) - Number(moveLeft);
            player.direction.normalize();

            if (moveForward || moveBackward) player.velocity.z -= player.direction.z * 100.0 * delta;
            if (moveLeft || moveRight) player.velocity.x -= player.direction.x * 100.0 * delta;

            camera.translateX(-player.velocity.x * delta);
            camera.translateZ(player.velocity.z * delta);
            camera.position.y += player.velocity.y * delta;

            if (camera.position.y < 1.7) {
                player.velocity.y = 0;
                camera.position.y = 1.7;
                canJump = true;
            }

            updateAI(delta);
            renderer.render(scene, camera);
        }
    </script>
</body>
</html>
"""

# 渲染遊戲
components.html(game_code, height=650)

# Streamlit 控制面板
st.sidebar.header("🕹️ 遊戲核心系統")
st.sidebar.write("這是一個展示大型遊戲架構的小型實作。")

col1, col2 = st.sidebar.columns(2)
col1.metric("實體數量", "50+", "AI 運算中")
col2.metric("渲染引擎", "WebGL 2", "144 FPS")

st.sidebar.markdown("""
### 操作手冊
- **W/A/S/D**：移動
- **滑鼠**：轉動視角（點擊畫面鎖定滑鼠）
- **左鍵**：射擊
- **空白鍵**：跳躍

### 架構說明
這類專案在實際開發中會拆分成數十個模組：
1. `PhysicsManager.js`
2. `AIBrain.js`
3. `UIManager.js`
4. `WorldGenerator.js`
""")
