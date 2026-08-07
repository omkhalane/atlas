window.addEventListener("message", (event) => {
    if (event.source !== window) return;

    if (event.data.type && (event.data.type === "ATLAS_CONNECT")) {
        console.log("Received connect request for session:", event.data.sessionId);
        chrome.runtime.sendMessage({
            type: "INIT_CONNECTION", 
            sessionId: event.data.sessionId
        }, (response) => {
            console.log("Extension connection status:", response.status);
        });
    }
});
