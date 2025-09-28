/**
 * 語音錄製組件 - 使用 WAV 格式
 * 處理音頻錄製和發送到後端
 */
class VoiceRecorder {
    constructor(options = {}) {
        this.wavRecorder = null;
        this.isRecording = false;
        this.recordingTimer = null;
        this.recordingStartTime = null;
        
        // 配置選項
        this.options = {
            sampleRate: 16000,
            maxRecordingTime: 60000, // 最大錄音時間 60 秒
            showRecordingTime: true,  // 顯示錄音時間
            ...options
        };
        
        // 回調函數
        this.onTranscriptionReceived = options.onTranscriptionReceived || null;
        this.onError = options.onError || null;
        this.onRecordingStart = options.onRecordingStart || null;
        this.onRecordingStop = options.onRecordingStop || null;
        
        this.initializeElements();
        this.bindEvents();
        this.initializeWAVRecorder();
    }

    async initializeWAVRecorder() {
        try {
            // 動態載入 WAV 錄音器
            if (typeof WAVRecorder === 'undefined') {
                await this.loadWAVRecorder();
            }
            
            this.wavRecorder = new WAVRecorder();
            const success = await this.wavRecorder.initialize();
            
            if (!success) {
                throw new Error('WAV 錄音器初始化失敗');
            }
            
            console.log('WAV 錄音器初始化成功');
        } catch (error) {
            console.error('WAV 錄音器初始化失敗:', error);
            this.handleError('錄音器初始化失敗，請檢查麥克風權限');
        }
    }

    async loadWAVRecorder() {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = '/static/js/wav-recorder.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
    
    initializeElements() {
        this.recordBtn = document.getElementById('recordBtn');
        this.recordIcon = document.getElementById('recordIcon');
        this.recordText = document.getElementById('recordText');
        this.recordingStatus = document.getElementById('recordingStatus');
        this.transcriptionResult = document.getElementById('transcriptionResult');
        this.transcriptionText = document.getElementById('transcriptionText');
        this.confidenceScore = document.getElementById('confidenceScore');
        this.confidenceBar = document.getElementById('confidenceBar');
        
        // 創建錄音時間顯示元素
        this.createRecordingTimeDisplay();
    }
    
    createRecordingTimeDisplay() {
        // 在錄音狀態區域添加時間顯示
        const recordingStatus = document.getElementById('recordingStatus');
        if (recordingStatus && !document.getElementById('recordingTime')) {
            const timeDisplay = document.createElement('div');
            timeDisplay.id = 'recordingTime';
            timeDisplay.className = 'text-white text-sm font-mono mt-2';
            timeDisplay.textContent = '00:00';
            recordingStatus.appendChild(timeDisplay);
        }
    }
    
    bindEvents() {
        if (this.recordBtn) {
            // 點擊切換錄音狀態
            this.recordBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleRecording();
            });
        }
    }
    
    toggleRecording() {
        if (this.isRecording) {
            this.stopRecording();
        } else {
            this.startRecording();
        }
    }
    
    async startRecording() {
        if (this.isRecording || !this.wavRecorder) return;
        
        try {
            this.wavRecorder.startRecording();
            this.isRecording = true;
            this.recordingStartTime = Date.now();
            
            // 更新UI
            this.updateRecordingUI(true);
            
            // 開始錄音計時器
            this.startRecordingTimer();
            
            // 設置最大錄音時間限制
            if (this.options.maxRecordingTime > 0) {
                setTimeout(() => {
                    if (this.isRecording) {
                        console.log('達到最大錄音時間，自動停止');
                        this.stopRecording();
                        this.showNotification('錄音時間已達上限，已自動停止', 'warning');
                    }
                }, this.options.maxRecordingTime);
            }
            
            // 觸發回調
            if (this.onRecordingStart) {
                this.onRecordingStart();
            }
            
            console.log('開始 WAV 錄音');
            
        } catch (error) {
            console.error('開始錄音失敗:', error);
            this.handleError('無法開始錄音: ' + error.message);
        }
    }
    
    stopRecording() {
        if (!this.isRecording || !this.wavRecorder) return;
        
        try {
            const audioBlob = this.wavRecorder.stopRecording();
            this.isRecording = false;
            
            // 停止計時器
            this.stopRecordingTimer();
            
            // 更新UI
            this.updateRecordingUI(false);
            
            // 觸發回調
            if (this.onRecordingStop) {
                this.onRecordingStop();
            }
            
            // 計算錄音時長
            const recordingDuration = this.recordingStartTime ? 
                (Date.now() - this.recordingStartTime) / 1000 : 0;
            
            console.log(`停止 WAV 錄音，時長: ${recordingDuration.toFixed(1)}秒`);
            
            // 檢查錄音時長
            if (recordingDuration < 0.5) {
                this.handleError('錄音時間太短，請重新錄音');
                return;
            }
            
            // 處理錄音
            if (audioBlob) {
                this.processRecording(audioBlob, recordingDuration);
            }
            
        } catch (error) {
            console.error('停止錄音失敗:', error);
            this.handleError('停止錄音時發生錯誤: ' + error.message);
        }
    }
    
    processRecording(audioBlob, duration = 0) {
        if (!audioBlob || audioBlob.size === 0) {
            this.handleError('沒有錄製到音頻數據');
            return;
        }
        
        console.log(`WAV 音頻處理完成，大小: ${audioBlob.size} bytes，時長: ${duration.toFixed(1)}秒`);
        
        // 檢查音頻文件大小
        const maxSize = 10 * 1024 * 1024; // 10MB 限制
        if (audioBlob.size > maxSize) {
            this.handleError('音頻文件過大，請縮短錄音時間');
            return;
        }
        
        // 發送到服務器
        this.sendAudioToServer(audioBlob, duration);
    }
    
    async sendAudioToServer(audioBlob, duration = 0) {
        try {
            // 顯示處理中狀態
            this.showTranscriptionResult('處理中...', 0);
            
            // 創建 FormData
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');
            formData.append('language', 'zh-HK');
            formData.append('duration', duration.toString());
            
            // 設置較長的超時時間用於長音頻
            const timeoutMs = Math.max(30000, duration * 2000); // 至少30秒，或音頻時長的2倍
            
            // 發送請求
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
            
            const response = await fetch('/api/speech/transcribe', {
                method: 'POST',
                body: formData,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            const result = await response.json();
            
            if (result.success) {
                this.showTranscriptionResult(
                    result.transcription,
                    result.confidence
                );
                
                // 觸發回調
                if (this.onTranscriptionReceived) {
                    this.onTranscriptionReceived(result);
                }
            } else {
                this.handleError(result.error || result.message || '語音識別失敗');
            }
            
        } catch (error) {
            if (error.name === 'AbortError') {
                this.handleError('處理超時，請嘗試縮短錄音時間');
            } else {
                console.error('發送音頻失敗:', error);
                this.handleError('網絡錯誤，請檢查連接');
            }
        }
    }
    
    updateRecordingUI(isRecording) {
        if (this.recordBtn) {
            if (isRecording) {
                this.recordBtn.classList.add('recording-pulse');
                this.recordBtn.classList.remove('animate-glow');
                this.recordBtn.classList.add('bg-gradient-to-br', 'from-green-400', 'to-green-600');
                this.recordBtn.classList.remove('from-red-400', 'to-red-600');
            } else {
                this.recordBtn.classList.remove('recording-pulse');
                this.recordBtn.classList.add('animate-glow');
                this.recordBtn.classList.remove('from-green-400', 'to-green-600');
                this.recordBtn.classList.add('from-red-400', 'to-red-600');
            }
        }
        
        if (this.recordIcon) {
            if (isRecording) {
                this.recordIcon.className = 'fas fa-stop text-3xl text-white group-hover:scale-110 transition-transform duration-300';
            } else {
                this.recordIcon.className = 'fas fa-microphone text-3xl text-white group-hover:scale-110 transition-transform duration-300';
            }
        }
        
        if (this.recordText) {
            this.recordText.textContent = isRecording ? '點擊停止' : '點擊說話';
        }
        
        if (this.recordingStatus) {
            if (isRecording) {
                this.recordingStatus.classList.remove('hidden');
            } else {
                this.recordingStatus.classList.add('hidden');
            }
        }
    }
    
    showTranscriptionResult(text, confidence) {
        if (this.transcriptionResult) {
            this.transcriptionResult.classList.remove('hidden');
        }
        
        if (this.transcriptionText) {
            this.transcriptionText.textContent = text;
        }
        
        if (this.confidenceScore) {
            const percentage = Math.round(confidence * 100);
            this.confidenceScore.textContent = `${percentage}%`;
            
            // 更新信心度顏色
            if (percentage >= 90) {
                this.confidenceScore.className = 'text-sm font-semibold text-green-300';
            } else if (percentage >= 70) {
                this.confidenceScore.className = 'text-sm font-semibold text-yellow-300';
            } else {
                this.confidenceScore.className = 'text-sm font-semibold text-red-300';
            }
        }
        
        if (this.confidenceBar) {
            const percentage = Math.round(confidence * 100);
            this.confidenceBar.style.width = `${percentage}%`;
            
            // 更新進度條顏色
            if (percentage >= 90) {
                this.confidenceBar.className = 'bg-gradient-to-r from-green-400 to-green-500 h-2 rounded-full transition-all duration-500';
            } else if (percentage >= 70) {
                this.confidenceBar.className = 'bg-gradient-to-r from-yellow-400 to-yellow-500 h-2 rounded-full transition-all duration-500';
            } else {
                this.confidenceBar.className = 'bg-gradient-to-r from-red-400 to-red-500 h-2 rounded-full transition-all duration-500';
            }
        }
    }
    
    hideTranscriptionResult() {
        if (this.transcriptionResult) {
            this.transcriptionResult.classList.add('hidden');
        }
    }
    
    handleError(message) {
        console.error('VoiceRecorder 錯誤:', message);
        
        // 重置狀態
        this.isRecording = false;
        this.updateRecordingUI(false);
        
        // 顯示錯誤信息
        this.showTranscriptionResult(`錯誤: ${message}`, 0);
        
        // 觸發錯誤回調
        if (this.onError) {
            this.onError(message);
        }
        
        // 清理資源
        if (this.wavRecorder) {
            // WAV 錄音器會自動清理資源
        }
    }
    
    // 檢查瀏覽器支援
    static isSupported() {
        return !!(navigator.mediaDevices && 
                 navigator.mediaDevices.getUserMedia && 
                 window.AudioContext || window.webkitAudioContext);
    }

    startRecordingTimer() {
        if (!this.options.showRecordingTime) return;
        
        this.recordingTimer = setInterval(() => {
            if (this.isRecording && this.recordingStartTime) {
                const elapsed = (Date.now() - this.recordingStartTime) / 1000;
                const minutes = Math.floor(elapsed / 60);
                const seconds = Math.floor(elapsed % 60);
                const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                
                const timeDisplay = document.getElementById('recordingTime');
                if (timeDisplay) {
                    timeDisplay.textContent = timeString;
                }
                
                // 接近最大時間時警告
                const maxTime = this.options.maxRecordingTime / 1000;
                if (maxTime > 0 && elapsed > maxTime - 10) {
                    const remaining = Math.ceil(maxTime - elapsed);
                    if (remaining > 0) {
                        timeDisplay.textContent = `${timeString} (剩餘${remaining}秒)`;
                        timeDisplay.className = 'text-yellow-300 text-sm font-mono mt-2';
                    }
                }
            }
        }, 100);
    }
    
    stopRecordingTimer() {
        if (this.recordingTimer) {
            clearInterval(this.recordingTimer);
            this.recordingTimer = null;
        }
        
        // 重置時間顯示
        const timeDisplay = document.getElementById('recordingTime');
        if (timeDisplay) {
            timeDisplay.textContent = '00:00';
            timeDisplay.className = 'text-white text-sm font-mono mt-2';
        }
    }
    
    showNotification(message, type = 'info') {
        // 創建通知元素
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm transform transition-all duration-300 translate-x-full opacity-0`;
        
        // 根據類型設置樣式
        switch (type) {
            case 'warning':
                notification.classList.add('bg-yellow-600', 'text-white');
                break;
            case 'error':
                notification.classList.add('bg-red-600', 'text-white');
                break;
            case 'success':
                notification.classList.add('bg-green-600', 'text-white');
                break;
            default:
                notification.classList.add('bg-blue-600', 'text-white');
        }
        
        notification.innerHTML = `
            <div class="flex items-center space-x-2">
                <i class="fas fa-info-circle"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // 顯示動畫
        setTimeout(() => {
            notification.classList.remove('translate-x-full', 'opacity-0');
        }, 100);
        
        // 自動移除
        setTimeout(() => {
            notification.classList.add('translate-x-full', 'opacity-0');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    // 清理資源
    cleanup() {
        this.stopRecordingTimer();
        
        if (this.wavRecorder) {
            this.wavRecorder.cleanup();
            this.wavRecorder = null;
        }
    }
}