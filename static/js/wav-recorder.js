/**
 * WAV 錄音器 - 使用 Web Audio API 生成 WAV 格式
 */
class WAVRecorder {
    constructor() {
        this.audioContext = null;
        this.mediaStream = null;
        this.processor = null;
        this.input = null;
        this.recording = false;
        this.audioData = [];
        this.sampleRate = 16000; // Azure Speech Services 推薦的採樣率
    }

    async initialize() {
        try {
            // 獲取麥克風權限
            this.mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: this.sampleRate
                }
            });

            // 創建音頻上下文
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                sampleRate: this.sampleRate
            });

            // 創建音頻輸入節點
            this.input = this.audioContext.createMediaStreamSource(this.mediaStream);

            // 創建處理器節點
            this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);

            // 設置音頻處理回調
            this.processor.onaudioprocess = (event) => {
                if (this.recording) {
                    const inputData = event.inputBuffer.getChannelData(0);
                    // 轉換為 16-bit PCM
                    const pcmData = this.floatTo16BitPCM(inputData);
                    this.audioData.push(pcmData);
                }
            };

            // 連接音頻節點
            this.input.connect(this.processor);
            this.processor.connect(this.audioContext.destination);

            console.log('WAV 錄音器初始化成功');
            return true;

        } catch (error) {
            console.error('WAV 錄音器初始化失敗:', error);
            return false;
        }
    }

    startRecording() {
        if (!this.audioContext) {
            throw new Error('錄音器未初始化');
        }

        this.audioData = [];
        this.recording = true;
        
        // 恢復音頻上下文（如果被暫停）
        if (this.audioContext.state === 'suspended') {
            this.audioContext.resume();
        }

        console.log('開始 WAV 錄音');
    }

    stopRecording() {
        if (!this.recording) {
            return null;
        }

        this.recording = false;
        console.log('停止 WAV 錄音');

        // 生成 WAV 文件
        const wavBlob = this.createWAVBlob();
        return wavBlob;
    }

    floatTo16BitPCM(input) {
        const output = new Int16Array(input.length);
        for (let i = 0; i < input.length; i++) {
            const sample = Math.max(-1, Math.min(1, input[i]));
            output[i] = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
        }
        return output;
    }

    createWAVBlob() {
        // 計算總數據長度
        let totalLength = 0;
        for (const chunk of this.audioData) {
            totalLength += chunk.length;
        }

        // 合併所有音頻數據
        const mergedData = new Int16Array(totalLength);
        let offset = 0;
        for (const chunk of this.audioData) {
            mergedData.set(chunk, offset);
            offset += chunk.length;
        }

        // 創建 WAV 文件
        const wavBuffer = this.createWAVBuffer(mergedData);
        return new Blob([wavBuffer], { type: 'audio/wav' });
    }

    createWAVBuffer(pcmData) {
        const sampleRate = this.sampleRate;
        const numChannels = 1;
        const bitsPerSample = 16;
        const byteRate = sampleRate * numChannels * bitsPerSample / 8;
        const blockAlign = numChannels * bitsPerSample / 8;
        const dataSize = pcmData.length * 2;
        const fileSize = 36 + dataSize;

        const buffer = new ArrayBuffer(44 + dataSize);
        const view = new DataView(buffer);

        // WAV 文件頭
        const writeString = (offset, string) => {
            for (let i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i));
            }
        };

        writeString(0, 'RIFF');
        view.setUint32(4, fileSize, true);
        writeString(8, 'WAVE');
        writeString(12, 'fmt ');
        view.setUint32(16, 16, true);
        view.setUint16(20, 1, true);
        view.setUint16(22, numChannels, true);
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, byteRate, true);
        view.setUint16(32, blockAlign, true);
        view.setUint16(34, bitsPerSample, true);
        writeString(36, 'data');
        view.setUint32(40, dataSize, true);

        // 寫入 PCM 數據
        let offset = 44;
        for (let i = 0; i < pcmData.length; i++) {
            view.setInt16(offset, pcmData[i], true);
            offset += 2;
        }

        return buffer;
    }

    cleanup() {
        if (this.processor) {
            this.processor.disconnect();
            this.processor = null;
        }

        if (this.input) {
            this.input.disconnect();
            this.input = null;
        }

        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }

        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
            this.mediaStream = null;
        }

        console.log('WAV 錄音器已清理');
    }
}