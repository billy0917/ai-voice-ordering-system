"""
語音處理相關路由 - 純 Azure Speech Services
"""
from flask import Blueprint, request, jsonify, current_app
from services.speech_service import SpeechService
import logging
import time

speech_bp = Blueprint('speech', __name__)
logger = logging.getLogger(__name__)

# 全局語音服務實例
speech_service = None

def get_speech_service():
    """獲取語音服務實例"""
    global speech_service
    if speech_service is None:
        azure_key = current_app.config.get('AZURE_SPEECH_KEY')
        azure_region = current_app.config.get('AZURE_SPEECH_REGION')
        
        if not azure_key or not azure_region:
            logger.error("Azure Speech Services 配置不完整")
            raise ValueError("Azure Speech Services 配置不完整")
        
        try:
            speech_service = SpeechService(azure_key, azure_region)
            logger.info("語音服務初始化成功")
        except Exception as e:
            logger.error(f"語音服務初始化失敗: {e}")
            raise
    
    return speech_service

@speech_bp.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """
    語音轉錄端點 - 純 Azure Speech Services
    """
    start_time = time.time()
    
    try:
        # 檢查是否有音頻文件
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': '未找到音頻文件'
            }), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': '音頻文件為空'
            }), 400
        
        logger.info("收到語音轉錄請求")
        
        # 讀取音頻數據
        audio_data = audio_file.read()
        logger.info(f"音頻文件大小: {len(audio_data)} bytes")
        
        # 獲取語音服務
        try:
            service = get_speech_service()
        except Exception as e:
            logger.error(f"無法獲取語音服務: {e}")
            return jsonify({
                'success': False,
                'error': f'Azure Speech Services 配置錯誤: {str(e)}',
                'processing_time': round(time.time() - start_time, 2)
            }), 500
        
        # 使用 Azure Speech Services 進行語音識別（帶回退機制）
        logger.info("使用 Azure Speech Services 進行語音識別")
        
        success, transcription, confidence = service.transcribe_audio_with_fallback(audio_data)
        processing_time = time.time() - start_time
        
        if success:
            logger.info(f"語音識別成功: {transcription}")
            return jsonify({
                'success': True,
                'transcription': transcription,
                'confidence': confidence,
                'processing_time': round(processing_time, 2),
                'mode': 'azure_speech_services'
            })
        else:
            logger.warning(f"語音識別失敗: {transcription}")
            return jsonify({
                'success': False,
                'error': transcription,
                'processing_time': round(processing_time, 2),
                'mode': 'azure_speech_services'
            }), 400
        
    except Exception as e:
        logger.error(f"語音轉錄錯誤: {e}")
        processing_time = time.time() - start_time
        
        return jsonify({
            'success': False,
            'error': f'語音處理失敗: {str(e)}',
            'processing_time': round(processing_time, 2)
        }), 500

@speech_bp.route('/test', methods=['GET'])
def test_speech_service():
    """測試語音服務配置"""
    try:
        service = get_speech_service()
        
        return jsonify({
            'success': True,
            'message': 'Azure Speech Services 配置正常',
            'region': current_app.config.get('AZURE_SPEECH_REGION'),
            'mode': 'azure_speech_services'
        })
        
    except Exception as e:
        logger.error(f"測試語音服務失敗: {e}")
        return jsonify({
            'success': False,
            'error': f'Azure Speech Services 測試失敗: {str(e)}'
        }), 500