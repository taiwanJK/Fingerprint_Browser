(function() {
  // 使用 MutationObserver 來監聽 DOM 變化，確保在頁面載入前就執行
  function injectCanvasSpoofer() {
    try {
      // 使用 Function 構造函數來創建並執行腳本，這可以繞過某些 CSP 限制
      const code = `
        // 建议由 background.js 傳入 window.__canvas_seed，否則隨機生成
        const seed = window.__canvas_seed || Math.floor(Math.random() * 1e9);
        
        // 產生 profile 專屬噪聲
        function noise(val, i) {
          const n = Math.floor(Math.sin(seed + i) * 3);
          return Math.max(0, Math.min(255, val + n));
        }
        
        // 保存原始方法
        const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        const originalToBlob = HTMLCanvasElement.prototype.toBlob;
        
        // 覆蓋 getImageData
        CanvasRenderingContext2D.prototype.getImageData = function() {
          const imageData = originalGetImageData.apply(this, arguments);
          const data = imageData.data;
          for (let i = 0; i < data.length; i += 4) {
            if (data[i+3] > 0) {
              data[i]   = noise(data[i], i);
              data[i+1] = noise(data[i+1], i+1);
              data[i+2] = noise(data[i+2], i+2);
            }
          }
          return imageData;
        };
        
        // 覆蓋 toDataURL
        HTMLCanvasElement.prototype.toDataURL = function() {
          const ctx = this.getContext('2d');
          if (ctx && this.width > 0 && this.height > 0) {
            const imageData = ctx.getImageData(0, 0, this.width, this.height);
            ctx.putImageData(imageData, 0, 0);
          }
          return originalToDataURL.apply(this, arguments);
        };
        
        // 覆蓋 toBlob
        HTMLCanvasElement.prototype.toBlob = function(callback) {
          const ctx = this.getContext('2d');
          if (ctx && this.width > 0 && this.height > 0) {
            const imageData = ctx.getImageData(0, 0, this.width, this.height);
            ctx.putImageData(imageData, 0, 0);
          }
          return originalToBlob.apply(this, arguments);
        };
        
        // WebGL readPixels 加噪聲
        function patchWebGLReadPixels(proto) {
          if (!proto) return;
          const originalReadPixels = proto.readPixels;
          proto.readPixels = function() {
            originalReadPixels.apply(this, arguments);
            const data = arguments[6];
            if (data && (data instanceof Uint8Array || data instanceof Uint8ClampedArray)) {
              for (let i = 0; i < data.length; i += 4) {
                if (data[i+3] > 0) {
                  data[i]   = noise(data[i], i);
                  data[i+1] = noise(data[i+1], i+1);
                  data[i+2] = noise(data[i+2], i+2);
                }
              }
            }
          };
        }
        
        patchWebGLReadPixels(window.WebGLRenderingContext && window.WebGLRenderingContext.prototype);
        patchWebGLReadPixels(window.WebGL2RenderingContext && window.WebGL2RenderingContext.prototype);
        
        console.log("Canvas指紋欺騙已啟用，種子:", seed);
      `;
      
      // 使用 Function 構造函數執行代碼
      new Function(code)();
      
      console.log("Canvas Spoofer 已成功注入");
    } catch (e) {
      console.error("Canvas Spoofer 注入失敗:", e);
    }
  }

  // 嘗試使用 chrome.scripting API (Manifest V3)
  if (typeof chrome !== 'undefined' && chrome.scripting) {
    try {
      chrome.scripting.executeScript({
        target: { tabId: chrome.devtools ? chrome.devtools.inspectedWindow.tabId : null },
        func: injectCanvasSpoofer
      });
    } catch (e) {
      // 如果 chrome.scripting 失敗，回退到其他方法
      injectCanvasSpoofer();
    }
  } else {
    // 直接執行注入
    injectCanvasSpoofer();
  }
  
  // 向 background script 發送消息，請求注入腳本
  chrome.runtime.sendMessage({ action: "injectScript" }, response => {
    if (response && response.success) {
      console.log("Canvas Spoofer 注入請求成功");
    } else {
      console.error("Canvas Spoofer 注入請求失敗:", response ? response.error : "未知錯誤");
      
      // 備用方案：使用 <script> 標籤加載外部腳本
      try {
        const script = document.createElement('script');
        script.src = chrome.runtime.getURL('inject.js');
        script.onload = function() { this.remove(); };
        (document.head || document.documentElement).appendChild(script);
        console.log("使用備用方案注入 Canvas Spoofer");
      } catch (e) {
        console.error("備用注入方案失敗:", e);
      }
    }
  });
  
  console.log("Canvas Spoofer content script 已執行");
})();