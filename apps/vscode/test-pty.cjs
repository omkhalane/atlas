try {
	const pty = require('/code/ATLAS/apps/vscode/node_modules/node-pty');
	console.log('ELECTRON_PTY_OK: node-pty loaded successfully in Electron');
	const term = pty.spawn('bash', [], {
		name: 'xterm-color',
		cols: 80,
		rows: 30,
		cwd: process.env.HOME,
		env: process.env
	});
	console.log('ELECTRON_PTY_SPAWN_SUCCESS: spawned pid', term.pid);
	term.kill();
	process.exit(0);
} catch (e) {
	console.error('ELECTRON_PTY_FAIL:', e);
	process.exit(1);
}
