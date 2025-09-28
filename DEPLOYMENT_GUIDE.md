# 🚀 部署指南 - 零差錯 AI 語音點餐系統

本指南將幫助您將系統部署到各種雲端平台，創建可分享的"Try it out"演示鏈接。

## 📋 部署前準備

### 1. 準備 API 密鑰
您需要以下 API 服務：
- **Azure Speech Services**: [申請地址](https://azure.microsoft.com/zh-tw/services/cognitive-services/speech-services/)
- **OpenRouter API**: [申請地址](https://openrouter.ai/)

### 2. GitHub Repository 設置
```bash
# 初始化 Git（如果尚未初始化）
git init

# 添加所有文件
git add .

# 創建初始提交
git commit -m "Initial commit: AI Voice Ordering System"

# 添加遠程倉庫（替換為您的 GitHub 用戶名）
git remote add origin https://github.com/您的用戶名/ai-voice-ordering-system.git

# 推送到 GitHub
git push -u origin main
```

## 🔧 推薦部署平台

### 選項 1: Vercel (推薦 - 最簡單)

**優點**: 
- 免費層慷慨
- 自動 HTTPS
- 全球 CDN
- 與 GitHub 集成完美

**步驟**:
1. 訪問 [vercel.com](https://vercel.com)
2. 用 GitHub 帳戶登錄
3. 點擊 "New Project"
4. 選擇您的 `ai-voice-ordering-system` repository
5. 添加環境變量：
   ```
   AZURE_SPEECH_KEY=您的Azure密鑰
   AZURE_SPEECH_REGION=您的Azure區域
   OPENROUTER_API_KEY=您的OpenRouter密鑰
   FLASK_ENV=production
   ```
6. 點擊 "Deploy"
7. 等待部署完成（通常 2-3 分鐘）

**完成後，您會得到類似這樣的鏈接**:
`https://ai-voice-ordering-system.vercel.app`

### 選項 2: Railway (對 Python 支持最好)

**優點**:
- 對 Python/Flask 優化
- 自動檢測配置
- 免費使用額度

**步驟**:
1. 訪問 [railway.app](https://railway.app)
2. 用 GitHub 帳戶登錄
3. 點擊 "New Project" → "Deploy from GitHub repo"
4. 選擇您的 repository
5. Railway 會自動檢測到 `railway.toml` 配置
6. 添加相同的環境變量
7. 自動部署

### 選項 3: Render (免費層穩定)

**優點**:
- 免費層穩定
- 自動 SSL
- 支持自定義域名

**步驟**:
1. 訪問 [render.com](https://render.com)
2. 用 GitHub 帳戶登錄
3. 點擊 "New Web Service"
4. 連接您的 GitHub repository
5. Render 會自動檢測到 `render.yaml` 配置
6. 添加環境變量
7. 部署

## 🔐 環境變量配置

在各平台添加以下環境變量：

```bash
# 必需變量
AZURE_SPEECH_KEY=your-azure-speech-key
AZURE_SPEECH_REGION=your-azure-region
OPENROUTER_API_KEY=your-openrouter-api-key

# 推薦設置
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
SITE_NAME=零差錯 AI 語音點餐系統

# 可選優化
MAX_AUDIO_SIZE=10485760
API_TIMEOUT=30
```

## 📱 部署後驗證

部署完成後，請驗證以下功能：

### 1. 健康檢查
訪問 `https://your-domain.com/health`
應該返回：
```json
{
  "status": "healthy",
  "service": "零差錯 AI 語音點餐系統",
  "version": "1.0.0"
}
```

### 2. 靜態文件檢查
訪問 `https://your-domain.com/debug/static`
確認所有靜態文件路徑正確

### 3. 功能測試
- 顧客界面: `https://your-domain.com`
- 管理員界面: `https://your-domain.com/admin`
- 麥克風權限測試
- 語音識別功能

## 🔗 更新演示鏈接

部署成功後，請更新 `README.md` 中的演示鏈接：

```markdown
**[👉 點擊這裡體驗演示](https://your-actual-domain.com)**
```

## 🛠️ 故障排除

### 常見問題

1. **靜態文件 404 錯誤**
   - 檢查 `vercel.json` 中的路由配置
   - 確認靜態文件夾結構正確

2. **API 密鑰錯誤**
   - 在平台設置中重新檢查環境變量
   - 確認密鑰格式和權限

3. **麥克風權限問題**
   - 確保部署平台支持 HTTPS（現代瀏覽器要求）
   - 所有推薦平台都自動提供 HTTPS

4. **語音識別失敗**
   - 檢查 Azure Speech Services 配額
   - 確認 OpenRouter API 餘額

### 調試技巧

1. **查看應用日誌**:
   - Vercel: 在控制台的 "Functions" 標籤查看
   - Railway: 在控制台的 "Deployments" 查看
   - Render: 在控制台的 "Logs" 查看

2. **測試 API 端點**:
   ```bash
   curl https://your-domain.com/health
   curl https://your-domain.com/debug/static
   ```

## 📈 性能優化建議

1. **啟用緩存**: 大多數平台自動啟用
2. **監控使用量**: 設置 API 使用量警報
3. **域名設置**: 使用自定義域名提升專業度

## 🔄 持續部署

配置自動部署：
1. 每次推送到 `main` 分支自動部署
2. 設置 staging 環境進行測試
3. 使用 GitHub Actions 進行 CI/CD（可選）

## 📞 支援

如果遇到部署問題：
1. 檢查平台官方文檔
2. 查看應用日誌
3. 測試本地環境是否正常
4. 確認所有依賴項都在 `requirements.txt` 中

---

**完成部署後，您就有了一個可以分享的"Try it out"鏈接！** 🎉

