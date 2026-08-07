#!/bin/bash
set -e

echo "Creating new directory structure..."
mkdir -p apps/desktop apps/website apps/docs
mkdir -p runtime/kernel runtime/context runtime/events runtime/capabilities runtime/workflows runtime/policy runtime/contracts runtime/adapters
mkdir -p memory plugins browser filesystem terminal models mcp skills services execution planner packages sdk docs configs assets scripts tests tools

echo "Moving frontend to apps/desktop..."
# mv frontend content into apps/desktop
shopt -s dotglob
mv frontend/* apps/desktop/ 2>/dev/null || true
rmdir frontend 2>/dev/null || true
shopt -u dotglob

echo "Moving core components..."
mv atlas/core/runtime/* runtime/kernel/ 2>/dev/null || true
mv atlas/core/context/* runtime/context/ 2>/dev/null || true
mv atlas/core/events/* runtime/events/ 2>/dev/null || true
mv atlas/core/capabilities/* runtime/capabilities/ 2>/dev/null || true
mv atlas/core/workflows/* runtime/workflows/ 2>/dev/null || true
mv atlas/core/security/* runtime/policy/ 2>/dev/null || true
mv atlas/core/contracts/* runtime/contracts/ 2>/dev/null || true
mv atlas/core/memory/* memory/ 2>/dev/null || true
mv atlas/core/plugins/* plugins/ 2>/dev/null || true

echo "Moving integrations..."
mv atlas/integrations/browser/* browser/ 2>/dev/null || true
mv atlas/integrations/filesystem/* filesystem/ 2>/dev/null || true
mv atlas/integrations/command/* terminal/ 2>/dev/null || true
mkdir -p terminal/docker terminal/git models/ocr models/voice models/documents models/media
mv atlas/integrations/docker/* terminal/docker/ 2>/dev/null || true
mv atlas/integrations/git/* terminal/git/ 2>/dev/null || true
mv atlas/integrations/ocr/* models/ocr/ 2>/dev/null || true
mv atlas/integrations/voice/* models/voice/ 2>/dev/null || true
mv atlas/integrations/documents/* models/documents/ 2>/dev/null || true
mv atlas/integrations/media/* models/media/ 2>/dev/null || true

echo "Moving adapters..."
mv atlas/adapters/* runtime/adapters/ 2>/dev/null || true

echo "Moving api.py..."
mv api.py runtime/main.py 2>/dev/null || true

echo "Cleaning up atlas..."
rm -rf atlas

echo "Refactoring imports..."
# Use sed to replace old imports with new ones
find . -name "*.py" -type f -exec sed -i \
  -e 's/atlas\.core\.runtime/runtime.kernel/g' \
  -e 's/atlas\.core\.context/runtime.context/g' \
  -e 's/atlas\.core\.events/runtime.events/g' \
  -e 's/atlas\.core\.capabilities/runtime.capabilities/g' \
  -e 's/atlas\.core\.workflows/runtime.workflows/g' \
  -e 's/atlas\.core\.security/runtime.policy/g' \
  -e 's/atlas\.core\.contracts/runtime.contracts/g' \
  -e 's/atlas\.core\.memory/memory/g' \
  -e 's/atlas\.core\.plugins/plugins/g' \
  -e 's/atlas\.integrations\.browser/browser/g' \
  -e 's/atlas\.integrations\.filesystem/filesystem/g' \
  -e 's/atlas\.integrations\.command/terminal/g' \
  -e 's/atlas\.integrations\.docker/terminal.docker/g' \
  -e 's/atlas\.integrations\.git/terminal.git/g' \
  -e 's/atlas\.integrations\.ocr/models.ocr/g' \
  -e 's/atlas\.integrations\.voice/models.voice/g' \
  -e 's/atlas\.integrations\.documents/models.documents/g' \
  -e 's/atlas\.integrations\.media/models.media/g' \
  -e 's/atlas\.adapters/runtime.adapters/g' \
  {} +

echo "Done"
