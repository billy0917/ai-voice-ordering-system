# 🎤 零差錯 AI 語音點餐系統

一個專為香港餐廳設計的智能語音點餐解決方案，能夠準確識別港式粵語和中英混合語音，並通過大模型理解複雜的點餐指令。

## 🚀 立即試用

### 在線演示
**[👉 點擊這裡體驗演示](https://your-demo-link.vercel.app)** *(部署後請更新此鏈接)*

### 試用說明
1. 點擊麥克風按鈕開始錄音
2. 用粵語說出您的訂單（例如：「凍檸茶，少甜，走冰」）
3. 系統會自動識別並解析您的訂單
4. 查看智能推薦並確認訂單

### 演示功能
- ✅ **語音識別**：支援粵語、國語、英語
- ✅ **智能訂單解析**：理解複雜點餐指令
- ✅ **追加銷售建議**：基於當前訂單智能推薦
- ✅ **訂單狀態追蹤**：實時更新訂單進度
- ✅ **管理員界面**：[訪問管理面板](https://your-demo-link.vercel.app/admin)

---

## 功能特點

- 🎤 **高精度語音識別**: 使用 Microsoft Azure Speech Services，專門優化港式粵語識別
- 🧠 **智能訂單解析**: 集成 OpenRouter API，準確理解複雜點餐指令和特殊要求
- 💡 **智能追加銷售**: 基於當前訂單自動生成相關推薦，提升營收
- 📱 **響應式界面**: 支援桌面和移動端，適配不同設備
- 👨‍💼 **管理員界面**: 實時監控訂單狀態，方便餐廳管理
- 🔄 **實時更新**: WebSocket 支援，訂單狀態即時同步

## 技術架構

- **前端**: HTML5, CSS3, JavaScript (Vanilla JS)
- **後端**: Python Flask
- **語音識別**: Microsoft Azure Speech Services
- **語言模型**: OpenRouter API (支援多種模型)
- **數據庫**: SQLite (開發) / PostgreSQL (生產)

## 快速開始

### 環境要求

- Python 3.9+
- 現代瀏覽器（支援 Web Audio API）
- Microsoft Azure 帳戶（用於 Speech Services）
- OpenRouter API 帳戶

### 安裝步驟

1. **克隆項目**
   ```bash
   git clone <repository-url>
   cd zero-error-voice-ordering
   ```

2. **創建虛擬環境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置環境變量**
   ```bash
   cp .env.example .env
   # 編輯 .env 文件，填入您的 API 密鑰
   ```

5. **運行應用程序**
   ```bash
   # 方式一：直接運行
   python app.py
   
   # 方式二：使用開發腳本（推薦）
   python run_dev.py
   
   # 方式三：測試完整流程
   python test_voice_flow.py
   ```

6. **訪問應用**
   - 顧客界面: http://localhost:5000
   - 管理員界面: http://localhost:5000/admin
   - 靜態文件調試: http://localhost:5000/debug/static

### 環境變量配置

在 `.env` 文件中配置以下變量：

```env
# Azure Speech Services
AZURE_SPEECH_KEY=your-azure-speech-key
AZURE_SPEECH_REGION=your-azure-region

# OpenRouter API
OPENROUTER_API_KEY=your-openrouter-api-key

# 應用配置
SECRET_KEY=your-secret-key
SITE_URL=http://localhost:5000
SITE_NAME=零差錯 AI 語音點餐系統
```

## 使用說明

### 顧客端使用

1. 打開瀏覽器訪問系統主頁
2. 點擊並按住「按住說話」按鈕
3. 用港式粵語說出您的訂單（例如：「凍檸茶，少甜，走冰」）
4. 鬆開按鈕，系統會自動識別並解析您的訂單
5. 確認訂單內容，接受或拒絕追加銷售建議
6. 點擊「確認訂單」完成點餐

### 管理員端使用

1. 訪問 `/admin` 頁面
2. 查看實時訂單統計和列表
3. 點擊相應按鈕更新訂單狀態：
   - 待確認 → 已確認
   - 已確認 → 準備中
   - 準備中 → 完成
   - 完成 → 已送達

## 項目結構

```
zero-error-voice-ordering/
├── app.py                 # 主應用程序
├── config.py             # 配置文件
├── requirements.txt      # Python 依賴
├── .env.example         # 環境變量範例
├── models/              # 數據模型
│   ├── __init__.py
│   └── order.py
├── services/            # 業務服務
│   ├── __init__.py
│   ├── speech_service.py
│   ├── openrouter_service.py
│   └── order_service.py
├── routes/              # API 路由
│   ├── __init__.py
│   ├── main_routes.py
│   ├── speech_routes.py
│   └── order_routes.py
└── static/              # 靜態文件
    ├── index.html       # 顧客界面
    ├── admin.html       # 管理員界面
    ├── css/
    │   ├── style.css
    │   └── admin.css
    └── js/
        ├── main.js
        ├── voice-recorder.js
        ├── order-display.js
        ├── admin-panel.js
        └── admin.js
```

## API 文檔

### 語音處理 API

- `POST /api/speech/transcribe` - 語音轉文字
- `GET /api/speech/test` - 測試語音服務配置

### 訂單管理 API

- `POST /api/order/parse` - 解析訂單內容
- `POST /api/order/create` - 創建新訂單
- `GET /api/order/{id}` - 獲取訂單詳情
- `PUT /api/order/{id}/status` - 更新訂單狀態
- `GET /api/order/active` - 獲取活躍訂單

## 開發指南

### 運行測試

```bash
pytest tests/
```

### 代碼格式化

```bash
black .
isort .
flake8 .
```

### 開發模式

```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

## 部署

### Docker 部署

```bash
# 構建鏡像
docker build -t voice-ordering .

# 運行容器
docker run -p 5000:5000 --env-file .env voice-ordering
```

### 生產環境部署

1. 設置環境變量 `FLASK_ENV=production`
2. 使用 Gunicorn 運行應用
3. 配置反向代理（Nginx）
4. 設置 HTTPS 證書
5. 配置數據庫（PostgreSQL）

## 故障排除

### 常見問題

1. **語音識別失敗 "cannot construct AudioConfig"**
   - 運行診斷工具: `python diagnose_audio.py`
   - 檢查 Azure Speech Services 配置
   - 確保音頻格式支援（WebM/WAV）

2. **CSS/JS 文件無法載入**
   - 確保使用正確的靜態文件路徑 (`/static/css/...`)
   - 訪問 `/debug/static` 查看靜態文件配置
   - 檢查 Flask 靜態文件夾配置

3. **麥克風權限被拒絕**
   - 確保瀏覽器允許麥克風訪問
   - 檢查系統麥克風設置
   - 嘗試使用 HTTPS（某些瀏覽器要求）

4. **API 配置問題**
   - 運行診斷工具: `python diagnose_audio.py`
   - 檢查 .env 文件中的 API 密鑰
   - 驗證 Azure Speech Services 和 OpenRouter 配置

5. **音頻處理錯誤**
   - 確保安裝了 pydub: `pip install pydub`
   - 檢查音頻文件格式和大小
   - 嘗試在安靜環境中錄音

### 日誌查看

```bash
tail -f logs/app.log
```

## 貢獻指南

1. Fork 項目
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打開 Pull Request

## 許可證

本項目採用 MIT 許可證 - 查看 [LICENSE](LICENSE) 文件了解詳情。

## 聯繫方式

如有問題或建議，請通過以下方式聯繫：

- 項目 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 郵箱: your-email@example.com

## 更新日誌

### v1.0.0 (2024-01-XX)
- 初始版本發布
- 基礎語音識別功能
- 訂單管理系統
- 管理員界面
- 追加銷售功能