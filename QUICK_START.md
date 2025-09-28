# 🚀 快速開始 - 5分鐘創建 "Try it out" 鏈接

## 📝 前提條件

您需要準備：
1. **GitHub 帳戶**
2. **Azure Speech Services 密鑰**：[申請地址](https://azure.microsoft.com/services/cognitive-services/speech-services/)
3. **OpenRouter API 密鑰**：[申請地址](https://openrouter.ai/)

## 🔄 步驟 1: 檢查 Git 安裝

如果您沒有 Git，請安裝：
```powershell
winget install Git.Git
```

重新啟動 PowerShell 後再繼續。

## 📤 步驟 2: 推送到 GitHub

```powershell
# 初始化 Git repository
git init

# 添加所有文件
git add .

# 創建初始提交
git commit -m "AI Voice Ordering System - Ready for deployment"

# 創建 main 分支
git branch -M main
```

## 🌐 步驟 3: 創建 GitHub Repository

1. 訪問 [github.com/new](https://github.com/new)
2. Repository name: `ai-voice-ordering-system`
3. 設為 **Public**（免費部署需要）
4. **不要**初始化 README
5. 點擊 "Create repository"

## 🔗 步驟 4: 連接並推送

複製 GitHub 給出的命令，類似：
```powershell
git remote add origin https://github.com/您的用戶名/ai-voice-ordering-system.git
git push -u origin main
```

## 🚀 步驟 5: 部署到 Vercel（推薦）

1. 訪問 [vercel.com](https://vercel.com)
2. 點擊 "Continue with GitHub"
3. 點擊 "New Project"
4. 選擇您的 `ai-voice-ordering-system` repository
5. 點擊 "Import"

### 添加環境變數：
在 "Environment Variables" 區域添加：
```
AZURE_SPEECH_KEY = 您的Azure密鑰
AZURE_SPEECH_REGION = 您的Azure區域
OPENROUTER_API_KEY = 您的OpenRouter密鑰
FLASK_ENV = production
```

6. 點擊 "Deploy"
7. 等待 2-3 分鐘部署完成

## ✅ 完成！

部署成功後，您會得到類似這樣的鏈接：
`https://ai-voice-ordering-system.vercel.app`

### 測試功能：
- 主界面：`https://您的鏈接.vercel.app`
- 管理員：`https://您的鏈接.vercel.app/admin`
- 健康檢查：`https://您的鏈接.vercel.app/health`

## 🔄 備選方案

如果 Vercel 有問題，可以嘗試：
- **Railway**: [railway.app](https://railway.app)
- **Render**: [render.com](https://render.com)

兩者都支持 GitHub 一鍵部署！

---

**🎉 恭喜！您現在有了可分享的 "Try it out" 演示鏈接！**

