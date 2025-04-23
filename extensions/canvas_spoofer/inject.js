(function() {
  // 建议由 background.js 传入 window.__canvas_seed，否则随机生成
  const seed = window.__canvas_seed || Math.floor(Math.random() * 1e9);
  
  // 产生 profile 专属噪声 - 使用更穩定的雜湊算法
  function noise(val, i) {
    // 使用種子和位置產生一個穩定的雜湊值
    const hashValue = (seed * 9301 + i * 49297) % 233280;
    // 將雜湊值轉換為 -1, 0, 1 的噪聲
    const n = Math.floor((hashValue / 233280) * 3) - 1;
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
  
  // WebGL readPixels 加噪声
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
  
  // 覆蓋 WebGL getParameter
  const getParameter = WebGLRenderingContext.prototype.getParameter;
  WebGLRenderingContext.prototype.getParameter = function(param) {
    if (param === 37445) return "Intel Inc.";
    if (param === 37446) return "Intel(R) Iris(TM) Xe Graphics";
    return getParameter.apply(this, arguments);
  };
  
  // 覆蓋 WebGL2 getParameter
  if (window.WebGL2RenderingContext) {
    const getParameterWebGL2 = WebGL2RenderingContext.prototype.getParameter;
    WebGL2RenderingContext.prototype.getParameter = function(param) {
      if (param === 37445) return "Intel Inc.";
      if (param === 37446) return "Intel(R) Iris(TM) Xe Graphics";
      return getParameterWebGL2.apply(this, arguments);
    };
  }
  
  // 添加更多指紋差異化特性
  // 修改 Font 列表
  const fontList = [
    'Arial', 'Arial Black', 'Arial Narrow', 'Calibri', 'Cambria', 'Cambria Math', 'Comic Sans MS',
    'Courier', 'Courier New', 'Georgia', 'Helvetica', 'Impact', 'Lucida Console', 'Lucida Sans Unicode',
    'Microsoft Sans Serif', 'Palatino Linotype', 'Tahoma', 'Times', 'Times New Roman', 'Trebuchet MS', 'Verdana'
  ];
  
  // 根據種子選擇要隱藏的字體
  const hiddenFonts = new Set();
  const numHiddenFonts = seed % 5; // 隱藏 0-4 個字體
  for (let i = 0; i < numHiddenFonts; i++) {
    const fontIndex = (seed * (i + 1)) % fontList.length;
    hiddenFonts.add(fontList[fontIndex]);
  }
  
  // 覆蓋 document.fonts.check 方法
  if (document.fonts && document.fonts.check) {
    const originalCheck = document.fonts.check;
    document.fonts.check = function(font, text) {
      const fontFamily = font.split(' ').pop().replace(/['"]/g, '');
      if (hiddenFonts.has(fontFamily)) {
        return false;
      }
      return originalCheck.apply(this, arguments);
    };
  }
  
  // 修改 AudioContext 指紋
  if (window.AudioContext || window.webkitAudioContext) {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    const originalGetChannelData = AudioContextClass.prototype.createAnalyser;
    
    AudioContextClass.prototype.createAnalyser = function() {
      const analyser = originalGetChannelData.apply(this, arguments);
      const originalGetFloatFrequencyData = analyser.getFloatFrequencyData;
      
      analyser.getFloatFrequencyData = function(array) {
        originalGetFloatFrequencyData.apply(this, arguments);
        // 添加微小噪聲到音頻數據
        for (let i = 0; i < array.length; i++) {
          array[i] += (seed % 3) - 1;
        }
        return array;
      };
      
      return analyser;
    };
  }
  
  // 修改 WebRTC 指紋
  if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
    const originalEnumerateDevices = navigator.mediaDevices.enumerateDevices;
    navigator.mediaDevices.enumerateDevices = async function() {
      const devices = await originalEnumerateDevices.apply(this, arguments);
      
      // 根據種子修改設備數量和 ID
      const modifiedDevices = [];
      const numDevices = Math.max(1, devices.length - (seed % 2));
      
      for (let i = 0; i < numDevices; i++) {
        if (i < devices.length) {
          const device = devices[i];
          const modifiedDevice = {
            deviceId: device.deviceId,
            groupId: device.groupId,
            kind: device.kind,
            label: device.label
          };
          
          // 修改 deviceId 和 groupId 的最後幾個字符
          if (modifiedDevice.deviceId) {
            const idSuffix = (seed + i) % 1000;
            modifiedDevice.deviceId = modifiedDevice.deviceId.replace(/.$/, idSuffix);
          }
          
          modifiedDevices.push(modifiedDevice);
        }
      }
      
      return modifiedDevices;
    };
  }
  
  console.log("Canvas指紋欺騙已啟用，種子:", seed, "- 增強版多瀏覽器差異化");
})();