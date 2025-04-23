// 监听页面导航事件，确保在每个页面都注入我们的脚本
chrome.webNavigation.onCommitted.addListener(function(details) {
  // 排除扩展页面和其他特殊页面
  if (details.url.startsWith('chrome://') || 
      details.url.startsWith('chrome-extension://') ||
      details.url.startsWith('about:')) {
    return;
  }
  
  // 使用scripting API注入脚本
  chrome.scripting.executeScript({
    target: { tabId: details.tabId },
    files: ['inject.js'],
    world: "MAIN", // 在主世界中执行，以便能够修改原生对象
    injectImmediately: true // 尽可能早地注入
  }).catch(err => console.error("注入脚本失败:", err));
});

// 生成随机噪声值，在0.0-1.0之间
function getRandomNoise() {
  return Math.random() * 0.1 - 0.05; // 生成-0.05到0.05之间的随机值
}

// 每个会话生成一个固定的噪声模式
const sessionNoise = {
  r: getRandomNoise(),
  g: getRandomNoise(),
  b: getRandomNoise(),
  a: getRandomNoise() * 0.1 // alpha通道噪声更小
};

// 将噪声模式发送给内容脚本
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'getNoise') {
    sendResponse(sessionNoise);
  }
});

// 当扩展安装或更新时执行
chrome.runtime.onInstalled.addListener(() => {
  console.log("Canvas Spoofer 扩展已安装");
});

// 监听来自 content script 的消息
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "injectScript") {
    // 使用 chrome.scripting API 注入脚本
    chrome.scripting.executeScript({
      target: { tabId: sender.tab.id },
      files: ["inject.js"]
    }).then(() => {
      console.log("Canvas Spoofer 已注入到页面");
      sendResponse({ success: true });
    }).catch(error => {
      console.error("注入失败:", error);
      sendResponse({ success: false, error: error.message });
    });
    return true; // 表示会异步响应
  }
});