/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/

import * as dom from '../../../../base/browser/dom.js';
import { Codicon } from '../../../../base/common/codicons.js';
import { localize2 } from '../../../../nls.js';
import { Registry } from '../../../../platform/registry/common/platform.js';
import { registerIcon } from '../../../../platform/theme/common/iconRegistry.js';
import { SyncDescriptor } from '../../../../platform/instantiation/common/descriptors.js';
import { IWorkbenchContribution, registerWorkbenchContribution2, WorkbenchPhase } from '../../../../workbench/common/contributions.js';
import { IViewContainersRegistry, IViewsRegistry, ViewContainerLocation, Extensions as ViewContainerExtensions, WindowEnablement } from '../../../../workbench/common/views.js';
import { ViewPaneContainer } from '../../../../workbench/browser/parts/views/viewPaneContainer.js';
import { IViewPaneOptions, ViewPane } from '../../../../workbench/browser/parts/views/viewPane.js';
import { IKeybindingService } from '../../../../platform/keybinding/common/keybinding.js';
import { IContextMenuService } from '../../../../platform/contextview/browser/contextView.js';
import { IConfigurationService } from '../../../../platform/configuration/common/configuration.js';
import { IContextKeyService } from '../../../../platform/contextkey/common/contextkey.js';
import { IViewDescriptorService } from '../../../../workbench/common/views.js';
import { IInstantiationService } from '../../../../platform/instantiation/common/instantiation.js';
import { IOpenerService } from '../../../../platform/opener/common/opener.js';
import { IThemeService } from '../../../../platform/theme/common/themeService.js';
import { IHoverService } from '../../../../platform/hover/browser/hover.js';

export const SESSIONS_LIVE_BROWSER_CONTAINER_ID = 'workbench.sessions.auxiliaryBar.liveBrowserContainer';
export const SESSIONS_LIVE_BROWSER_VIEW_ID = 'sessions.liveBrowser.recordingView';

const liveBrowserIcon = registerIcon('sessions-live-browser-icon', Codicon.deviceCameraVideo, localize2('sessionsLiveBrowserIcon', 'View icon of live browser recording.').value);

const viewContainerRegistry = Registry.as<IViewContainersRegistry>(ViewContainerExtensions.ViewContainersRegistry);

// Register container right near Files toggle (Order: 12) on the right side of Atlas Agent App
const liveBrowserViewContainer = viewContainerRegistry.registerViewContainer({
	id: SESSIONS_LIVE_BROWSER_CONTAINER_ID,
	title: localize2('liveBrowserRecording', "Browser Recording Live"),
	icon: liveBrowserIcon,
	order: 12,
	ctorDescriptor: new SyncDescriptor(ViewPaneContainer, [SESSIONS_LIVE_BROWSER_CONTAINER_ID, { mergeViewWithContainerWhenSingleView: true }]),
	storageId: SESSIONS_LIVE_BROWSER_CONTAINER_ID,
	windowEnablement: WindowEnablement.Sessions,
}, ViewContainerLocation.AuxiliaryBar, { isDefault: false });

export class SessionsLiveBrowserRecordingView extends ViewPane {
	private _imgElement?: HTMLImageElement;
	private _statusText?: HTMLElement;
	private _urlText?: HTMLElement;
	private _refreshInterval?: any;
	private _isLive: boolean = true;

	constructor(
		options: IViewPaneOptions,
		@IKeybindingService keybindingService: IKeybindingService,
		@IContextMenuService contextMenuService: IContextMenuService,
		@IConfigurationService configurationService: IConfigurationService,
		@IContextKeyService contextKeyService: IContextKeyService,
		@IViewDescriptorService viewDescriptorService: IViewDescriptorService,
		@IInstantiationService instantiationService: IInstantiationService,
		@IOpenerService openerService: IOpenerService,
		@IThemeService themeService: IThemeService,
		@IHoverService hoverService: IHoverService,
	) {
		super(options, keybindingService, contextMenuService, configurationService, contextKeyService, viewDescriptorService, instantiationService, openerService, themeService, hoverService);
	}

	protected override renderBody(container: HTMLElement): void {
		super.renderBody(container);
		container.style.display = 'flex';
		container.style.flexDirection = 'column';
		container.style.height = '100%';
		container.style.background = 'var(--vscode-sideBar-background, #181818)';
		container.style.color = 'var(--vscode-foreground, #cccccc)';
		container.style.fontFamily = 'system-ui, -apple-system, sans-serif';

		// Header / Status Bar
		const header = dom.append(container, dom.$('.live-browser-header'));
		header.style.display = 'flex';
		header.style.alignItems = 'center';
		header.style.justifyContent = 'space-between';
		header.style.padding = '8px 12px';
		header.style.borderBottom = '1px solid var(--vscode-widget-border, #333)';
		header.style.background = 'rgba(0, 0, 0, 0.2)';

		const badgeContainer = dom.append(header, dom.$('.badge-container'));
		badgeContainer.style.display = 'flex';
		badgeContainer.style.alignItems = 'center';
		badgeContainer.style.gap = '6px';

		const dot = dom.append(badgeContainer, dom.$('.live-dot'));
		dot.style.width = '8px';
		dot.style.height = '8px';
		dot.style.borderRadius = '50%';
		dot.style.background = '#e53935';
		dot.style.boxShadow = '0 0 6px #e53935';

		const badgeText = dom.append(badgeContainer, dom.$('span'));
		badgeText.innerText = 'LIVE BROWSER STREAM';
		badgeText.style.fontSize = '11px';
		badgeText.style.fontWeight = 'bold';
		badgeText.style.letterSpacing = '0.5px';
		badgeText.style.color = '#ff5252';

		const controls = dom.append(header, dom.$('.live-controls'));
		controls.style.display = 'flex';
		controls.style.gap = '8px';

		const refreshBtn = dom.append(controls, dom.$('button'));
		refreshBtn.innerText = 'Refresh';
		refreshBtn.style.padding = '2px 8px';
		refreshBtn.style.fontSize = '11px';
		refreshBtn.style.background = 'var(--vscode-button-background, #007acc)';
		refreshBtn.style.color = '#fff';
		refreshBtn.style.border = 'none';
		refreshBtn.style.borderRadius = '3px';
		refreshBtn.style.cursor = 'pointer';
		refreshBtn.onclick = () => this._updateFrame();

		// URL Bar
		const urlBar = dom.append(container, dom.$('.live-browser-url'));
		urlBar.style.padding = '6px 12px';
		urlBar.style.fontSize = '12px';
		urlBar.style.background = 'var(--vscode-input-background, #222)';
		urlBar.style.borderBottom = '1px solid var(--vscode-widget-border, #333)';
		urlBar.style.whiteSpace = 'nowrap';
		urlBar.style.overflow = 'hidden';
		urlBar.style.textOverflow = 'ellipsis';
		this._urlText = urlBar;
		this._urlText.innerText = 'Atlas Browser Harness: Active CDP Session';

		// Video / Frame Stream Viewer
		const streamView = dom.append(container, dom.$('.live-browser-view'));
		streamView.style.flex = '1';
		streamView.style.display = 'flex';
		streamView.style.alignItems = 'center';
		streamView.style.justifyContent = 'center';
		streamView.style.overflow = 'hidden';
		streamView.style.position = 'relative';
		streamView.style.background = '#0d0d0d';

		this._imgElement = dom.append(streamView, dom.$('img'));
		this._imgElement.style.maxWidth = '100%';
		this._imgElement.style.maxHeight = '100%';
		this._imgElement.style.objectFit = 'contain';
		this._imgElement.style.display = 'block';

		// Status text footer
		const footer = dom.append(container, dom.$('.live-browser-footer'));
		footer.style.padding = '6px 12px';
		footer.style.fontSize = '11px';
		footer.style.color = 'var(--vscode-descriptionForeground, #888)';
		footer.style.borderTop = '1px solid var(--vscode-widget-border, #333)';
		this._statusText = footer;
		this._statusText.innerText = 'Engine: @packages/browser/atlas-browser (CDP Harness)';

		this._startStream();
	}

	private _startStream(): void {
		this._updateFrame();
		if (!this._refreshInterval) {
			this._refreshInterval = setInterval(() => {
				if (this._isLive) {
					this._updateFrame();
				}
			}, 1000);
		}
	}

	private _updateFrame(): void {
		if (this._imgElement) {
			const cacheBust = new Date().getTime();
			this._imgElement.src = `http://127.0.0.1:8000/api/browser_screenshot?t=${cacheBust}`;
			this._imgElement.onerror = () => {
				if (this._imgElement) {
					this._imgElement.style.display = 'none';
				}
				if (this._statusText) {
					this._statusText.innerText = 'Atlas Browser Harness Idle (Waiting for active task...)';
				}
			};
			this._imgElement.onload = () => {
				if (this._imgElement) {
					this._imgElement.style.display = 'block';
				}
				if (this._statusText) {
					this._statusText.innerText = 'Streaming Atlas Browser recording live';
				}
			};
		}
	}

	override dispose(): void {
		if (this._refreshInterval) {
			clearInterval(this._refreshInterval);
		}
		super.dispose();
	}
}

class RegisterLiveBrowserViewContribution implements IWorkbenchContribution {
	static readonly ID = 'sessions.registerLiveBrowserRecordingView';

	constructor() {
		const viewsRegistry = Registry.as<IViewsRegistry>(ViewContainerExtensions.ViewsRegistry);
		viewsRegistry.registerViews([{
			id: SESSIONS_LIVE_BROWSER_VIEW_ID,
			name: localize2('liveBrowserRecording', "Browser Recording Live"),
			containerIcon: liveBrowserIcon,
			ctorDescriptor: new SyncDescriptor(SessionsLiveBrowserRecordingView),
			canToggleVisibility: false,
			canMoveView: true,
			windowEnablement: WindowEnablement.Sessions,
		}], liveBrowserViewContainer);
	}
}

registerWorkbenchContribution2(RegisterLiveBrowserViewContribution.ID, RegisterLiveBrowserViewContribution, WorkbenchPhase.AfterRestored);
