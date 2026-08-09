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
	private _canvas?: HTMLCanvasElement;
	private _ctx?: CanvasRenderingContext2D | null;
	private _statusText?: HTMLElement;
	private _urlText?: HTMLElement;
	private _ws?: WebSocket;

	// Viewport state
	private _scale: number = 1.0;
	private _offsetX: number = 0;
	private _offsetY: number = 0;
	private _isDragging: boolean = false;
	private _dragStartX: number = 0;
	private _dragStartY: number = 0;
	private _baseOffsetX: number = 0;
	private _baseOffsetY: number = 0;

	private _browserWidth: number = 1280;
	private _browserHeight: number = 720;
	private _lastImage?: HTMLImageElement;

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
		badgeText.innerText = 'LIVE CDP MIRROR';
		badgeText.style.fontSize = '11px';
		badgeText.style.fontWeight = 'bold';
		badgeText.style.letterSpacing = '0.5px';
		badgeText.style.color = '#ff5252';

		const controls = dom.append(header, dom.$('.live-controls'));
		controls.style.display = 'flex';
		controls.style.gap = '8px';

		const refreshBtn = dom.append(controls, dom.$('button'));
		refreshBtn.innerText = 'Connect';
		refreshBtn.style.padding = '2px 8px';
		refreshBtn.style.fontSize = '11px';
		refreshBtn.style.background = 'var(--vscode-button-background, #007acc)';
		refreshBtn.style.color = '#fff';
		refreshBtn.style.border = 'none';
		refreshBtn.style.borderRadius = '3px';
		refreshBtn.style.cursor = 'pointer';
		refreshBtn.onclick = () => this._startStream();

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
		this._urlText.innerText = 'Atlas Browser: CDP Interactive Canvas';

		// Video / Frame Stream Viewer
		const streamView = dom.append(container, dom.$('.live-browser-view'));
		streamView.style.flex = '1';
		streamView.style.display = 'flex';
		streamView.style.alignItems = 'center';
		streamView.style.justifyContent = 'center';
		streamView.style.overflow = 'hidden';
		streamView.style.position = 'relative';
		streamView.style.background = '#0d0d0d';

		this._canvas = dom.append(streamView, dom.$('canvas'));
		this._canvas.style.display = 'block';
		this._canvas.style.cursor = 'default';
		this._ctx = this._canvas.getContext('2d');

		// Resize Observer for Canvas
		const resizeObserver = new ResizeObserver(() => this._resizeCanvas(streamView));
		resizeObserver.observe(streamView);

		// Status text footer
		const footer = dom.append(container, dom.$('.live-browser-footer'));
		footer.style.padding = '6px 12px';
		footer.style.fontSize = '11px';
		footer.style.color = 'var(--vscode-descriptionForeground, #888)';
		footer.style.borderTop = '1px solid var(--vscode-widget-border, #333)';
		this._statusText = footer;
		this._statusText.innerText = 'Engine: CDP WebSocket | Disconnected';

		this._bindInteractionEvents();
		this._startStream();
	}

	private _resizeCanvas(container: HTMLElement) {
		if (!this._canvas) return;
		this._canvas.width = container.clientWidth;
		this._canvas.height = container.clientHeight;
		this._redraw();
	}

	private _bindInteractionEvents() {
		if (!this._canvas) return;

		this._canvas.addEventListener('wheel', (e) => {
			e.preventDefault();
			if (e.ctrlKey || e.metaKey) {
				// Zoom
				const zoomSpeed = 0.005;
				const delta = -e.deltaY * zoomSpeed;
				const oldScale = this._scale;
				this._scale = Math.min(Math.max(0.1, this._scale + delta), 10);
				
				// Center zoom on mouse pointer
				const rect = this._canvas!.getBoundingClientRect();
				const mouseX = e.clientX - rect.left;
				const mouseY = e.clientY - rect.top;
				
				this._offsetX = mouseX - (mouseX - this._offsetX) * (this._scale / oldScale);
				this._offsetY = mouseY - (mouseY - this._offsetY) * (this._scale / oldScale);
				
				this._redraw();
			} else {
				// Normal Scroll -> CDP
				if (this._ws && this._ws.readyState === WebSocket.OPEN) {
					const { x, y } = this._mapToBrowserCoordinates(e.clientX, e.clientY);
					this._ws.send(JSON.stringify({
						id: Date.now(),
						method: 'Input.dispatchMouseEvent',
						params: {
							type: 'mouseWheel',
							x,
							y,
							deltaX: e.deltaX,
							deltaY: e.deltaY
						}
					}));
				}
			}
		});

		this._canvas.addEventListener('mousedown', (e) => {
			if (e.button === 0 && e.shiftKey) { // Or if we want drag-to-pan to be right click/middle click
				// Panning using shift+drag for now, or if scale > 1
				this._isDragging = true;
				this._dragStartX = e.clientX;
				this._dragStartY = e.clientY;
				this._baseOffsetX = this._offsetX;
				this._baseOffsetY = this._offsetY;
			} else {
				// CDP click
				if (this._ws && this._ws.readyState === WebSocket.OPEN) {
					const { x, y } = this._mapToBrowserCoordinates(e.clientX, e.clientY);
					this._ws.send(JSON.stringify({
						id: Date.now(),
						method: 'Input.dispatchMouseEvent',
						params: {
							type: 'mousePressed',
							x,
							y,
							button: 'left',
							clickCount: 1
						}
					}));
				}
			}
		});

		this._canvas.addEventListener('mousemove', (e) => {
			if (this._isDragging) {
				this._offsetX = this._baseOffsetX + (e.clientX - this._dragStartX);
				this._offsetY = this._baseOffsetY + (e.clientY - this._dragStartY);
				this._redraw();
			} else {
				// CDP mouse move
				if (this._ws && this._ws.readyState === WebSocket.OPEN) {
					const { x, y } = this._mapToBrowserCoordinates(e.clientX, e.clientY);
					this._ws.send(JSON.stringify({
						id: Date.now(),
						method: 'Input.dispatchMouseEvent',
						params: {
							type: 'mouseMoved',
							x,
							y
						}
					}));
				}
			}
		});

		this._canvas.addEventListener('mouseup', (e) => {
			if (this._isDragging) {
				this._isDragging = false;
			} else {
				// CDP mouse up
				if (this._ws && this._ws.readyState === WebSocket.OPEN) {
					const { x, y } = this._mapToBrowserCoordinates(e.clientX, e.clientY);
					this._ws.send(JSON.stringify({
						id: Date.now(),
						method: 'Input.dispatchMouseEvent',
						params: {
							type: 'mouseReleased',
							x,
							y,
							button: 'left',
							clickCount: 1
						}
					}));
				}
			}
		});

		this._canvas.addEventListener('dblclick', (e) => {
			e.preventDefault();
			this._scale = 1.0;
			this._offsetX = 0;
			this._offsetY = 0;
			this._redraw();
		});
	}

	private _mapToBrowserCoordinates(clientX: number, clientY: number): { x: number, y: number } {
		if (!this._canvas) return { x: 0, y: 0 };
		const rect = this._canvas.getBoundingClientRect();
		const canvasX = clientX - rect.left;
		const canvasY = clientY - rect.top;

		// Inverse transform
		const imgX = (canvasX - this._offsetX) / this._scale;
		const imgY = (canvasY - this._offsetY) / this._scale;

		// The image is drawn to fit the canvas if scale=1 and offsets=0, but here we actually map imgX and imgY
		// Need to see how we draw it in _redraw.
		// We draw the image at (0, 0) with width = browserWidth, height = browserHeight (scaled down to fit canvas).
		
		// Let's assume we maintain aspect ratio inside _redraw.
		const scaleFit = Math.min(
			this._canvas.width / this._browserWidth,
			this._canvas.height / this._browserHeight
		);

		const dx = (this._canvas.width - this._browserWidth * scaleFit) / 2;
		const dy = (this._canvas.height - this._browserHeight * scaleFit) / 2;

		const finalX = (imgX - dx) / scaleFit;
		const finalY = (imgY - dy) / scaleFit;

		return {
			x: Math.round(Math.max(0, Math.min(this._browserWidth, finalX))),
			y: Math.round(Math.max(0, Math.min(this._browserHeight, finalY)))
		};
	}

	private _redraw() {
		if (!this._ctx || !this._canvas) return;
		
		this._ctx.clearRect(0, 0, this._canvas.width, this._canvas.height);

		if (!this._lastImage) return;

		this._ctx.save();
		
		// Apply pan and zoom
		this._ctx.translate(this._offsetX, this._offsetY);
		this._ctx.scale(this._scale, this._scale);

		// Draw image centered in the un-scaled canvas space
		const scaleFit = Math.min(
			this._canvas.width / this._browserWidth,
			this._canvas.height / this._browserHeight
		);
		const dw = this._browserWidth * scaleFit;
		const dh = this._browserHeight * scaleFit;
		const dx = (this._canvas.width - dw) / 2;
		const dy = (this._canvas.height - dh) / 2;

		this._ctx.drawImage(this._lastImage, dx, dy, dw, dh);
		
		this._ctx.restore();
	}

	private _startStream(): void {
		if (this._ws) {
			this._ws.close();
		}

		if (this._statusText) {
			this._statusText.innerText = 'Connecting to CDP WebSocket...';
		}

		// Connect to the IPC server's screencast proxy
		this._ws = new WebSocket('ws://127.0.0.1:50051/screencast/active');
		
		this._ws.onopen = () => {
			if (this._statusText) {
				this._statusText.innerText = 'CDP WebSocket Connected';
			}
		};

		this._ws.onmessage = (event) => {
			try {
				const msg = JSON.parse(event.data);
				if (msg.type === 'screencastFrame') {
					if (msg.metadata) {
						this._browserWidth = msg.metadata.deviceWidth || this._browserWidth;
						this._browserHeight = msg.metadata.deviceHeight || this._browserHeight;
					}

					const img = new Image();
					img.onload = () => {
						this._lastImage = img;
						this._redraw();
					};
					img.src = 'data:image/jpeg;base64,' + msg.data;
				}
			} catch (e) {
				console.error('Failed to parse WS message', e);
			}
		};

		this._ws.onclose = () => {
			if (this._statusText) {
				this._statusText.innerText = 'CDP WebSocket Disconnected';
			}
		};
	}

	override dispose(): void {
		if (this._ws) {
			this._ws.close();
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
