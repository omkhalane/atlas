import * as vscode from 'vscode';
import { AtlasIpcClient, IAtlasEvent } from './atlasIpcClient';

let atlasIpc: AtlasIpcClient;

export function activate(context: vscode.ExtensionContext) {
    atlasIpc = new AtlasIpcClient();

    const uriHandler = {
        handleUri: (uri: vscode.Uri) => {
            if (uri.path === '/auth' || uri.authority === 'auth') {
                const queryParams = new URLSearchParams(uri.query);
                const code = queryParams.get('code');
                const requestId = queryParams.get('request_id');
                if (code && requestId) {
                    atlasIpc.grantAuth(requestId, code).catch(console.error);
                }
            }
        }
    };
    context.subscriptions.push(vscode.window.registerUriHandler(uriHandler));

    const handler: vscode.ChatRequestHandler = async (
        request: vscode.ChatRequest,
        chatContext: vscode.ChatContext,
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ) => {
        const execId = vscode.env.sessionId + '-' + Date.now();
        
        token.onCancellationRequested(() => {
            atlasIpc.cancelExecution(execId).catch(console.error);
        });

        return new Promise<void>((resolve, reject) => {
            const disposable = atlasIpc.onEvent((event: IAtlasEvent) => {
                // If the event doesn't specify exec_id, or it matches, we process it.
                // Ideally, the server should return exec_id.
                if (event.exec_id && event.exec_id !== execId) return;

                if (event.type === 'THOUGHT') {
                    stream.progress(event.content + '\n');
                } else if (event.type === 'message') {
                    stream.markdown(event.content || '');
                } else if (event.type === 'tool_approval') {
                    stream.progress(`🔧 Automatically approving execution of ${event.tool_name}\n`);
                    atlasIpc.approveTool(execId, true).catch(console.error);
                } else if (event.type === 'cdp_auth_request') {
                    const requestId = event.request_id;
                    const authUrl = `http://127.0.0.1:8000/auth/authorize?request_id=${requestId}`;
                    stream.progress(`🔒 Requesting browser authorization...\n`);
                    vscode.env.openExternal(vscode.Uri.parse(authUrl));
                } else if (event.type === 'finish' || event.type === 'error') {
                    disposable.dispose();
                    if (event.type === 'error') {
                        reject(new Error(event.error));
                    } else {
                        resolve();
                    }
                }
            });

            const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
            atlasIpc.executeGoal(request.prompt, execId, workspaceRoot).catch(err => {
                disposable.dispose();
                reject(err);
            });
        });
    };

    const atlasParticipant = vscode.chat.createChatParticipant('atlas.chat', handler);
    atlasParticipant.iconPath = new vscode.ThemeIcon('hubot');
    
    context.subscriptions.push(atlasParticipant);
}

export function deactivate() {}
