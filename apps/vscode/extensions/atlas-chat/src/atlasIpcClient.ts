import * as vscode from 'vscode';
import * as http from 'http';

export interface IAtlasEvent {
	task_id?: string;
	exec_id?: string;
	type?: string;
	content?: string;
	status?: string;
	error?: string;
	result?: any;
	tool_name?: string;
	arguments?: any;
	request_id?: string;
}

export class AtlasIpcClient {
	private readonly _port = 50051;
	private readonly _baseUrl = `http://127.0.0.1:${this._port}`;

	private readonly _onEvent = new vscode.EventEmitter<IAtlasEvent>();
	public readonly onEvent: vscode.Event<IAtlasEvent> = this._onEvent.event;

	constructor() {}

	public async executeGoal(goal: string, execId: string, workspaceRoot?: string): Promise<void> {
		const res = await fetch(`${this._baseUrl}/execute`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				goal,
				exec_id: execId,
				workspace_root: workspaceRoot
			})
		});
		if (!res.ok) {
			throw new Error(`Atlas IPC execute failed: ${res.statusText}`);
		}
		this._streamEvents(execId);
	}

	public async cancelExecution(execId: string): Promise<void> {
		const res = await fetch(`${this._baseUrl}/cancel`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ exec_id: execId })
		});
		if (!res.ok) {
			throw new Error(`Atlas IPC cancel failed: ${res.statusText}`);
		}
	}

	public async approveTool(execId: string, approved: boolean): Promise<void> {
		const res = await fetch(`${this._baseUrl}/approve`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ exec_id: execId, approved })
		});
		if (!res.ok) {
			throw new Error(`Atlas IPC approve failed: ${res.statusText}`);
		}
	}

	public async grantAuth(requestId: string, code: string): Promise<void> {
		const res = await fetch(`${this._baseUrl}/auth/grant`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ request_id: requestId, code })
		});
		if (!res.ok) {
			throw new Error(`Atlas IPC grant auth failed: ${res.statusText}`);
		}
	}

	// --- Integrations API ---

	public async getCapabilities(): Promise<any[]> {
		const res = await fetch(`${this._baseUrl}/integrations/capabilities`);
		if (!res.ok) throw new Error(`Failed to fetch capabilities`);
		return res.json();
	}

	public async getPlugins(): Promise<any[]> {
		const res = await fetch(`${this._baseUrl}/integrations/plugins`);
		if (!res.ok) throw new Error(`Failed to fetch plugins`);
		return res.json();
	}

	public async getMcpServers(): Promise<{ installed: any[], available: any[] }> {
		const res = await fetch(`${this._baseUrl}/integrations/mcp`);
		if (!res.ok) throw new Error(`Failed to fetch MCP servers`);
		return res.json();
	}

	public async installMcpServer(mcpId: string): Promise<void> {
		const res = await fetch(`${this._baseUrl}/integrations/mcp/install`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ mcp_id: mcpId })
		});
		if (!res.ok) throw new Error(`Failed to install MCP server: ${res.statusText}`);
	}

	public async updatePermission(providerId: string, permissionId: string, grant: boolean): Promise<void> {
		const res = await fetch(`${this._baseUrl}/integrations/permissions`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ provider_id: providerId, permission_id: permissionId, grant })
		});
		if (!res.ok) throw new Error(`Failed to update permissions: ${res.statusText}`);
	}

	private async _streamEvents(execId: string): Promise<void> {
		try {
			const req = http.get(`${this._baseUrl}/events/${execId}`, (res) => {
				let buffer = '';
				res.on('data', (chunk) => {
					buffer += chunk.toString();
					const lines = buffer.split('\n\n');
					buffer = lines.pop() || ''; 
					
					for (const line of lines) {
						if (line.startsWith('data: ')) {
							try {
								const data = JSON.parse(line.substring(6));
								this._onEvent.fire(data as IAtlasEvent);
							} catch (e) {
								console.error('Failed to parse ATLAS SSE event', e);
							}
						}
					}
				});
				res.on('end', () => {
					console.log(`ATLAS stream ended for ${execId}`);
				});
			});
			req.on('error', (err) => {
				console.error(`ATLAS IPC stream error: ${err.message}`);
			});
		} catch (err) {
			console.error('Failed to connect to ATLAS SSE', err);
		}
	}
}
