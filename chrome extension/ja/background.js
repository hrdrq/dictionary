chrome.runtime.onMessage.addListener(function(message) {
  if (message.type === 'setBadgeText') {
    return chrome.browserAction.setBadgeText({
      text: message.value
    });
  }
});

chrome.tabs.onActivated.addListener(function(activeInfo) {
  return chrome.tabs.sendMessage(activeInfo.tabId, {
    type: 'onActivated'
  });
});

chrome.tabs.onUpdated.addListener(function(tabId, changeInfo) {
  if (changeInfo.status === 'complete') {
    return chrome.tabs.sendMessage(tabId, {
      type: 'onActivated'
    });
  }
});

chrome.browserAction.onClicked.addListener(function(tab) { 
  chrome.tabs.sendMessage(tab.id, {method: "getSelection"}, function(response){
     // alert(response.data);
     window.open('https://v3.nrfc.jp/yspider/#q='+response.data, '', 'width=1400, height=1300')
  });
});