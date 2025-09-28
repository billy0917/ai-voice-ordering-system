"""
語音處理服務 - Azure Speech Services 集成
"""
import azure.cognitiveservices.speech as speechsdk
import logging
import os
import tempfile
import time
import threading
import gc
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class SpeechService:
    """語音識別服務類"""
    
    def __init__(self, azure_key: str, azure_region: str):
        """
        初始化語音服務
        
        Args:
            azure_key: Azure Speech Services API 密鑰
            azure_region: Azure 服務區域
        """
        self.azure_key = azure_key
        self.azure_region = azure_region
        self.speech_config = None
        self._configure_speech_service()
    
    def _configure_speech_service(self):
        """配置 Azure Speech Services"""
        try:
            # 驗證密鑰和區域
            if not self.azure_key or not self.azure_region:
                raise ValueError("Azure Speech Services 密鑰或區域未配置")
            
            # 創建語音配置
            self.speech_config = speechsdk.SpeechConfig(
                subscription=self.azure_key,
                region=self.azure_region
            )
            
            # 設置語言為香港粵語
            self.speech_config.speech_recognition_language = "zh-HK"
            
            # 針對粵語優化的配置
            self.speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceConnection_RecoMode,
                "INTERACTIVE"  # 交互模式，適合短語音
            )
            
            # 配置超時參數
            self.speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, 
                "8000"  # 8秒初始靜音超時
            )
            
            self.speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs, 
                "5000"   # 5秒結束靜音超時
            )
            
            # 設置連接超時
            self.speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceConnection_TranslationToLanguages,
                ""  # 清空翻譯語言，避免不必要的處理
            )
            
            # 禁用某些可能導致問題的功能
            self.speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceResponse_RequestDetailedResultTrueFalse,
                "false"  # 禁用詳細結果，避免上下文驗證問題
            )
            
            # 設置語音服務端點格式
            self.speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceConnection_EndpointId,
                ""  # 使用默認端點
            )
            
            logger.info(f"Azure Speech Services 配置成功 - 區域: {self.azure_region}, 語言: zh-HK (粵語)")
        except Exception as e:
            logger.error(f"Azure Speech Services 配置失敗: {e}")
            raise
    
    def transcribe_audio_sync(self, audio_data: bytes) -> Tuple[bool, str, float]:
        """
        將音頻轉換為文字（同步版本）
        
        Args:
            audio_data: 音頻數據 (bytes)
            
        Returns:
            Tuple[bool, str, float]: (成功標誌, 轉錄文字, 信心度)
        """
        try:
            logger.info(f"開始處理音頻數據，大小: {len(audio_data)} bytes")
            
            # 優先嘗試使用內存流，避免臨時文件問題
            try:
                return self._transcribe_with_stream(audio_data)
            except Exception as stream_error:
                logger.warning(f"內存流識別失敗: {stream_error}，回退到文件方式")
                
            # 回退到文件方式
            return self._transcribe_with_file(audio_data)
                
        except Exception as e:
            logger.error(f"語音識別異常: {e}")
            return False, f"識別異常: {str(e)}", 0.0

    def _transcribe_with_stream(self, audio_data: bytes) -> Tuple[bool, str, float]:
        """
        使用內存流進行語音識別，避免臨時文件
        
        Args:
            audio_data: 音頻數據 (bytes)
            
        Returns:
            Tuple[bool, str, float]: (成功標誌, 轉錄文字, 信心度)
        """
        try:
            import azure.cognitiveservices.speech.audio as audio
            import io
            
            logger.info("使用內存流進行語音識別...")
            
            # 轉換音頻數據
            try:
                converted_audio = self._convert_audio_to_wav(audio_data)
            except Exception as convert_error:
                logger.warning(f"音頻轉換失敗，使用原始數據: {convert_error}")
                converted_audio = audio_data
            
            # 創建內存流
            audio_stream = io.BytesIO(converted_audio)
            
            # 創建推送音頻輸入流
            push_stream = audio.PushAudioInputStream()
            audio_config = audio.AudioConfig(stream=push_stream)
            
            # 創建語音識別器
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            # 將音頻數據寫入流
            chunk_size = 1024
            audio_stream.seek(0)
            
            while True:
                chunk = audio_stream.read(chunk_size)
                if not chunk:
                    break
                push_stream.write(chunk)
            
            push_stream.close()
            
            # 執行識別
            logger.info("開始內存流語音識別...")
            result = speech_recognizer.recognize_once()
            
            return self._process_recognition_result(result)
            
        except Exception as e:
            logger.error(f"內存流識別失敗: {e}")
            raise

    def _transcribe_with_file(self, audio_data: bytes) -> Tuple[bool, str, float]:
        """
        使用臨時文件進行語音識別（備用方法）
        
        Args:
            audio_data: 音頻數據 (bytes)
            
        Returns:
            Tuple[bool, str, float]: (成功標誌, 轉錄文字, 信心度)
        """
        temp_file_path = None
        try:
            logger.info("使用臨時文件進行語音識別...")
            
            # 創建臨時文件並確保完全關閉句柄
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_file_path = temp_file.name
            
            try:
                # 轉換音頻數據
                try:
                    converted_audio = self._convert_audio_to_wav(audio_data)
                    temp_file.write(converted_audio)
                except Exception as convert_error:
                    logger.warning(f"音頻轉換失敗，使用原始數據: {convert_error}")
                    temp_file.write(audio_data)
                
                temp_file.flush()  # 確保數據寫入磁盤
            finally:
                temp_file.close()  # 明確關閉文件句柄
            
            # 短暫延遲，確保文件句柄完全釋放
            time.sleep(0.1)
            
            # 創建音頻配置和識別器
            audio_config = speechsdk.audio.AudioConfig(filename=temp_file_path)
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            # 執行識別
            logger.info("開始文件語音識別...")
            result = speech_recognizer.recognize_once()
            
            return self._process_recognition_result(result)
            
        except Exception as e:
            logger.error(f"文件識別失敗: {e}")
            raise
        finally:
            # 安全清理臨時文件
            if temp_file_path:
                self._safe_cleanup_temp_file(temp_file_path)

    def _process_recognition_result(self, result) -> Tuple[bool, str, float]:
        """
        處理語音識別結果
        
        Args:
            result: Azure Speech SDK 識別結果
            
        Returns:
            Tuple[bool, str, float]: (成功標誌, 轉錄文字, 信心度)
        """
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            logger.info(f"識別成功: {result.text}")
            # 根據結果長度估算信心度
            confidence = min(0.95, len(result.text) / 50.0 + 0.7)
            return True, result.text, confidence
        elif result.reason == speechsdk.ResultReason.NoMatch:
            logger.warning("未識別到語音")
            return False, "未識別到語音內容", 0.0
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logger.error(f"語音識別被取消: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                logger.error(f"錯誤詳情: {cancellation_details.error_details}")
            return False, f"識別錯誤: {cancellation_details.error_details}", 0.0
        else:
            logger.error(f"未知的識別結果: {result.reason}")
            return False, "識別失敗", 0.0

    def _convert_audio_to_wav(self, audio_data: bytes) -> bytes:
        """
        將音頻數據轉換為 WAV 格式，增強兼容性
        
        Args:
            audio_data: 原始音頻數據
            
        Returns:
            bytes: WAV 格式的音頻數據
        """
        try:
            # 檢查是否已經是 WAV 格式
            if audio_data.startswith(b'RIFF') and b'WAVE' in audio_data[:12]:
                logger.info("音頻已經是 WAV 格式，驗證參數...")
                # 驗證是否符合 Azure 要求的格式
                if self._validate_wav_format(audio_data):
                    return audio_data
                else:
                    logger.info("WAV 格式不符合要求，需要重新轉換...")
            
            # 使用 pydub 進行音頻轉換
            try:
                from pydub import AudioSegment
                import io
                
                logger.info("開始音頻格式轉換...")
                
                # 嘗試從不同格式讀取
                audio_segment = None
                supported_formats = ["webm", "mp3", "ogg", "wav", "m4a"]
                
                for format_name in supported_formats:
                    try:
                        audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format=format_name)
                        logger.info(f"成功從 {format_name.upper()} 格式讀取音頻")
                        break
                    except Exception as e:
                        logger.debug(f"{format_name.upper()} 格式讀取失敗: {e}")
                        continue
                
                # 如果所有格式都失敗，嘗試自動檢測
                if audio_segment is None:
                    try:
                        audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))
                        logger.info("成功從自動檢測格式讀取音頻")
                    except Exception as e:
                        logger.error(f"音頻格式自動檢測失敗: {e}")
                        # 最後嘗試原始數據包裝
                        return self._create_raw_wav_wrapper(audio_data)
                
                # 轉換為 Azure Speech Services 要求的格式
                # 16kHz, 16-bit, 單聲道 PCM
                audio_segment = audio_segment.set_frame_rate(16000)
                audio_segment = audio_segment.set_channels(1)
                audio_segment = audio_segment.set_sample_width(2)  # 16-bit
                
                # 導出為 WAV
                wav_io = io.BytesIO()
                audio_segment.export(wav_io, format="wav", parameters=["-acodec", "pcm_s16le"])
                wav_data = wav_io.getvalue()
                
                logger.info(f"音頻轉換成功，原始大小: {len(audio_data)} bytes，轉換後: {len(wav_data)} bytes")
                return wav_data
                
            except ImportError:
                logger.warning("pydub 模塊未安裝，嘗試原始數據包裝...")
                return self._create_raw_wav_wrapper(audio_data)
                
        except Exception as e:
            logger.error(f"音頻轉換失敗: {e}")
            # 作為最後手段，嘗試原始數據包裝
            try:
                return self._create_raw_wav_wrapper(audio_data)
            except:
                raise ValueError(f"音頻轉換完全失敗: {e}")
    
    def _validate_wav_format(self, wav_data: bytes) -> bool:
        """
        驗證 WAV 文件是否符合 Azure Speech Services 要求
        
        Args:
            wav_data: WAV 音頻數據
            
        Returns:
            bool: 是否符合要求
        """
        try:
            import struct
            
            # 檢查 WAV 頭部
            if len(wav_data) < 44:
                return False
                
            # 解析頭部信息
            chunk_id = wav_data[0:4]
            format_tag = wav_data[8:12]
            subchunk1_id = wav_data[12:16]
            
            if chunk_id != b'RIFF' or format_tag != b'WAVE' or subchunk1_id != b'fmt ':
                return False
            
            # 檢查音頻格式參數
            audio_format = struct.unpack('<H', wav_data[20:22])[0]  # 1 = PCM
            num_channels = struct.unpack('<H', wav_data[22:24])[0]  # 1 = 單聲道
            sample_rate = struct.unpack('<I', wav_data[24:28])[0]   # 16000 Hz
            bits_per_sample = struct.unpack('<H', wav_data[34:36])[0]  # 16 bits
            
            # Azure Speech Services 要求
            is_valid = (
                audio_format == 1 and      # PCM
                num_channels == 1 and      # 單聲道
                sample_rate == 16000 and   # 16kHz
                bits_per_sample == 16      # 16-bit
            )
            
            if is_valid:
                logger.debug("WAV 格式驗證通過")
            else:
                logger.debug(f"WAV 格式不符合要求: 格式={audio_format}, 聲道={num_channels}, 採樣率={sample_rate}, 位深={bits_per_sample}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"WAV 格式驗證失敗: {e}")
            return False
    
    def _create_raw_wav_wrapper(self, audio_data: bytes) -> bytes:
        """
        為原始音頻數據創建 WAV 包裝（備用方法）
        
        Args:
            audio_data: 原始音頻數據
            
        Returns:
            bytes: 包裝後的 WAV 數據
        """
        try:
            logger.warning("使用原始數據包裝方法創建 WAV 文件")
            
            # 假設是 16kHz, 16-bit, 單聲道的原始 PCM 數據
            wav_header = self._create_wav_header(len(audio_data))
            wav_data = wav_header + audio_data
            
            logger.info(f"創建 WAV 包裝完成，總大小: {len(wav_data)} bytes")
            return wav_data
                
        except Exception as e:
            logger.error(f"創建 WAV 包裝失敗: {e}")
            raise ValueError(f"無法處理音頻數據: {e}")
    
    def _create_wav_header(self, data_size: int, sample_rate: int = 16000, channels: int = 1, bits_per_sample: int = 16) -> bytes:
        """
        創建 WAV 文件頭
        
        Args:
            data_size: 音頻數據大小
            sample_rate: 採樣率
            channels: 聲道數
            bits_per_sample: 每樣本位數
            
        Returns:
            bytes: WAV 文件頭
        """
        import struct
        
        # WAV 文件頭結構
        byte_rate = sample_rate * channels * bits_per_sample // 8
        block_align = channels * bits_per_sample // 8
        
        header = b'RIFF'
        header += struct.pack('<I', data_size + 36)  # 文件大小
        header += b'WAVE'
        header += b'fmt '
        header += struct.pack('<I', 16)  # fmt chunk 大小
        header += struct.pack('<H', 1)   # 音頻格式 (PCM)
        header += struct.pack('<H', channels)  # 聲道數
        header += struct.pack('<I', sample_rate)  # 採樣率
        header += struct.pack('<I', byte_rate)  # 字節率
        header += struct.pack('<H', block_align)  # 塊對齊
        header += struct.pack('<H', bits_per_sample)  # 每樣本位數
        header += b'data'
        header += struct.pack('<I', data_size)  # 數據大小
        
        return header
    
    def _simple_audio_convert(self, audio_data: bytes) -> bytes:
        """
        簡單的音頻轉換（備用方法）
        
        Args:
            audio_data: 原始音頻數據
            
        Returns:
            bytes: 處理後的音頻數據
        """
        try:
            # 檢查是否已經是 WAV 格式
            if audio_data.startswith(b'RIFF') and b'WAVE' in audio_data[:12]:
                logger.info("音頻已經是 WAV 格式")
                return audio_data
            
            # 如果不是 WAV 格式，嘗試創建一個基本的 WAV 包裝
            logger.warning("音頻格式未知，嘗試創建 WAV 包裝")
            
            # 假設是 16kHz, 16-bit, 單聲道的原始 PCM 數據
            wav_header = self._create_wav_header(len(audio_data))
            wav_data = wav_header + audio_data
            
            logger.info("創建 WAV 包裝完成")
            return wav_data
                
        except Exception as e:
            logger.error(f"簡單音頻轉換錯誤: {e}")
            return audio_data
    
    async def transcribe_audio(self, audio_data: bytes) -> Tuple[bool, str, float]:
        """
        將音頻轉換為文字（異步版本）
        
        Args:
            audio_data: 音頻數據 (bytes)
            
        Returns:
            Tuple[bool, str, float]: (成功標誌, 轉錄文字, 信心度)
        """
        # 目前使用同步版本
        return self.transcribe_audio_sync(audio_data)
    
    def transcribe_audio_continuous(self, audio_data: bytes) -> Tuple[bool, str, float]:
        """
        使用連續識別模式處理音頻（適合有停頓的語音）
        
        Args:
            audio_data: 音頻數據 (bytes)
            
        Returns:
            Tuple[bool, str, float]: (成功標誌, 轉錄文字, 信心度)
        """
        try:
            logger.info(f"開始連續識別處理音頻數據，大小: {len(audio_data)} bytes")
            
            # 創建臨時文件並確保完全關閉句柄
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_file_path = temp_file.name
            
            try:
                # 轉換音頻數據
                try:
                    converted_audio = self._convert_audio_to_wav(audio_data)
                    temp_file.write(converted_audio)
                except Exception as convert_error:
                    logger.warning(f"音頻轉換失敗，使用原始數據: {convert_error}")
                    temp_file.write(audio_data)
                
                temp_file.flush()  # 確保數據寫入磁盤
            finally:
                temp_file.close()  # 明確關閉文件句柄
            
            # 短暫延遲，確保文件句柄完全釋放
            time.sleep(0.1)
            
            try:
                # 創建音頻配置
                audio_config = speechsdk.audio.AudioConfig(filename=temp_file_path)
                
                # 創建語音識別器
                speech_recognizer = speechsdk.SpeechRecognizer(
                    speech_config=self.speech_config,
                    audio_config=audio_config
                )
                
                # 用於收集識別結果
                recognized_texts = []
                recognition_done = threading.Event()
                
                def recognized_handler(evt):
                    """處理識別結果"""
                    if evt.result.text:
                        logger.info(f"識別到文字: {evt.result.text}")
                        recognized_texts.append(evt.result.text)
                
                def session_stopped_handler(evt):
                    """會話停止處理"""
                    logger.info("連續識別會話停止")
                    recognition_done.set()
                
                def canceled_handler(evt):
                    """取消處理"""
                    logger.warning(f"識別被取消: {evt.reason}")
                    if evt.reason == speechsdk.CancellationReason.Error:
                        logger.error(f"錯誤詳情: {evt.error_details}")
                    recognition_done.set()
                
                # 連接事件處理器
                speech_recognizer.recognized.connect(recognized_handler)
                speech_recognizer.session_stopped.connect(session_stopped_handler)
                speech_recognizer.canceled.connect(canceled_handler)
                
                logger.info("開始連續語音識別...")
                
                # 開始連續識別
                speech_recognizer.start_continuous_recognition()
                
                # 等待識別完成，最多等待30秒
                if recognition_done.wait(timeout=30):
                    logger.info("連續識別完成")
                else:
                    logger.warning("連續識別超時")
                
                # 停止識別
                speech_recognizer.stop_continuous_recognition()
                
                # 合併所有識別結果
                if recognized_texts:
                    full_text = " ".join(recognized_texts).strip()
                    logger.info(f"連續識別最終結果: {full_text}")
                    confidence = min(0.95, len(full_text) / 50.0 + 0.7)
                    return True, full_text, confidence
                else:
                    logger.warning("連續識別未得到任何結果")
                    return False, "未識別到語音內容", 0.0
                    
            finally:
                # 安全清理臨時文件
                self._safe_cleanup_temp_file(temp_file_path)
                
        except Exception as e:
            logger.error(f"連續語音識別異常: {e}")
            return False, f"識別異常: {str(e)}", 0.0
    
    def transcribe_audio_with_fallback(self, audio_data: bytes, max_retries: int = 2) -> Tuple[bool, str, float]:
        """
        帶回退機制和重試的語音識別
        
        Args:
            audio_data: 音頻數據 (bytes)
            max_retries: 最大重試次數
            
        Returns:
            Tuple[bool, str, float]: (成功標誌, 轉錄文字, 信心度)
        """
        last_error = None
        
        # 嘗試不同的識別策略
        strategies = [
            ("單次識別", self.transcribe_audio_sync),
            ("連續識別", self.transcribe_audio_continuous)
        ]
        
        for retry_count in range(max_retries + 1):
            for strategy_name, strategy_func in strategies:
                try:
                    logger.info(f"嘗試 {strategy_name} (第 {retry_count + 1} 次)")
                    success, text, confidence = strategy_func(audio_data)
                    
                    if success and text.strip():
                        logger.info(f"{strategy_name} 成功: {text}")
                        return success, text, confidence
                    else:
                        logger.warning(f"{strategy_name} 無結果: {text}")
                        last_error = text
                        
                except Exception as e:
                    error_str = str(e)
                    logger.warning(f"{strategy_name} 失敗: {error_str}")
                    last_error = error_str
                    
                    # 檢查是否是特定錯誤，需要特殊處理
                    if "1007" in error_str or "Could not validate speech context" in error_str:
                        logger.info("檢測到上下文驗證錯誤，重新初始化語音服務...")
                        try:
                            self._configure_speech_service()
                        except Exception as config_error:
                            logger.error(f"重新配置語音服務失敗: {config_error}")
                    
                    # 如果是最後一次重試，不需要繼續
                    if retry_count == max_retries:
                        break
                    
                    # 短暫延遲後重試
                    time.sleep(1.0)
        
        # 所有策略都失敗了
        error_message = f"所有識別策略都失敗了。最後錯誤: {last_error or '未知錯誤'}"
        logger.error(error_message)
        return False, error_message, 0.0

    def _safe_cleanup_temp_file(self, temp_file_path: str, max_retries: int = 5, delay: float = 0.3):
        """
        增強的安全清理臨時文件，專門處理 Windows 文件佔用問題
        
        Args:
            temp_file_path: 臨時文件路徑
            max_retries: 最大重試次數
            delay: 重試間隔（秒）
        """
        import sys
        import subprocess
        
        for attempt in range(max_retries):
            try:
                # 第一步：強制垃圾回收和延遲
                if attempt > 0:
                    gc.collect()
                    time.sleep(delay * attempt)  # 遞增延遲
                
                # 檢查文件是否存在
                if not os.path.exists(temp_file_path):
                    logger.debug(f"臨時文件已不存在: {temp_file_path}")
                    return
                
                # 第二步：嘗試標準刪除
                os.unlink(temp_file_path)
                logger.debug(f"成功清理臨時文件: {temp_file_path}")
                return
                    
            except PermissionError as e:
                logger.warning(f"清理嘗試 {attempt + 1}/{max_retries} (權限錯誤): {e}")
                
                # Windows 特殊處理
                if sys.platform.startswith('win') and attempt < max_retries - 1:
                    try:
                        # 嘗試使用 Windows del 命令強制刪除
                        result = subprocess.run(
                            ['del', '/F', '/Q', f'"{temp_file_path}"'],
                            shell=True,
                            capture_output=True,
                            timeout=5,
                            text=True
                        )
                        
                        # 檢查是否成功刪除
                        if not os.path.exists(temp_file_path):
                            logger.info(f"使用 del 命令成功清理: {temp_file_path}")
                            return
                        elif result.returncode == 0:
                            logger.debug(f"del 命令執行成功但文件仍存在")
                            
                    except subprocess.TimeoutExpired:
                        logger.warning(f"del 命令超時")
                    except Exception as cmd_error:
                        logger.debug(f"del 命令失敗: {cmd_error}")
                    
            except OSError as e:
                if e.errno == 32 or "being used by another process" in str(e):
                    logger.warning(f"清理嘗試 {attempt + 1}/{max_retries} (文件被佔用): {e}")
                    
                    # 最後一次嘗試時，標記文件為待刪除
                    if attempt == max_retries - 1:
                        try:
                            import random
                            pending_name = f"{temp_file_path}.delete_{int(time.time())}_{random.randint(1000,9999)}"
                            os.rename(temp_file_path, pending_name)
                            logger.info(f"文件標記為待清理: {pending_name}")
                            
                            # 嘗試使用後台任務清理
                            if sys.platform.startswith('win'):
                                try:
                                    # 創建一個延遲刪除的批處理命令
                                    subprocess.Popen(
                                        f'timeout /t 5 >nul && del /F /Q "{pending_name}"',
                                        shell=True,
                                        creationflags=subprocess.CREATE_NO_WINDOW
                                    )
                                    logger.debug(f"已安排延遲刪除任務")
                                except:
                                    pass
                            return
                            
                        except Exception as rename_error:
                            logger.error(f"無法重命名文件為待刪除: {rename_error}")
                else:
                    logger.error(f"清理時發生未知 OSError: {e}")
                    break
                    
            except Exception as e:
                logger.error(f"清理時發生未知異常: {e}")
                break
        
        # 所有嘗試都失敗了 - 靜默處理，避免日誌噪音
        logger.debug(f"臨時文件將由系統稍後清理: {temp_file_path}")
        # 不再輸出錯誤信息，因為這是 Windows 上的常見情況，不影響功能

    def configure_for_cantonese(self):
        """配置粵語識別參數"""
        if self.speech_config:
            # 設置語言為香港粵語
            self.speech_config.speech_recognition_language = "zh-HK"
            # 可以添加更多粵語特定配置
            logger.info("粵語識別參數配置完成")