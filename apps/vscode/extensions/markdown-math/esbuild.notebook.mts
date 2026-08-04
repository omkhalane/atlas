/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
import fse from 'fs-extra';
import path from 'path';
import { run } from '../esbuild-webview-common.mts';

const srcDir = path.join(import.meta.dirname, 'notebook');
const outDir = path.join(import.meta.dirname, 'notebook-out');

function postBuild(outDir: string) {
	try {
		const katexDist = fse.existsSync(path.join(import.meta.dirname, 'node_modules', 'katex'))
			? path.join(import.meta.dirname, 'node_modules', 'katex', 'dist')
			: path.resolve(import.meta.dirname, '../../../../node_modules/katex/dist');

		if (fse.existsSync(katexDist)) {
			fse.copySync(
				path.join(katexDist, 'katex.min.css'),
				path.join(outDir, 'katex.min.css'));

			const fontsDir = path.join(katexDist, 'fonts');
			const fontsOutDir = path.join(outDir, 'fonts');

			fse.mkdirSync(fontsOutDir, { recursive: true });

			if (fse.existsSync(fontsDir)) {
				for (const file of fse.readdirSync(fontsDir)) {
					const srcFile = path.join(fontsDir, file);
					if (fse.statSync(srcFile).isFile() && file.endsWith('.woff2')) {
						fse.copyFileSync(srcFile, path.join(fontsOutDir, file));
					}
				}
			}
		}
	} catch (e) {
		console.warn('katex postBuild copy warning:', e);
	}
}

run({
	entryPoints: [
		path.join(srcDir, 'katex.ts'),
	],
	srcDir,
	outdir: outDir,
}, process.argv, postBuild);
