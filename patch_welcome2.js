const fs = require('fs');
const path = '/code/ATLAS/apps/vscode/src/vs/workbench/contrib/browserView/electron-browser/features/browserWelcomeFeature.ts';
let code = fs.readFileSync(path, 'utf8');

code = code.replace(
"		wsInput.placeholder = \"e.g. 127.0.0.1:42407\";",
"		wsInput.placeholder = \"e.g. 127.0.0.1:42407\";\n\t\twsInput.value = \"42407\";"
);

const autoConnectStr = `
		setTimeout(async () => {
			try {
				if (fetchBtn) {
					fetchBtn.element.click();
				}
			} catch (e) { console.error(e); }
		}, 1000);
`;

code = code.replace("const waitingMsg = $('.browser-waiting-msg', { style: 'margin-top: 16px; color: var(--vscode-descriptionForeground); font-style: italic;' });", 
"const waitingMsg = $('.browser-waiting-msg', { style: 'margin-top: 16px; color: var(--vscode-descriptionForeground); font-style: italic;' });" + autoConnectStr);

fs.writeFileSync(path, code);
console.log('Patched browserWelcomeFeature.ts');
