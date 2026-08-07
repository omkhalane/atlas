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

export class BrowserWelcomeFeature extends BrowserEditorContribution {

	private readonly _container: HTMLElement;
	private readonly _widget: IBrowserEditorWidget;
	private _content: HTMLElement;

	constructor(
		editor: BrowserEditor,
		@IContextKeyService contextKeyService: IContextKeyService,
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
		this._content.appendChild(btnContainer);
	}

	private async _startConnection() {
		this._content.innerText = ''; // clear

		try {
			const response = await fetch('http://127.0.0.1:3210/connect/start', { method: 'POST' });
			const data = await response.json();
			const connectUrl = data.url;

			const iconContainer = $('.browser-welcome-icon');
			iconContainer.appendChild(renderIcon(Codicon.globe));
			this._content.appendChild(iconContainer);

			const title = $('.browser-welcome-title');
			title.textContent = localize('browser.welcomeTitle', "Connect Browser");
			this._content.appendChild(title);

			const instruction = $('.browser-welcome-subtitle');
			instruction.textContent = localize('browserConnect.waiting', "Open your normal Chrome, Edge, or Brave browser and paste this link into the address bar:");
			this._content.appendChild(instruction);

			const urlBox = $('.browser-url-box', { style: 'user-select: all; font-family: monospace; background: var(--vscode-input-background); padding: 8px; border: 1px solid var(--vscode-input-border); margin: 16px 0; font-size: 14px;' });
			urlBox.innerText = connectUrl;
			this._content.appendChild(urlBox);

			const copyBtnContainer = $('.browser-btn-container');
			const copyBtn = this._register(new Button(copyBtnContainer, defaultButtonStyles));
			copyBtn.label = localize('browserConnect.copy', "Copy Link");
			this._register(copyBtn.onDidClick(() => navigator.clipboard.writeText(connectUrl)));
			this._content.appendChild(copyBtnContainer);

			const waitingMsg = $('.browser-waiting-msg', { style: 'margin-top: 16px; color: var(--vscode-descriptionForeground); font-style: italic;' });
			waitingMsg.innerText = "Waiting for browser connection...";
			this._content.appendChild(waitingMsg);

			const ws = new WebSocket(`ws://127.0.0.1:3211/browser/${data.sessionId}`);
			ws.onmessage = (event) => {
				const msg = JSON.parse(event.data);
				if (msg.status === 'connected' || msg.type === 'handshake') {
					waitingMsg.innerText = "✓ Browser Connected. You can now close the connection tab in your browser.";
					waitingMsg.style.color = "var(--vscode-testing-iconPassed)";
					waitingMsg.style.fontStyle = "normal";
				}
			};

		} catch (e) {
			console.error("Failed to start browser connection:", e);
			this._renderInitialState();
			const err = $('.browser-err', { style: 'color: var(--vscode-errorForeground); margin-top: 8px;' });
			err.innerText = "Error: Ensure Atlas local connector service is running.";
			this._content.appendChild(err);
		}
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
