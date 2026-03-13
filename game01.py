import streamlit as st
import streamlit.components.v1 as components

# 設定頁面
st.set_page_config(page_title="3D 醫療大冒險", page_icon="🏥", layout="centered")

st.title("🏥 3D 醫療大冒險 (GLB 模型支援)")
st.write("這是一個使用 Three.js 驅動的 3D 遊戲環境，你可以將 GLB 模型替換到場景中。")

# 遊戲的核心 HTML 與 JavaScript 代碼 (使用 Three.js)
game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; background: #222; overflow: hidden; font-family: 'Arial', sans-serif; }
        #ui { position: absolute; top: 10px; width: 100%; display: flex; justify-content: space-around; color: #ff0000; font-weight: bold; font-size: 20px; pointer-events: none; z-index: 10; }
        #toolbar { position: absolute; bottom: 20px; width: 100%; display: flex; justify-content: center; gap: 10px; z-index: 10; }
        .tool { width: 60px; height: 60px; background: rgba(255,255,255,0.8); border: 3px solid #666; border-radius: 10px; display: flex; justify-content: center; align-items: center; font-size: 30px; cursor: pointer; }
        .tool.active { background: #fff; border-color: #00ff00; }
        canvas { display: block; }
    </style>
</head>
<body>
    <div id="ui">
        <div>❤️ HP: <span id="hp">100</span></div>
        <div>⏱️ 狀態：準備手術</div>
    </div>
    
    <div id="toolbar">
        <div class="tool active" id="tool-knife">🔪</div>
        <div class="tool" id="tool-pincer">✂️</div>
        <div class="tool" id="tool-gel">🧪</div>
    </div>

    <!-- 載入 Three.js 庫 -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <!-- 載入 GLTF 載入器 -->
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>

    <script>
        let scene, camera, renderer, model;
        let hp = 100;

        function init() {
            // 1. 建立場景
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0xf5d0b0); // 皮膚色背景

            // 2. 建立攝影機
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.z = 5;

            // 3. 建立渲染器
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            // 4. 加入燈光
            const light = new THREE.DirectionalLight(0xffffff, 1);
            light.position.set(5, 5, 5).normalize();
            scene.add(light);
            scene.add(new THREE.AmbientLight(0x404040));

            // 5. 載入 GLB 模型 (這裡是關鍵)
            const loader = new THREE.GLTFLoader();
            
            // 注意：這裡放置你的 GLB 檔案路徑
            // 例如：'https://your-domain.com/path/to/your_model.glb'
            const modelUrl = 'https://threejs.org/examples/models/gltf/LeePerrySmith/LeePerrySmith.glb'; 

            loader.load(modelUrl, function (gltf) {
                model = gltf.scene;
                model.scale.set(0.5, 0.5, 0.5); // 根據模型大小調整縮放
                scene.add(model);
                console.log("模型載入成功！");
            }, undefined, function (error) {
                console.error("載入失敗：", error);
                // 失敗時畫一個簡單的立方體代替
                const geometry = new THREE.BoxGeometry(2, 2, 2);
                const material = new THREE.MeshPhongMaterial({ color: 0xff0000 });
                model = new THREE.Mesh(geometry, material);
                scene.add(model);
            });

            // 滑鼠互動
            window.addEventListener('mousemove', onMouseMove);
            animate();
        }

        function onMouseMove(event) {
            if (model) {
                // 讓模型隨滑鼠微動，增加立體感
                model.rotation.y = (event.clientX / window.innerWidth - 0.5) * 0.5;
                model.rotation.x = (event.clientY / window.innerHeight - 0.5) * 0.5;
            }
        }

        function animate() {
            requestAnimationFrame(animate);
            if (hp > 0) hp -= 0.01;
            document.getElementById('hp').innerText = Math.floor(hp);
            renderer.render(scene, camera);
        }

        window.onload = init;
    </script>
</body>
</html>
"""

components.html(game_code, height=600)

st.sidebar.markdown("""
### 🛠️ 替換 3D 模型說明
如果你有自己的 `.glb` 檔案，請按以下步驟操作：
1. **託管檔案**：將你的 GLB 檔案上傳到 GitHub 或其他雲端空間，取得直連網址。
2. **修改代碼**：在 `app.py` 搜尋 `modelUrl`，將其更換為你的網址。
3. **調整縮放**：使用 `model.scale.set(x, y, z)` 來符合畫面大小。
4. **模型操作**：你可以使用 `THREE.Raycaster` 來檢測滑鼠是否點擊到模型上的特定區域（例如傷口）。
""")
