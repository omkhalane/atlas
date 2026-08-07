import { $ } from '../../../../base/browser/dom.js';
import { Disposable } from '../../../../base/common/lifecycle.js';
import { IObservable, observableValue } from '../../../../base/common/observable.js';
import { localize } from '../../../../nls.js';
import { Button } from '../../../../base/browser/ui/button/button.js';
import { defaultButtonStyles } from '../../../../platform/theme/browser/defaultStyles.js';

export class BrowserConnectUX extends Disposable {
    readonly element: HTMLElement;
    private readonly _status = observableValue<'disconnected' | 'waiting' | 'connected'>('browserStatus', 'disconnected');
    private readonly _browserState = observableValue<{url: string, title: string, status: string}>('browserState', {url: '', title: '', status: ''});
    private _connectUrl: string = '';
    private _contentContainer: HTMLElement;
    private _ws: WebSocket | null = null;

    constructor() {
        super();
        this.element = $('.browser-connect-ux', { style: 'padding: 10px; border: 1px solid var(--vscode-widget-border); border-radius: 4px; margin-top: 10px;' });
        
        const header = $('.browser-header', { style: 'font-weight: bold; margin-bottom: 8px;' });
        header.innerText = localize('browserConnect.title', "Browser");
        this.element.appendChild(header);

        this._contentContainer = $('.browser-content');
        this.element.appendChild(this._contentContainer);

        this._render();
        this._register(this._status.onDidChange(() => this._render()));
        this._register(this._browserState.onDidChange(() => this._render()));
    }

    private _render(): void {
        this._contentContainer.innerText = ''; // clear

        const status = this._status.get();
        if (status === 'disconnected') {
            const msg = $('.browser-msg', { style: 'margin-bottom: 8px;' });
            msg.innerText = localize('browserConnect.msg', "I need browser access for this task.");
            
            const btnContainer = $('.browser-btn-container');
            const btn = this._register(new Button(btnContainer, defaultButtonStyles));
            btn.label = localize('browserConnect.btn', "Connect Browser");
            this._register(btn.onDidClick(() => this.startConnection()));

            this._contentContainer.appendChild(msg);
            this._contentContainer.appendChild(btnContainer);
        } else if (status === 'waiting') {
            const msg = $('.browser-msg', { style: 'margin-bottom: 8px;' });
            msg.innerText = localize('browserConnect.waiting', "Open your normal browser and paste this link into the address bar:");
            
            const urlBox = $('.browser-url-box', { style: 'user-select: all; font-family: monospace; background: var(--vscode-input-background); padding: 4px; border: 1px solid var(--vscode-input-border); margin-bottom: 8px;' });
            urlBox.innerText = this._connectUrl;

            const copyBtnContainer = $('.browser-btn-container');
            const copyBtn = this._register(new Button(copyBtnContainer, defaultButtonStyles));
            copyBtn.label = localize('browserConnect.copy', "Copy Link");
            this._register(copyBtn.onDidClick(() => navigator.clipboard.writeText(this._connectUrl)));

            const waitingMsg = $('.browser-waiting-msg', { style: 'margin-top: 8px; color: var(--vscode-descriptionForeground);' });
            waitingMsg.innerText = "Waiting for browser...";

            this._contentContainer.appendChild(msg);
            this._contentContainer.appendChild(urlBox);
            this._contentContainer.appendChild(copyBtnContainer);
            this._contentContainer.appendChild(waitingMsg);
        } else if (status === 'connected') {
            const state = this._browserState.get();
            const header = this.element.querySelector('.browser-header') as HTMLElement;
            if (header) {
                header.innerText = localize('browserConnect.titleConnected', "Browser ● Connected");
            }
            const infoContainer = $('.browser-info-container', { style: 'display: flex; flex-direction: column; gap: 4px;' });
            
            const urlLine = $('.browser-url', { style: 'font-size: 0.9em; opacity: 0.8;' });
            urlLine.innerText = state.url || "about:blank";
            
            const titleLine = $('.browser-title', { style: 'font-weight: 500;' });
            titleLine.innerText = state.title || "New Tab";

            infoContainer.appendChild(titleLine);
            infoContainer.appendChild(urlLine);
            
            this._contentContainer.appendChild(infoContainer);
        }
    }

    public async startConnection(): Promise<void> {
        try {
            const response = await fetch('http://127.0.0.1:3210/connect/start', { method: 'POST' });
            const data = await response.json();
            this._connectUrl = data.url;
            this._status.set('waiting', undefined);

            this._ws = new WebSocket(`ws://127.0.0.1:3211/browser/${data.sessionId}`);
            this._ws.onmessage = (event) => {
                const msg = JSON.parse(event.data);
                if (msg.status === 'connected' || msg.type === 'handshake') {
                    this._status.set('connected', undefined);
                } else if (msg.type === 'state_update') {
                    this._status.set('connected', undefined);
                    this._browserState.set({
                        url: msg.url,
                        title: msg.title,
                        status: msg.status
                    }, undefined);
                }
            };
        } catch (e) {
            console.error("Failed to start browser connection:", e);
            const err = $('.browser-err', { style: 'color: var(--vscode-errorForeground); margin-top: 8px;' });
            err.innerText = "Error: Ensure Atlas connector is running.";
            this._contentContainer.appendChild(err);
        }
    }
}
