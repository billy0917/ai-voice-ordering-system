# ✅ 部署檢查清單

## 📋 GitHub 設置
- [ ] 安裝 Git（如果尚未安裝）: `winget install Git.Git`
- [ ] 初始化 repository: `git init`
- [ ] 添加文件: `git add .`
- [ ] 提交: `git commit -m "Initial commit"`
- [ ] 在 GitHub 創建新 repository（設為 Public）
- [ ] 連接遠程: `git remote add origin https://github.com/您的用戶名/項目名.git`
- [ ] 推送: `git push -u origin main`

## 🔑 API 密鑰準備
- [ ] Azure Speech Services 密鑰和區域
- [ ] OpenRouter API 密鑰

## 🚀 選擇部署平台（任選一個）

### 選項 1: Vercel（推薦）
- [ ] 訪問 [vercel.com](https://vercel.com)
- [ ] GitHub 登錄
- [ ] 選擇 repository
- [ ] 添加環境變量
- [ ] 點擊部署

### 選項 2: Railway
- [ ] 訪問 [railway.app](https://railway.app)
- [ ] GitHub 登錄
- [ ] 選擇 repository
- [ ] 添加環境變量

### 選項 3: Render
- [ ] 訪問 [render.com](https://render.com)
- [ ] GitHub 登錄
- [ ] 選擇 repository
- [ ] 添加環境變量

## 🧪 部署後測試
- [ ] 健康檢查: `/health`
- [ ] 靜態文件: `/debug/static`
- [ ] 顧客界面: `/`
- [ ] 管理員界面: `/admin`
- [ ] 麥克風功能測試

## 📝 最後步驟
- [ ] 更新 README.md 中的演示鏈接
- [ ] 測試所有功能
- [ ] 分享您的 "Try it out" 鏈接！

---

**快速啟動**: 運行 `.\setup-github.ps1` 獲取詳細指導

