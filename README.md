# Fingerprint Browser

一個用於啟動多個具有不同指紋配置的 Chrome 瀏覽器窗口的 Python 工具，可以強制恢復預定義的標籤頁，使用 undetected-chromedriver。

## 功能特點

- 啟動多個具有不同指紋的 Chrome 實例
- 自動加載 VPN 和 Canvas 指紋欺騙擴展
- 支持 JSON 配置文件
- 命令行參數支持
- 本地存儲配置文件和擴展
- 自定義啟動 URL
- 隨機化瀏覽器指紋參數（用戶代理、語言、時區等）

## 安裝要求

- Python 3.6+
- undetected-chromedriver
- Chrome 瀏覽器

## 安裝步驟

1. 克隆或下載此存儲庫
2. 安裝依賴項：
```bash
pip install -r requirements.txt
```
3. 配置 config.json 文件，根據需要修改配置參數。
4. 準備擴展目錄

## 擴展安裝

### Oxylabs 擴展安裝

Oxylabs 瀏覽器插件需要通過以下步驟安裝：

1. 使用 [CRX Extractor/Downloader](https://chromewebstore.google.com/detail/crx-extractordownloader/ajkhmmldknmfjnmeedkbkkojgobmljda?hl=zh-TW) 從 Chrome 網上應用店下載 Oxylabs 擴展的 .crx 文件
2. 解壓縮 .crx 文件（可以將擴展名改為 .zip 然後解壓）
3. 將解壓後的文件夾放入項目的 `extensions/Oxylabs` 目錄中

### Canvas Spoofer 擴展

Canvas Spoofer 擴展已包含在項目中，用於修改 Canvas 指紋以避免追踪。程序會自動為每個瀏覽器實例生成不同的 Canvas 指紋欺騙配置。

## 使用方法

### 基本用法

```bash
python fingerprint_browser.py
```

### 使用配置文件
```bash
python fingerprint_browser.py --config config.json
```

### 生成默認配置文件
```bash
python fingerprint_browser.py --write-config my_config.json
```

### 指定實例數量
```bash
python fingerprint_browser.py --count 5
```

### 啟動特定範圍的實例
```bash
python fingerprint_browser.py --start 2 --end 4
```

### 無痕模式運行
```bash
python fingerprint_browser.py -headless
```

### 指定擴展
```bash
python fingerprint_browser.py --extensions Oxylabs canvas_spoofer
```

## 目錄結構

Fingerprint_Browser/
├── fingerprint_browser.py  # 主程序
├── config.json             # 配置文件
├── README.md               # 說明文檔
├── browser_data/           # 瀏覽器配置文件存儲目錄
│   ├── profile_0/          # 第一個實例的配置文件
│   ├── profile_1/          # 第二個實例的配置文件
│   └── ...
└── extensions/             # 擴展目錄
    ├── Oxylabs/            # Oxylabs 擴展
    ├── canvas_spoofer/     # Canvas 指紋欺騙擴展基礎目錄
    ├── canvas_spoofer_0/   # 第一個實例的 Canvas 指紋欺騙擴展
    ├── canvas_spoofer_1/   # 第二個實例的 Canvas 指紋欺騙擴展
    └── ...

## 常見問題

### Q: 為什麼需要使用 undetected-chromedriver？
A: undetected-chromedriver 可以繞過大多數網站的自動化檢測，使得自動化操作更難被識別。

### Q: 如何檢查指紋欺騙是否有效？
A: 可以訪問 https://browserleaks.com/canvas 或 https://bot.sannysoft.com/ 等網站進行測試。

### Q: 如何添加其他擴展？
A: 將擴展文件夾放入 extensions 目錄，然後在配置文件中添加擴展名稱。

## 注意事項
- 確保 Chrome 瀏覽器已安裝
- 某些網站可能會檢測自動化工具，請謹慎使用
- 使用 VPN 擴展時，請確保您遵守相關服務條款
- 本工具僅供學習和研究使用，請勿用於非法用途