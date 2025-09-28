# 🎤 零差錯 AI 語音點餐系統 - 項目結構

## 📁 核心文件結構

```
零差錯 AI 語音點餐系統/
├── 📄 核心配置
│   ├── .env                    # 環境變量配置
│   ├── config.py              # 應用程序配置
│   ├── requirements.txt       # Python 依賴包
│   └── run_dev.py            # 開發服務器啟動腳本
│
├── 🚀 應用程序核心
│   ├── app.py                 # Flask 應用程序主文件
│   └── README.md             # 項目說明文檔
│
├── 🗄️ 數據模型
│   └── models/
│       └── order.py          # 訂單數據模型
│
├── 🔧 業務服務
│   └── services/
│       ├── speech_service.py     # Azure 語音識別服務
│       ├── openrouter_service.py # OpenRouter AI 服務
│       └── order_service.py      # 訂單處理服務
│
├── 🛣️ API 路由
│   └── routes/
│       ├── main_routes.py        # 主要頁面路由
│       ├── speech_routes.py      # 語音處理 API
│       └── order_routes.py       # 訂單處理 API
│
├── 🎨 前端資源
│   └── static/
│       ├── 📄 HTML 頁面
│       │   ├── index.html        # 主頁面（點餐界面）
│       │   └── admin.html        # 管理員界面
│       │
│       ├── 🎨 樣式文件
│       │   └── css/
│       │       ├── style.css     # 主頁面樣式
│       │       └── admin.css     # 管理員頁面樣式
│       │
│       └── 💻 JavaScript
│           └── js/
│               ├── wav-recorder.js    # WAV 錄音器（核心）
│               ├── voice-recorder.js  # 語音錄音組件
│               ├── main.js           # 主頁面邏輯
│               ├── order-display.js  # 訂單顯示組件
│               └── admin-panel.js    # 管理員面板邏輯
│
└── 🔧 工具模塊
    └── utils/
        └── logger.py             # 日誌工具
```

## 🎯 核心功能模塊

### 1. 語音識別系統
- **WAV 錄音器** (`static/js/wav-recorder.js`)
  - 使用 Web Audio API 生成 WAV 格式
  - 16kHz, 16-bit, 單聲道（Azure 優化）
  - 實時 PCM 轉換

- **語音服務** (`services/speech_service.py`)
  - Azure Speech Services 集成
  - 音頻格式處理
  - 多語言支援（中文、粵語、英文）

### 2. AI 訂單解析
- **OpenRouter 服務** (`services/openrouter_service.py`)
  - 使用免費 Grok-4-Fast 模型
  - 智能訂單解析
  - 追加銷售建議生成

### 3. 訂單管理
- **訂單服務** (`services/order_service.py`)
  - 訂單創建和管理
  - 狀態追蹤
  - 數據持久化

### 4. 用戶界面
- **主頁面** (`static/index.html`)
  - 語音點餐界面
  - 實時訂單顯示
  - 追加銷售建議

- **管理員界面** (`static/admin.html`)
  - 訂單管理
  - 系統監控
  - 數據統計

## 🔑 關鍵配置

### 環境變量 (`.env`)
```env
# Azure Speech Services
AZURE_SPEECH_KEY=your_azure_key
AZURE_SPEECH_REGION=eastasia

# OpenRouter API
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=x-ai/grok-4-fast:free

# 應用程序設置
SITE_URL=http://localhost:5000
SITE_NAME=零差錯 AI 語音點餐系統
```

### Python 依賴 (`requirements.txt`)
- Flask: Web 框架
- azure-cognitiveservices-speech: Azure 語音服務
- openai: OpenRouter API 客戶端
- pydub: 音頻處理（備用）

## 🚀 啟動方式

```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動開發服務器
python run_dev.py

# 訪問應用程序
# 主頁面: http://localhost:5000
# 管理員: http://localhost:5000/admin
```

## 🎉 系統特色

- ✅ **真實語音識別**: Azure Speech Services
- ✅ **智能訂單解析**: OpenRouter + Grok AI
- ✅ **WAV 格式錄音**: 最佳兼容性
- ✅ **多語言支援**: 中文、粵語、英文
- ✅ **追加銷售**: AI 驅動的建議系統
- ✅ **完整管理**: 訂單追蹤和管理
- ✅ **響應式設計**: 適配各種設備

這是一個完整、專業的 AI 語音點餐系統！🎤🍵✨