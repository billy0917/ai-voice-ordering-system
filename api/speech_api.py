"""
Azure Speech Services REST API 實現 - 適用於 Vercel 無服務器環境
"""
import requests
import json
import os
import base64
import tempfile
from typing import Optional, Dict, Any

class VercelSpeechService:
    """適用於 Vercel 的語音識別服務"""
    
    def __init__(self):
        self.azure_key = os.getenv('AZURE_SPEECH_KEY')
        self.azure_region = os.getenv('AZURE_SPEECH_REGION', 'eastasia')
        self.base_url = f"https://{self.azure_region}.stt.speech.microsoft.com"
        
    def validate_config(self) -> bool:
        """驗證配置"""
        return bool(self.azure_key and self.azure_region)
    
    def transcribe_audio(self, audio_data: bytes, content_type: str = "audio/wav") -> Dict[str, Any]:
        """
        使用 REST API 進行語音識別
        
        Args:
            audio_data: 音頻數據
            content_type: 音頻格式
            
        Returns:
            識別結果字典
        """
        if not self.validate_config():
            return {
                'success': False,
                'error': 'Azure Speech Services 未配置'
            }
        
        try:
            # 構建請求頭
            headers = {
                'Ocp-Apim-Subscription-Key': self.azure_key,
                'Content-Type': content_type,
                'Accept': 'application/json'
            }
            
            # 構建請求 URL
            url = f"{self.base_url}/speech/recognition/conversation/cognitiveservices/v1"
            params = {
                'language': 'zh-HK',  # 香港粵語
                'format': 'detailed'
            }
            
            # 發送請求
            response = requests.post(
                url,
                headers=headers,
                params=params,
                data=audio_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # 解析結果
                if result.get('RecognitionStatus') == 'Success':
                    display_text = result.get('DisplayText', '')
                    confidence = result.get('NBest', [{}])[0].get('Confidence', 0)
                    
                    return {
                        'success': True,
                        'text': display_text,
                        'confidence': confidence,
                        'language': 'zh-HK'
                    }
                else:
                    return {
                        'success': False,
                        'error': f"識別失敗: {result.get('RecognitionStatus')}"
                    }
            else:
                return {
                    'success': False,
                    'error': f"API 請求失敗: {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': '請求超時，請重試'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'網絡請求失敗: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'語音識別錯誤: {str(e)}'
            }
    
    def get_token(self) -> Optional[str]:
        """獲取訪問令牌"""
        if not self.azure_key:
            return None
            
        try:
            url = f"https://{self.azure_region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
            headers = {
                'Ocp-Apim-Subscription-Key': self.azure_key,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.text
            return None
        except:
            return None
