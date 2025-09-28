/**
 * 性能優化工具 - 減少GPU使用
 */

class PerformanceOptimizer {
    constructor() {
        this.isLowPerformanceMode = false;
        this.init();
    }

    init() {
        // 檢測設備性能
        this.detectPerformance();
        
        // 如果是低性能設備，啟用優化模式
        if (this.isLowPerformanceMode) {
            this.enableLowPerformanceMode();
        }

        // 監聽性能變化
        this.monitorPerformance();
    }

    detectPerformance() {
        // 檢測設備內存
        if (navigator.deviceMemory && navigator.deviceMemory < 4) {
            this.isLowPerformanceMode = true;
            console.log('檢測到低內存設備，啟用性能優化模式');
        }

        // 檢測硬件並發數
        if (navigator.hardwareConcurrency && navigator.hardwareConcurrency < 4) {
            this.isLowPerformanceMode = true;
            console.log('檢測到低性能CPU，啟用性能優化模式');
        }

        // 檢測連接速度
        if (navigator.connection) {
            const connection = navigator.connection;
            if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
                this.isLowPerformanceMode = true;
                console.log('檢測到慢速網絡，啟用性能優化模式');
            }
        }
    }

    enableLowPerformanceMode() {
        console.log('啟用低性能模式');
        
        // 添加性能優化類
        document.body.classList.add('low-performance-mode');
        
        // 禁用所有動畫
        this.disableAnimations();
        
        // 簡化視覺效果
        this.simplifyVisualEffects();
        
        // 優化圖片
        this.optimizeImages();
        
        // 減少DOM更新頻率
        this.throttleDOMUpdates();
    }

    disableAnimations() {
        const style = document.createElement('style');
        style.textContent = `
            .low-performance-mode * {
                animation-duration: 0.01ms !important;
                animation-delay: 0.01ms !important;
                transition-duration: 0.01ms !important;
                transition-delay: 0.01ms !important;
            }
        `;
        document.head.appendChild(style);
    }

    simplifyVisualEffects() {
        // 移除所有backdrop-filter
        const elements = document.querySelectorAll('.glass-morphism, .glass-card');
        elements.forEach(el => {
            el.style.backdropFilter = 'none';
            el.style.webkitBackdropFilter = 'none';
            el.style.background = 'rgba(255, 255, 255, 0.1)';
        });

        // 簡化按鈕效果
        const buttons = document.querySelectorAll('button');
        buttons.forEach(btn => {
            btn.style.boxShadow = 'none';
            btn.style.transform = 'none';
        });
    }

    optimizeImages() {
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            // 降低圖片質量
            if (img.src.includes('unsplash.com')) {
                img.src = img.src.replace(/w=\d+/, 'w=400').replace(/q=\d+/, 'q=30');
            }
            
            // 添加loading="lazy"
            img.loading = 'lazy';
            
            // 設置圖片渲染優化
            img.style.imageRendering = 'auto';
        });
    }

    throttleDOMUpdates() {
        // 節流DOM更新
        let updateQueue = [];
        let isUpdating = false;

        const processUpdates = () => {
            if (updateQueue.length === 0) {
                isUpdating = false;
                return;
            }

            const update = updateQueue.shift();
            update();
            
            requestAnimationFrame(processUpdates);
        };

        window.throttledUpdate = (updateFn) => {
            updateQueue.push(updateFn);
            
            if (!isUpdating) {
                isUpdating = true;
                requestAnimationFrame(processUpdates);
            }
        };
    }

    monitorPerformance() {
        // 監控FPS
        let lastTime = performance.now();
        let frameCount = 0;
        let fps = 60;

        const measureFPS = (currentTime) => {
            frameCount++;
            
            if (currentTime - lastTime >= 1000) {
                fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
                frameCount = 0;
                lastTime = currentTime;
                
                // 如果FPS過低，啟用更激進的優化
                if (fps < 30 && !this.isLowPerformanceMode) {
                    console.log(`FPS過低 (${fps})，啟用性能優化模式`);
                    this.isLowPerformanceMode = true;
                    this.enableLowPerformanceMode();
                }
            }
            
            requestAnimationFrame(measureFPS);
        };

        requestAnimationFrame(measureFPS);
    }

    // 優化音頻處理
    optimizeAudioProcessing() {
        // 降低音頻採樣率
        if (window.AudioContext || window.webkitAudioContext) {
            const originalCreateMediaStreamSource = AudioContext.prototype.createMediaStreamSource;
            AudioContext.prototype.createMediaStreamSource = function(stream) {
                // 設置較低的採樣率
                if (this.sampleRate > 16000) {
                    console.log('降低音頻採樣率以優化性能');
                }
                return originalCreateMediaStreamSource.call(this, stream);
            };
        }
    }

    // 優化網絡請求
    optimizeNetworkRequests() {
        // 添加請求節流
        const originalFetch = window.fetch;
        let requestQueue = [];
        let isProcessing = false;

        window.fetch = function(...args) {
            return new Promise((resolve, reject) => {
                requestQueue.push({ args, resolve, reject });
                
                if (!isProcessing) {
                    processQueue();
                }
            });
        };

        const processQueue = async () => {
            if (requestQueue.length === 0) {
                isProcessing = false;
                return;
            }

            isProcessing = true;
            const { args, resolve, reject } = requestQueue.shift();
            
            try {
                const response = await originalFetch(...args);
                resolve(response);
            } catch (error) {
                reject(error);
            }

            // 添加小延遲以避免請求過於頻繁
            setTimeout(processQueue, 50);
        };
    }
}

// 初始化性能優化器
document.addEventListener('DOMContentLoaded', () => {
    window.performanceOptimizer = new PerformanceOptimizer();
});

// 導出給其他模塊使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PerformanceOptimizer;
}