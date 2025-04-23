# fingerprint_browser.py
# A Python script for Windows 10 to launch multiple Chrome windows with distinct fingerprint profiles,
# force-restoring a predefined set of tabs, using undetected-chromedriver.
# It loads a VPN Chrome extension by default, supports enhanced fingerprint parameters,
# JSON config file auto-loading, CLI range selection, and local storage of profiles and extensions.

import os
import argparse
import random
import json
import undetected_chromedriver as uc
import shutil

# ---- Configuration Directories ----
script_dir = os.path.dirname(os.path.abspath(__file__))
browser_data_dir = os.path.join(script_dir, 'browser_data')
extensions_dir = os.path.join(script_dir, 'extensions')
# Ensure directories exist
os.makedirs(browser_data_dir, exist_ok=True)
os.makedirs(extensions_dir, exist_ok=True)

# ---- Fingerprint Parameter Lists ----
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_1_0) AppleWebKit/537.36.0 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Apple Mac OS X 12_1_0) AppleWebKit/537.36.0 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_1) AppleWebKit/537.36.0 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.3"
]
# 將 LANGUAGES 和 TIMEZONES 組織成對應關係
LOCALE_CONFIGS = [
    {"lang": "en-US,en;q=0.9", "timezone": "America/New_York"},
    {"lang": "de-DE,de;q=0.9", "timezone": "Europe/Berlin"},
    {"lang": "zh-TW,zh;q=0.9", "timezone": "Asia/Taipei"},
    {"lang": "zh-CN,zh;q=0.9", "timezone": "Asia/Shanghai"},
    {"lang": "en-GB,en;q=0.9", "timezone": "Europe/London"},
    {"lang": "ja-JP,ja;q=0.9", "timezone": "Asia/Tokyo"},
    {"lang": "ko-KR,ko;q=0.9", "timezone": "Asia/Seoul"},
    {"lang": "fr-FR,fr;q=0.9", "timezone": "Europe/Paris"}
]

# 為了向後兼容，保留原始列表
LANGUAGES = [config["lang"] for config in LOCALE_CONFIGS]
TIMEZONES = [config["timezone"] for config in LOCALE_CONFIGS]

BASE_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
    "--disable-infobars",
    "--disable-dev-shm-usage"
]
WEBRTC_ARGS = [
    "--disable-features=WebRtcHideLocalIps",
    "--force-webrtc-ip-handling-policy=disable-non-proxied-udp"
]

# ---- Config Helpers ----
def generate_default_config(path: str):
    template = {
        "count": 2,
        "headless": False,
        "extensions": ["vpn_plugin", "canvas_spoofer"],  # 添加canvas_spoofer到默认扩展
        # List of startup URLs to restore as tabs
        "startup_urls": [
            "https://www.example.com",
            "https://www.google.com",
            "https://www.github.com"
        ]
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=4)
    print(f"Default config written to {path}")


def load_config(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# ---- Canvas Spoofer Extension Preparation ----
def prepare_canvas_spoofer_profiles(profile_count):
    """
    自動產生 inject.js 並複製 canvas_spoofer 目錄到 canvas_spoofer_0, canvas_spoofer_1, ...
    """
    base_ext_dir = os.path.join(extensions_dir, "canvas_spoofer")
    
    # 檢查基礎目錄是否存在
    if not os.path.exists(base_ext_dir):
        print(f"警告: 基礎目錄 {base_ext_dir} 不存在，將創建空目錄")
        os.makedirs(base_ext_dir, exist_ok=True)
    
    profiles_dir = os.path.join(base_ext_dir, "profiles")
    inject_template = """
(function() {{
  const seed = {seed};
  function noise(val, i) {{
    const n = Math.floor(Math.sin(seed + i) * 3);
    return Math.max(0, Math.min(255, val + n));
  }}
  const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
  const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
  const originalToBlob = HTMLCanvasElement.prototype.toBlob;
  CanvasRenderingContext2D.prototype.getImageData = function() {{
    const imageData = originalGetImageData.apply(this, arguments);
    const data = imageData.data;
    for (let i = 0; i < data.length; i += 4) {{
      // 只修改非透明像素 (alpha > 0)
      if (data[i+3] > 0) {{
        data[i]   = noise(data[i], i);
        data[i+1] = noise(data[i+1], i+1);
        data[i+2] = noise(data[i+2], i+2);
      }}
    }}
    return imageData;
  }};
  HTMLCanvasElement.prototype.toDataURL = function() {{
    const ctx = this.getContext('2d');
    if (ctx && this.width > 0 && this.height > 0) {{
      const imageData = ctx.getImageData(0, 0, this.width, this.height);
      ctx.putImageData(imageData, 0, 0);
    }}
    return originalToDataURL.apply(this, arguments);
  }};
  HTMLCanvasElement.prototype.toBlob = function(callback) {{
    const ctx = this.getContext('2d');
    if (ctx && this.width > 0 && this.height > 0) {{
      const imageData = ctx.getImageData(0, 0, this.width, this.height);
      ctx.putImageData(imageData, 0, 0);
    }}
    return originalToBlob.apply(this, arguments);
  }};
  function patchWebGLReadPixels(proto) {{
    if (!proto) return;
    const originalReadPixels = proto.readPixels;
    proto.readPixels = function() {{
      originalReadPixels.apply(this, arguments);
      const data = arguments[6];
      if (data && (data instanceof Uint8Array || data instanceof Uint8ClampedArray)) {{
        for (let i = 0; i < data.length; i += 4) {{
          // 只修改非透明像素
          if (data[i+3] > 0) {{
            data[i]   = noise(data[i], i);
            data[i+1] = noise(data[i+1], i+1);
            data[i+2] = noise(data[i+2], i+2);
          }}
        }}
      }}
    }};
  }}
  patchWebGLReadPixels(window.WebGLRenderingContext && window.WebGLRenderingContext.prototype);
  patchWebGLReadPixels(window.WebGL2RenderingContext && window.WebGL2RenderingContext.prototype);
  const getParameter = WebGLRenderingContext.prototype.getParameter;
  WebGLRenderingContext.prototype.getParameter = function(param) {{
    if (param === 37445) return "Intel Inc.";
    if (param === 37446) return "Intel(R) Iris(TM) Xe Graphics";
    return getParameter.apply(this, arguments);
  }};
  // console.log("Canvas指紋欺騙已啟用，種子:", seed);
}})();
"""
    for idx in range(profile_count):
        # 產生 seed 並生成 inject.js
        seed = random.randint(1, 2**31 - 1)
        js_code = inject_template.format(seed=seed)
        ext_dst = os.path.join(extensions_dir, f"canvas_spoofer_{idx}")
        # 複製原始 extension 目錄
        if os.path.exists(ext_dst):
            shutil.rmtree(ext_dst)
        shutil.copytree(base_ext_dir, ext_dst, ignore=shutil.ignore_patterns('profiles'))
        # 覆蓋 inject.js
        inject_dst = os.path.join(ext_dst, "inject.js")
        with open(inject_dst, "w", encoding="utf-8") as f:
            f.write(js_code)
        print(f"Profile {idx}: {inject_dst} 已產生，seed={seed}")

# ---- Launch Logic ----
def launch_instance(idx: int, headless: bool, extensions: list, startup_urls: list):
    options = uc.ChromeOptions()
    if headless:
        options.headless = True

    # Profile directory per instance
    profile_path = os.path.join(browser_data_dir, f"profile_{idx}")
    os.makedirs(profile_path, exist_ok=True)
    options.add_argument(f"--user-data-dir={profile_path}")

    # Fingerprint args
    options.add_argument(f"--window-size={random.randint(800,1920)},{random.randint(600,1080)}")
    options.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")
    
    # 選擇一個隨機的 locale 配置
    locale_config = random.choice(LOCALE_CONFIGS)
    options.add_argument(f"--lang={locale_config['lang']}")
    
    for arg in BASE_ARGS + WEBRTC_ARGS:
        options.add_argument(arg)

    # Load VPN plugin and other extensions
    if extensions:
        ext_paths = []
        for e in extensions:
            if e == "canvas_spoofer":
                ext_paths.append(os.path.join(extensions_dir, f"canvas_spoofer_{idx}"))
            else:
                ext_paths.append(os.path.join(extensions_dir, e))
        ext_arg = ",".join(ext_paths)
        options.add_argument(f"--disable-extensions-except={ext_arg}")
        options.add_argument(f"--load-extension={ext_arg}")

    try:
        driver = uc.Chrome(options=options)

        # 為每個 profile 產生一個隨機 seed
        canvas_seed = random.randint(1, 2**31 - 1)
        
        # 用 CDP 注入 canvas 指紋欺騙腳本（統一使用一個腳本，避免衝突）
        canvas_spoof_js = f"""
        (() => {{
            // 設定全局 seed
            const seed = {canvas_seed};
            
            // 定義噪聲函數
            function noise(val, i) {{
                const n = Math.floor(Math.sin(seed + i) * 3);
                return Math.max(0, Math.min(255, val + n));
            }}
            
            // 覆蓋 Canvas 2D 方法
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            const originalToBlob = HTMLCanvasElement.prototype.toBlob;
            
            CanvasRenderingContext2D.prototype.getImageData = function() {{
                const imageData = originalGetImageData.apply(this, arguments);
                const data = imageData.data;
                for (let i = 0; i < data.length; i += 4) {{
                    // 只修改非透明像素
                    if (data[i+3] > 0) {{
                        data[i]   = noise(data[i], i);
                        data[i+1] = noise(data[i+1], i+1);
                        data[i+2] = noise(data[i+2], i+2);
                    }}
                }}
                return imageData;
            }};
            
            HTMLCanvasElement.prototype.toDataURL = function() {{
                const ctx = this.getContext('2d');
                if (ctx && this.width > 0 && this.height > 0) {{
                    const imageData = ctx.getImageData(0, 0, this.width, this.height);
                    ctx.putImageData(imageData, 0, 0);
                }}
                return originalToDataURL.apply(this, arguments);
            }};
            
            HTMLCanvasElement.prototype.toBlob = function(callback) {{
                const ctx = this.getContext('2d');
                if (ctx && this.width > 0 && this.height > 0) {{
                    const imageData = ctx.getImageData(0, 0, this.width, this.height);
                    ctx.putImageData(imageData, 0, 0);
                }}
                return originalToBlob.apply(this, arguments);
            }};
            
            // WebGL 指紋欺騙
            function patchWebGLReadPixels(proto) {{
                if (!proto) return;
                const originalReadPixels = proto.readPixels;
                proto.readPixels = function() {{
                    originalReadPixels.apply(this, arguments);
                    const data = arguments[6];
                    if (data && (data instanceof Uint8Array || data instanceof Uint8ClampedArray)) {{
                        for (let i = 0; i < data.length; i += 4) {{
                            if (data[i+3] > 0) {{
                                data[i]   = noise(data[i], i);
                                data[i+1] = noise(data[i+1], i+1);
                                data[i+2] = noise(data[i+2], i+2);
                            }}
                        }}
                    }}
                }};
            }}
            
            patchWebGLReadPixels(window.WebGLRenderingContext && window.WebGLRenderingContext.prototype);
            patchWebGLReadPixels(window.WebGL2RenderingContext && window.WebGL2RenderingContext.prototype);
            
            // 覆蓋 WebGL getParameter
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(param) {{
                if (param === 37445) return "Intel Inc.";
                if (param === 37446) return "Intel(R) Iris(TM) Xe Graphics";
                return getParameter.apply(this, arguments);
            }};
            
            // 覆蓋 WebGL2 getParameter
            if (window.WebGL2RenderingContext) {{
                const getParameterWebGL2 = WebGL2RenderingContext.prototype.getParameter;
                WebGL2RenderingContext.prototype.getParameter = function(param) {{
                    if (param === 37445) return "Intel Inc.";
                    if (param === 37446) return "Intel(R) Iris(TM) Xe Graphics";
                    return getParameterWebGL2.apply(this, arguments);
                }};
            }}
            
            // 其他瀏覽器指紋欺騙
            Object.defineProperty(navigator, 'plugins', {{get: () => [
                {{ name: 'Chrome PDF Viewer' }},
                {{ name: 'Native Client' }},
                {{ name: 'Widevine Content Decryption Module' }}
            ]}});
            
            Object.defineProperty(navigator, 'webdriver', {{get: () => false}});
            
            console.log("Canvas指紋欺騙已啟用，種子:", seed);
        }})();
        """
        
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': canvas_spoof_js})

        # Spoof timezone & geolocation
        driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": locale_config['timezone']})
        driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
            "latitude": random.uniform(-90, 90),
            "longitude": random.uniform(-180, 180),
            "accuracy": 100
        })

        # Force restore tabs: open each URL in its own tab
        if startup_urls:
            driver.get(startup_urls[0])
            for url in startup_urls[1:]:
                driver.switch_to.new_window('tab')
                driver.get(url)
        else:
            driver.get("about:blank")

        return driver
    except Exception as e:
        print(f"Error launching Chrome instance #{idx+1}: {str(e)}")
        raise

# ---- Main ----
def main():
    parser = argparse.ArgumentParser(
        description="Launch Chrome fingerprint instances and restore predefined tabs."
    )
    parser.add_argument("--config", help="Path to JSON config (default: config.json)")
    parser.add_argument("--write-config", metavar="FILE", help="Write default config template and exit")
    parser.add_argument("-n", "--count", type=int, help="Number of instances if no config")
    parser.add_argument("--extensions", nargs="*", help="Override extensions list")
    parser.add_argument("--headless", action="store_true", help="Run headless")
    parser.add_argument("--start", type=int, help="1-based start index")
    parser.add_argument("--end", type=int, help="1-based end index")
    args = parser.parse_args()

    # Generate default config and exit
    if args.write_config:
        generate_default_config(args.write_config)
        return

    # Load config or fallback
    config_path = args.config or os.path.join(script_dir, 'config.json')
    cfg = load_config(config_path) if os.path.isfile(config_path) else {}
    count = args.count or cfg.get('count')
    headless = args.headless or cfg.get('headless', False)
    extensions = args.extensions if args.extensions is not None else cfg.get('extensions', [])
    startup_urls = cfg.get('startup_urls', [])

    # Determine instance indices
    if args.start and args.end:
        indices = list(range(args.start - 1, args.end))
    else:
        if count is None:
            parser.error("Specify --count or set 'count' in config.")
        indices = list(range(count))

    # 準備 canvas_spoofer 擴展
    prepare_canvas_spoofer_profiles(count)
    
    # 啟動實例 (移除重複的配置載入)
    drivers = []
    for i in indices:
        print(f"Launching instance #{i+1}")
        drivers.append(launch_instance(i, headless, extensions, startup_urls))

    print(f"Launched {len(drivers)} instances.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Shutting down...")
        for d in drivers:
            d.quit()

if __name__ == '__main__':
    main()
