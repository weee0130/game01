<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D GLB 模型預覽器</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { margin: 0; background-color: #111; overflow: hidden; }
        #canvas-container { width: 100vw; height: 100vh; cursor: move; }
        .ui-panel { position: absolute; top: 20px; left: 20px; z-index: 10; pointer-events: none; }
        .ui-element { pointer-events: auto; }
        #drop-zone {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.5); display: none;
            justify-content: center; align-items: center; z-index: 50;
            border: 4px dashed #3b82f6;
        }
        #loading { display: none; }
    </style>
</head>
<body>

    <div id="drop-zone" class="text-white text-3xl font-bold">
        放開滑鼠以上傳模型
    </div>

    <div class="ui-panel space-y-4">
        <div class="ui-element bg-white/10 backdrop-blur-md p-6 rounded-2xl border border-white/20 shadow-2xl max-w-sm">
            <h1 class="text-white text-xl font-bold mb-2">3D 模型預覽器</h1>
            <p class="text-gray-300 text-sm mb-4">支援 GLB / GLTF 格式</p>
            
            <label class="block">
                <span class="sr-only">選擇模型</span>
                <input type="file" id="file-input" accept=".glb,.gltf" 
                    class="block w-full text-sm text-gray-400
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-full file:border-0
                    file:text-sm file:font-semibold
                    file:bg-blue-600 file:text-white
                    hover:file:bg-blue-700 cursor-pointer">
            </label>

            <div id="loading" class="mt-4 flex items-center space-x-2 text-blue-400">
                <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>正在加載模型...</span>
            </div>
        </div>

        <div class="ui-element bg-black/40 backdrop-blur-sm p-4 rounded-xl border border-white/10 text-white text-xs">
            <p>● 左鍵旋轉模型</p>
            <p>● 滾輪縮放視角</p>
            <p>● 右鍵平移相機</p>
        </div>
    </div>

    <div id="canvas-container"></div>

    <script>
        let scene, camera, renderer, controls, currentModel;

        function init() {
            // 初始化場景
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x1a1a1a);

            // 初始化相機
            camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(5, 5, 5);

            // 初始化渲染器
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.outputEncoding = THREE.sRGBEncoding;
            renderer.shadowMap.enabled = true;
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            // 控制器
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;

            // 燈光
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);

            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(5, 10, 7);
            directionalLight.castShadow = true;
            scene.add(directionalLight);

            const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.4);
            scene.add(hemiLight);

            // 輔助網格
            const grid = new THREE.GridHelper(20, 20, 0x444444, 0x222222);
            scene.add(grid);

            animate();
        }

        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }

        // 處理模型讀取
        function loadModel(url) {
            if (currentModel) scene.remove(currentModel);
            
            document.getElementById('loading').style.display = 'flex';
            const loader = new THREE.GLTFLoader();
            
            loader.load(url, (gltf) => {
                currentModel = gltf.scene;
                
                // 自動居中與調整比例
                const box = new THREE.Box3().setFromObject(currentModel);
                const center = box.getCenter(new THREE.Vector3());
                const size = box.getSize(new THREE.Vector3());
                
                currentModel.position.x += (currentModel.position.x - center.x);
                currentModel.position.y += (currentModel.position.y - center.y);
                currentModel.position.z += (currentModel.position.z - center.z);
                
                // 調整相機距離
                const maxDim = Math.max(size.x, size.y, size.z);
                const fov = camera.fov * (Math.PI / 180);
                let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
                cameraZ *= 1.5; // 留點邊距
                
                camera.position.set(cameraZ, cameraZ, cameraZ);
                camera.lookAt(center);
                controls.target.set(0, 0, 0);
                controls.update();

                scene.add(currentModel);
                document.getElementById('loading').style.display = 'none';
            }, undefined, (error) => {
                console.error(error);
                alert('模型載入失敗，請確認檔案格式是否正確。');
                document.getElementById('loading').style.display = 'none';
            });
        }

        // 監聽視窗變化
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        // 檔案上傳處理
        document.getElementById('file-input').addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const url = URL.createObjectURL(file);
                loadModel(url);
            }
        });

        // 拖放處理
        const dropZone = document.getElementById('drop-zone');
        window.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.style.display = 'flex';
        });
        dropZone.addEventListener('dragleave', () => {
            dropZone.style.display = 'none';
        });
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.style.display = 'none';
            const file = e.dataTransfer.files[0];
            if (file && (file.name.endsWith('.glb') || file.name.endsWith('.gltf'))) {
                const url = URL.createObjectURL(file);
                loadModel(url);
            }
        });

        init();
    </script>
</body>
</html>
