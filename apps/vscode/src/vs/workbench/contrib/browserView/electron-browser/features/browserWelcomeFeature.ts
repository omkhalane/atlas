/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/

import { localize } from '../../../../../nls.js';
import { $ } from '../../../../../base/browser/dom.js';
import { renderIcon } from '../../../../../base/browser/ui/iconLabel/iconLabels.js';
import { Codicon } from '../../../../../base/common/codicons.js';
import { DisposableStore } from '../../../../../base/common/lifecycle.js';
import { IContextKeyService } from '../../../../../platform/contextkey/common/contextkey.js';
import { ChatContextKeys } from '../../../chat/common/actions/chatContextKeys.js';
import { IBrowserViewModel } from '../../common/browserView.js';
import { BrowserEditorInput } from '../../common/browserEditorInput.js';
import { Button } from '../../../../../base/browser/ui/button/button.js';
import { defaultButtonStyles } from '../../../../../platform/theme/browser/defaultStyles.js';
import {
	BrowserEditor,
	BrowserEditorContribution,
	BrowserWidgetLocation,
	IBrowserEditorWidget,
} from '../browserEditor.js';
import { ITerminalService } from '../../../terminal/browser/terminal.js';
import { TerminalLocation } from '../../../../../platform/terminal/common/terminal.js';

import { IClipboardService } from '../../../../../platform/clipboard/common/clipboardService.js';
import { IRequestService, asJson } from '../../../../../platform/request/common/request.js';
import { CancellationToken } from '../../../../../base/common/cancellation.js';

export class BrowserWelcomeFeature extends BrowserEditorContribution {

	private readonly _container: HTMLElement;
	private readonly _widget: IBrowserEditorWidget;
	private _content: HTMLElement;

	constructor(
		editor: BrowserEditor,
		@IContextKeyService contextKeyService: IContextKeyService,
		@ITerminalService private readonly _terminalService: ITerminalService,
		@IClipboardService private readonly _clipboardService: IClipboardService,
		@IRequestService private readonly _requestService: IRequestService,
	) {
		super(editor);

		this._container = $('.browser-welcome-container');
		this._content = $('.browser-welcome-content');

		this._renderInitialState();

		this._container.appendChild(this._content);
		this._widget = { location: BrowserWidgetLocation.ContentArea, element: this._container, order: 50 };
	}

	private _renderInitialState() {
		this._content.innerText = ''; // clear

		const iconContainer = $('.browser-welcome-icon');
		iconContainer.appendChild(renderIcon(Codicon.globe));
		this._content.appendChild(iconContainer);

		const title = $('.browser-welcome-title');
		title.textContent = localize('browser.welcomeTitle', "Browser");
		this._content.appendChild(title);

		const subtitle = $('.browser-welcome-subtitle');
		subtitle.textContent = localize('browser.welcomeSubtitleChat', "I need browser access for this task. Connect your browser to continue.");
		this._content.appendChild(subtitle);

		const btnContainer = $('.browser-btn-container', { style: 'margin-top: 16px;' });
		const btn = this._register(new Button(btnContainer, defaultButtonStyles));
		btn.label = localize('browserConnect.btn', "Connect Browser");
		this._register(btn.onDidClick(() => this._startConnection()));
		setTimeout(() => this._startConnection(), 500);
		this._content.appendChild(btnContainer);
	}

	private async _startConnection() {
		this._content.innerText = ''; // clear

		const connectUrl = 'chrome://inspect/#remote-debugging';

		const iconContainer = $('.browser-welcome-icon');
		iconContainer.appendChild(renderIcon(Codicon.globe));
		this._content.appendChild(iconContainer);

		const title = $('.browser-welcome-title');
		title.textContent = localize('browser.welcomeTitle', "Connect Browser");
		this._content.appendChild(title);

		const instruction = $('.browser-welcome-subtitle');
		instruction.textContent = localize('browserConnect.waiting', "Open your normal Chrome, Edge, or Brave browser and paste this link into the address bar, allow remote debugging, and copy the Server IP:Port shown on the screen (e.g., 127.0.0.1:9222):");
		this._content.appendChild(instruction);

		const urlBox = $('.browser-url-box', { style: 'user-select: all; font-family: monospace; background: var(--vscode-input-background); padding: 8px; border: 1px solid var(--vscode-input-border); margin: 16px 0; font-size: 14px;' });
		urlBox.innerText = connectUrl;
		this._content.appendChild(urlBox);

		const wsInputContainer = $('.browser-ws-input-container', { style: 'margin: 16px 0; display: flex; flex-direction: column; gap: 8px;' });
		const wsInputLabel = $('label', { style: 'font-size: 13px; color: var(--vscode-descriptionForeground);' }, 'Paste the Server IP:Port here:');
		const wsInput = $<HTMLInputElement>('input', { type: 'text', style: 'padding: 8px; background: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--vscode-input-border); font-family: monospace; width: 100%; box-sizing: border-box;' });
		wsInput.placeholder = "e.g. 127.0.0.1:42407";
		wsInput.value = "42407";
		wsInputContainer.appendChild(wsInputLabel);
		wsInputContainer.appendChild(wsInput);
		this._content.appendChild(wsInputContainer);

		const copyBtnContainer = $('.browser-btn-container');
		const copyBtn = this._register(new Button(copyBtnContainer, defaultButtonStyles));
		copyBtn.label = localize('browserConnect.copy', "Copy Link");
		this._register(copyBtn.onDidClick(async () => {
			try {
				await navigator.clipboard.writeText(connectUrl);
				copyBtn.label = "Copied!";
			} catch (e) {
				try {
					await this._clipboardService.writeText(connectUrl);
					copyBtn.label = "Copied!";
				} catch (err) {
					console.error(err);
				}
			}
		}));
		this._content.appendChild(copyBtnContainer);

		const fetchBtnContainer = $('.browser-btn-container', { style: 'margin-top: 16px;' });
		const fetchBtn = this._register(new Button(fetchBtnContainer, defaultButtonStyles));
		fetchBtn.label = localize('browserConnect.fetch', "Connect to Browser");
		this._content.appendChild(fetchBtnContainer);

		const waitingMsg = $('.browser-waiting-msg', { style: 'margin-top: 16px; color: var(--vscode-descriptionForeground); font-style: italic;' });
		setTimeout(async () => {
			try {
				if (fetchBtn) {
					fetchBtn.element.click();
				}
			} catch (e) { console.error(e); }
		}, 1000);

		setTimeout(async () => {
			try {
				const fs = require('fs');
				const os = require('os');
				const p = require('path');
				const portPath = p.join(os.homedir(), '.config', 'google-chrome', 'DevToolsActivePort');
				if (fs.existsSync(portPath)) {
					const lines = fs.readFileSync(portPath, 'utf8').split('\n');
					if (lines.length > 0) {
						wsInput.value = lines[0];
						fetchBtn.click();
					}
				}
			} catch (e) { console.error(e); }
		}, 1000);

		this._content.appendChild(waitingMsg);

		const streamImg = document.createElement('img');
		streamImg.style.display = 'none';
		streamImg.style.width = '100%';
		streamImg.style.height = '100%';
		streamImg.style.objectFit = 'contain';

		let cdpMessageId = 1;

		this._register(fetchBtn.onDidClick(async () => {
			try {
				let targetPort = '9222';
				let inputVal = wsInput.value.trim();
				if (inputVal) {
					// Extract port from something like "Server running at: 127.0.0.1:42407" or just 42407
					const portMatch = inputVal.match(/:(\d+)/) || inputVal.match(/(\d+)/);
					if (portMatch) {
						targetPort = portMatch[1];
					}
				}

				waitingMsg.innerText = `Connecting to Chrome CDP on port ${targetPort}...`;
				const response = await this._requestService.request({ url: `http://127.0.0.1:3210/api/browser/cdp-version?targetPort=${targetPort}` }, CancellationToken.None);
				const versionInfo = (await asJson<any>(response)) || {};
				
				if (!versionInfo.webSocketDebuggerUrl) {
					throw new Error(`Could not find webSocketDebuggerUrl in Chrome response on port ${targetPort}. Ensure Chrome is running and remote debugging is allowed.`);
				}
				let wsUrl = versionInfo.webSocketDebuggerUrl;

				waitingMsg.innerText = "Connected to browser! Discovering targets...";
				
				const ws = new WebSocket(wsUrl);
				
				ws.onopen = () => {
					// Then we can start CDP
					ws.send(JSON.stringify({
						id: cdpMessageId++,
						method: 'Target.getTargets'
					}));
				};

				let sessionId = '';

				ws.onmessage = (event) => {
					const msg = JSON.parse(event.data);
					
					if (msg.result && msg.result.targetInfos) {
						const targets = msg.result.targetInfos;
						const page = targets.find((t: any) => t.type === 'page' && !t.url.startsWith('chrome://'));
						if (!page) {
							waitingMsg.innerText = "No attachable page target found.";
							return;
						}
						
						waitingMsg.innerText = "Attaching to page target...";
						
						ws.send(JSON.stringify({
							id: cdpMessageId++,
							method: 'Target.attachToTarget',
							params: { targetId: page.targetId, flatten: true }
						}));
					} else if (msg.result && msg.result.sessionId) {
						sessionId = msg.result.sessionId;
						waitingMsg.innerText = "Attached! Starting screencast...";
						// Must enable Page domain before starting screencast
						ws.send(JSON.stringify({
							id: cdpMessageId++,
							sessionId: sessionId,
							method: 'Page.enable'
						}));
						ws.send(JSON.stringify({
							id: cdpMessageId++,
							sessionId: sessionId,
							method: 'Page.startScreencast',
							params: { format: 'jpeg', quality: 80, everyNthFrame: 1 }
						}));
					} else if (msg.method === 'Page.screencastFrame') {
						// Sometimes Chrome sends it globally, sometimes wrapped. If wrapped, check sessionId.
						if (!msg.sessionId || msg.sessionId === sessionId) {
							if (streamImg.style.display === 'none') {
								this._content.innerText = '';
								this._content.style.padding = '0';
								this._content.style.height = '100%';
								this._content.style.display = 'flex';
								this._content.style.justifyContent = 'center';
								this._content.style.alignItems = 'center';
								this._content.style.background = 'black';
								this._content.appendChild(streamImg);
								streamImg.style.display = 'block';
							}
							// The actual data is in msg.params.data
							const frameData = msg.params ? msg.params.data : null;
							if (frameData) {
								streamImg.src = 'data:image/jpeg;base64,' + frameData;
							}
							
							// Need to send screencastFrameAck
							const sessionIdToAck = msg.params && msg.params.sessionId ? msg.params.sessionId : msg.sessionId;
							ws.send(JSON.stringify({
								id: cdpMessageId++,
								sessionId: sessionId,
								method: 'Page.screencastFrameAck',
								params: { sessionId: sessionIdToAck || 1 }
							}));
						}
					}
				};

				ws.onerror = (e) => {
					console.error("WebSocket error", e);
					waitingMsg.innerText = "WebSocket error. See console for details.";
				};
			} catch (e: any) {
				console.error(e);
				waitingMsg.innerText = "Failed to connect to CDP: " + e.message;
			}
		}));
	}

	override get widgets(): readonly IBrowserEditorWidget[] {
		return [this._widget];
	}

	override prerenderInput(input: BrowserEditorInput): void {
		this._setVisible(!input.url);
	}

	protected override onModelAttached(model: IBrowserViewModel, store: DisposableStore): void {
		this._setVisible(!model.url);
		store.add(model.onDidNavigate(event => this._setVisible(!event.url)));
	}

	override onModelDetached(): void {
		this._setVisible(true);
	}

	private _setVisible(visible: boolean): void {
		this._container.style.display = visible ? '' : 'none';
	}
}

BrowserEditor.registerContribution(BrowserWelcomeFeature);
