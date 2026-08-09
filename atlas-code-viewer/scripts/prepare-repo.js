import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths
const VIEWER_ROOT = path.resolve(__dirname, '..');
const REPO_ROOT = path.resolve(VIEWER_ROOT, '..');
const PUBLIC_REPO_DIR = path.join(VIEWER_ROOT, 'public', 'repository');

// Exclusions
const EXCLUDED_DIRS = new Set([
  '.git',
  'node_modules',
  'dist',
  'build',
  'coverage',
  '.cache',
  'atlas-code-viewer',
  '.vscode',
  '.idea'
]);

const EXCLUDED_EXTENSIONS = new Set([
  '.pem', '.key', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', 
  '.pdf', '.zip', '.tar', '.gz', '.mp3', '.mp4', '.woff', '.woff2', '.ttf'
]);

function isExcludedFile(filename) {
  if (filename === '.env' || filename.startsWith('.env.')) return true;
  if (filename.includes('secret') || filename.includes('credential')) return true;
  
  const ext = path.extname(filename).toLowerCase();
  if (EXCLUDED_EXTENSIONS.has(ext)) return true;

  return false;
}

// Tree and Index Data
const tree = [];
const searchIndex = [];

function walkAndCopy(srcDir, relativePath = '') {
  const items = fs.readdirSync(srcDir);
  const nodes = [];

  for (const item of items) {
    const itemPath = path.join(srcDir, item);
    const itemRelativePath = path.join(relativePath, item);
    
    // Skip excluded directories
    const stat = fs.statSync(itemPath);
    if (stat.isDirectory()) {
      if (EXCLUDED_DIRS.has(item)) continue;
      
      const targetDir = path.join(PUBLIC_REPO_DIR, itemRelativePath);
      fs.mkdirSync(targetDir, { recursive: true });
      
      const children = walkAndCopy(itemPath, itemRelativePath);
      if (children.length > 0) {
        nodes.push({
          name: item,
          path: itemRelativePath.replace(/\\/g, '/'),
          type: 'dir',
          children
        });
      }
    } else if (stat.isFile()) {
      if (isExcludedFile(item)) continue;

      // Copy file
      const targetFile = path.join(PUBLIC_REPO_DIR, itemRelativePath);
      fs.copyFileSync(itemPath, targetFile);
      
      nodes.push({
        name: item,
        path: itemRelativePath.replace(/\\/g, '/'),
        type: 'file',
        size: stat.size
      });

      // Add to search index if reasonable size (< 500KB)
      if (stat.size < 500 * 1024) {
        try {
          const content = fs.readFileSync(itemPath, 'utf8');
          // Only add if it's actually valid utf8 text (no null bytes)
          if (!content.includes('\0')) {
             searchIndex.push({
               path: itemRelativePath.replace(/\\/g, '/'),
               content
             });
          }
        } catch (e) {
          // Ignore binary read errors
        }
      }
    }
  }

  // Sort: directories first, then files
  nodes.sort((a, b) => {
    if (a.type === b.type) return a.name.localeCompare(b.name);
    return a.type === 'dir' ? -1 : 1;
  });

  return nodes;
}

function run() {
  console.log('Preparing repository snapshot...');
  
  // Clean public/repository
  if (fs.existsSync(PUBLIC_REPO_DIR)) {
    fs.rmSync(PUBLIC_REPO_DIR, { recursive: true, force: true });
  }
  fs.mkdirSync(PUBLIC_REPO_DIR, { recursive: true });

  // Walk, copy, and build tree
  const rootNodes = walkAndCopy(REPO_ROOT);
  
  // Write tree.json
  fs.writeFileSync(
    path.join(PUBLIC_REPO_DIR, 'tree.json'), 
    JSON.stringify(rootNodes, null, 2)
  );
  
  // Write search-index.json
  fs.writeFileSync(
    path.join(PUBLIC_REPO_DIR, 'search-index.json'), 
    JSON.stringify(searchIndex) // no pretty print to save space
  );

  console.log(`Snapshot complete. Created tree with ${searchIndex.length} searchable files.`);
}

run();
