# GitHub Repository 設置腳本
# 零差錯 AI 語音點餐系統

Write-Host "========================================" -ForegroundColor Green
Write-Host "GitHub Repository 設置腳本" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# 檢查 Git 是否安裝
Write-Host "`n1. 檢查 Git 安裝狀態..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "✓ Git 已安裝: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Git 未安裝" -ForegroundColor Red
    Write-Host "請先安裝 Git: https://git-scm.com/download/win" -ForegroundColor Red
    Write-Host "或使用 winget 安裝: winget install Git.Git" -ForegroundColor Yellow
    Read-Host "按任意鍵繼續查看其他設置說明"
}

Write-Host "`n2. 項目文件檢查..." -ForegroundColor Yellow
$requiredFiles = @(
    ".gitignore",
    "vercel.json", 
    "railway.toml",
    "Dockerfile",
    "env.example",
    "DEPLOYMENT_GUIDE.md"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file" -ForegroundColor Green
    } else {
        Write-Host "✗ $file 缺失" -ForegroundColor Red
    }
}

Write-Host "`n3. 下一步操作說明..." -ForegroundColor Yellow
Write-Host @"
如果 Git 已安裝，請執行以下命令：

# 初始化 Git repository
git init

# 添加所有文件
git add .

# 創建初始提交
git commit -m "Initial commit: AI Voice Ordering System with deployment configs"

# 在 GitHub 創建新 repository
# 1. 訪問 https://github.com/new
# 2. Repository name: ai-voice-ordering-system
# 3. 設為 Public（使用免費部署服務需要）
# 4. 不要初始化 README（我們已有文件）

# 添加遠程 repository（替換 YOUR-USERNAME）
git remote add origin https://github.com/YOUR-USERNAME/ai-voice-ordering-system.git

# 推送到 GitHub
git branch -M main
git push -u origin main

"@ -ForegroundColor Cyan

Write-Host "`n4. 部署平台選擇..." -ForegroundColor Yellow
Write-Host @"
推薦部署順序：

1. 🚀 Vercel (最簡單)
   - 訪問: https://vercel.com
   - 用 GitHub 登錄並選擇您的 repository
   - 添加環境變量並部署

2. 🚂 Railway (Python 友好)
   - 訪問: https://railway.app
   - 用 GitHub 登錄並選擇您的 repository

3. 🎨 Render (免費層穩定)
   - 訪問: https://render.com
   - 用 GitHub 登錄並選擇您的 repository

"@ -ForegroundColor Cyan

Write-Host "`n5. 需要準備的 API 密鑰..." -ForegroundColor Yellow
Write-Host @"
部署前請準備：

✓ Azure Speech Services
  - 申請地址: https://azure.microsoft.com/services/cognitive-services/speech-services/
  - 需要: AZURE_SPEECH_KEY 和 AZURE_SPEECH_REGION

✓ OpenRouter API  
  - 申請地址: https://openrouter.ai/
  - 需要: OPENROUTER_API_KEY

"@ -ForegroundColor Cyan

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "準備工作已完成！請按照上述步驟操作。" -ForegroundColor Green
Write-Host "詳細部署指南請查看 DEPLOYMENT_GUIDE.md" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Read-Host "`n按任意鍵退出"

