let ws = null;
let currentSessionId = null;

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
    };

    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.action === 'navigate') {
            chrome.tabs.update({ url: msg.url });
        } else if (msg.action === 'execute') {
            chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
                if (tabs[0]) {
                    chrome.scripting.executeScript({
                        target: {tabId: tabs[0].id},
                        func: new Function('return ' + msg.script)()
                    });
                }
            });
        }
    };

    ws.onclose = () => {
        console.log('Disconnected from Atlas runtime');
        setTimeout(connectWebSocket, 5000); // Auto-reconnect
    };
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
