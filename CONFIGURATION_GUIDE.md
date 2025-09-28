# 零差錯 AI 語音點餐系統 - 配置指南

## 🔧 環境變數配置

### 必需配置項

創建 `.env` 文件並配置以下必需的環境變數：

```bash
# Azure Speech Services 配置
AZURE_SPEECH_KEY=your-azure-speech-key-here
AZURE_SPEECH_REGION=your-azure-region-here

# OpenRouter API 配置  
OPENROUTER_API_KEY=your-openrouter-api-key-here
```

### 獲取 Azure Speech Services 配置

1. 訪問 [Azure Portal](https://portal.azure.com)
2. 創建或選擇現有的 Speech Services 資源
3. 在「密鑰和端點」頁面中獲取：
   - **AZURE_SPEECH_KEY**: 密鑰1 或 密鑰2
   - **AZURE_SPEECH_REGION**: 區域（如：eastus、westus、southeastasia）

### 獲取 OpenRouter API 密鑰

1. 訪問 [OpenRouter](https://openrouter.ai)
2. 註冊賬戶並獲取 API 密鑰
3. 將密鑰設置為 `OPENROUTER_API_KEY`

## 🛠️ 語音識別錯誤修復

### Error Code 1007 修復

您遇到的 `Error code: 1007. Could not validate speech context` 錯誤已通過以下方式修復：

1. **粵語語音服務優化**: 保持粵語 `zh-HK` 設置，但優化連接模式和配置參數
2. **音頻格式驗證**: 確保音頻格式符合 Azure 要求（16kHz, 16-bit, 單聲道）
3. **連接配置優化**: 禁用可能導致上下文驗證問題的功能
4. **重試機制**: 添加智能重試和錯誤恢復機制

### 臨時文件清理問題修復

`[WinError 32] 程序無法存取檔案` 錯誤已通過以下方式解決：

1. **安全清理機制**: 使用重試機制處理文件佔用問題
2. **垃圾回收**: 強制釋放文件句柄
3. **延遲清理**: 適當延遲確保文件不被佔用
4. **標記待清理**: 無法立即清理時標記文件待系統重啟後清理

## 🔄 測試修復結果

運行以下命令測試系統：

```bash
# 啟動開發服務器
python run_dev.py

# 或使用 Flask 直接運行
python app.py
```

## 📋 完整的 .env 文件模板

```bash
# Flask 應用配置
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True

# Azure Speech Services 配置
AZURE_SPEECH_KEY=your-azure-speech-key-here
AZURE_SPEECH_REGION=your-azure-region-here

# OpenRouter API 配置
OPENROUTER_API_KEY=your-openrouter-api-key-here
OPENROUTER_MODEL=x-ai/grok-4-fast:free

# 網站信息
SITE_URL=http://localhost:5000
SITE_NAME=零差錯 AI 語音點餐系統

# 數據庫配置
DATABASE_URL=sqlite:///voice_ordering.db

# 日誌配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# 音頻處理配置
MAX_AUDIO_SIZE=10485760
API_TIMEOUT=30
MAX_RETRIES=3
```

## 🚀 修復內容總結

1. ✅ **修復 Azure Speech 錯誤 1007**: 優化語音服務配置，改善兼容性
2. ✅ **修復臨時文件清理問題**: 實現安全的文件清理機制
3. ✅ **改善音頻格式處理**: 增強音頻轉換和驗證功能
4. ✅ **添加錯誤處理機制**: 實現智能重試和錯誤恢復
5. ✅ **優化語音識別策略**: 多種識別方法的回退機制

現在語音識別系統應該能夠穩定運行，不再出現之前的錯誤！
