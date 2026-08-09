# ATLAS Code Viewer

A lightweight static web application that provides a GitHub-style source-code browsing experience for showcasing the ATLAS codebase.

## What is this?
This viewer is a read-only showcase designed to be hosted on GitHub Pages. It allows anyone to browse a snapshot of the ATLAS source code without requiring a GitHub login, a Personal Access Token, or direct access to the private repository. It provides:
- A file explorer tree
- Syntax-highlighted code viewing
- Markdown rendering
- Full-text code search
- Deep-linking capabilities

## How to use locally

### 1. Install dependencies
```bash
cd atlas-code-viewer
npm install
```

### 2. Prepare the source snapshot
Before you can run the app, you need to populate it with the repository data.
```bash
npm run prepare-repo
```
This script recursively copies the codebase from `../` into `public/repository/`, automatically excluding sensitive files (`.env`, `secrets`, `.git`, `node_modules`, binary assets). It also generates the `tree.json` and `search-index.json` manifests used by the viewer.

### 3. Run the development server
```bash
npm run dev
```

## How to build and deploy

### Manual Build
```bash
npm run build
```
The output will be placed in the `dist/` folder, ready for static deployment.

### GitHub Pages Deployment
A GitHub Actions workflow (`.github/workflows/deploy.yml`) is included. It automatically builds the application and deploys it to GitHub Pages whenever changes are pushed to the `code-viewer` branch. 

To configure this in GitHub:
1. Go to your repository **Settings** > **Pages**.
2. Under **Build and deployment**, change the Source to **GitHub Actions**.

## Limitations and Security
**This is not a security boundary.** Since the source code snapshot is transferred to the browser, technically knowledgeable users can download the files. Do not include API keys, database credentials, or `.env` files. The `prepare-repo.js` script actively filters these out, but always audit the snapshot before deploying.
