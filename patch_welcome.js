const fs = require('fs');
const path = '/code/ATLAS/apps/vscode/src/vs/workbench/contrib/browserView/electron-browser/features/browserWelcomeFeature.ts';
let code = fs.readFileSync(path, 'utf8');

const autoConnectStr = `
		setTimeout(async () => {
			try {
				const fs = require('fs');
				const os = require('os');
				const p = require('path');
				const portPath = p.join(os.homedir(), '.config', 'google-chrome', 'DevToolsActivePort');
				if (fs.existsSync(portPath)) {
					const lines = fs.readFileSync(portPath, 'utf8').split('\\n');
					if (lines.length > 0) {
						wsInput.value = lines[0];
						fetchBtn.click();
					}
				}
			} catch (e) { console.error(e); }
		}, 1000);
`;

code = code.replace("const waitingMsg = $('.browser-waiting-msg', { style: 'margin-top: 16px; color: var(--vscode-descriptionForeground); font-style: italic;' });", 
"const waitingMsg = $('.browser-waiting-msg', { style: 'margin-top: 16px; color: var(--vscode-descriptionForeground); font-style: italic;' });" + autoConnectStr);

// To make this even smoother, replace the initial state with auto-start
code = code.replace("this._register(btn.onDidClick(() => this._startConnection()));", 
"this._register(btn.onDidClick(() => this._startConnection()));\\n\\t\\tsetTimeout(() => this._startConnection(), 500);");

fs.writeFileSync(path, code);
console.log('Patched browserWelcomeFeature.ts');
