let ws = null;
let currentSessionId = null;
let streamInterval = null;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'INIT_CONNECTION') {
        currentSessionId = request.sessionId;
        connectWebSocket();
        sendResponse({status: 'connecting'});
    }
});

function connectWebSocket() {
    if (ws) {
        ws.close();
    }
    ws = new WebSocket(`ws://127.0.0.1:3211/browser/${currentSessionId}`);
    
    ws.onopen = () => {
        console.log('Connected to Atlas runtime');
        ws.send(JSON.stringify({ type: 'handshake', status: 'connected' }));
        broadcastState();
        startStreaming();
    };

    ws.onmessage = (event) => {
        try {
            const msg = JSON.parse(event.data);
            const reqId = msg.requestId;
            
            if (msg.action === 'navigate') {
                chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
                    if (tabs[0]) {
                        chrome.tabs.update(tabs[0].id, { url: msg.payload.url }, () => {
                            if (reqId) ws.send(JSON.stringify({ type: 'response', requestId: reqId, data: 'ok' }));
                        });
                    }
                });
            } else if (msg.action === 'execute') {
                chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
                    if (tabs[0]) {
                        chrome.scripting.executeScript({
                            target: {tabId: tabs[0].id},
                            func: new Function('return ' + msg.payload.script)
                        }, (results) => {
                            let resData = null;
                            if (results && results[0]) resData = results[0].result;
                            if (reqId) ws.send(JSON.stringify({ type: 'response', requestId: reqId, data: resData }));
                        });
                    }
                });
            } else if (msg.action === 'read') {
                chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
                    if (tabs[0]) {
                        chrome.scripting.executeScript({
                            target: {tabId: tabs[0].id},
                            func: () => document.body.innerText
                        }, (results) => {
                            let text = "";
                            if (results && results[0]) text = results[0].result;
                            if (reqId) ws.send(JSON.stringify({ type: 'response', requestId: reqId, data: text }));
                        });
                    }
                });
            }
        } catch (e) {
            console.error("Error handling message:", e);
        }
    };

    ws.onclose = () => {
        console.log('Disconnected from Atlas runtime');
        stopStreaming();
        setTimeout(connectWebSocket, 5000); // Auto-reconnect
    };
}

function startStreaming() {
    if (streamInterval) clearInterval(streamInterval);
    // Send a frame every 500ms (2 FPS) to avoid overloading WebSocket while testing
    streamInterval = setInterval(() => {
        if (!ws || ws.readyState !== WebSocket.OPEN) return;
        chrome.tabs.captureVisibleTab(null, {format: 'jpeg', quality: 50}, (dataUrl) => {
            if (chrome.runtime.lastError) {
                // Ignore errors like "no active tab"
                return;
            }
            if (dataUrl) {
                ws.send(JSON.stringify({
                    type: 'screencast',
                    data: dataUrl
                }));
            }
        });
    }, 500);
}

function stopStreaming() {
    if (streamInterval) {
        clearInterval(streamInterval);
        streamInterval = null;
    }
}

function broadcastState() {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        if (tabs[0]) {
            ws.send(JSON.stringify({
                type: 'state_update',
                url: tabs[0].url,
                title: tabs[0].title,
                status: tabs[0].status
            }));
        }
    });
}

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (tab.active) broadcastState();
});

chrome.tabs.onActivated.addListener((activeInfo) => {
    broadcastState();
});
