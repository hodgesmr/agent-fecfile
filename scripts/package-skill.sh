#!/bin/bash
# Package the FEC Filing skill as a ZIP for upload to Claude
#
# Usage: ./scripts/package-skill.sh
#
# Output: fec-filing-skill.zip in the repo root

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SKILL_DIR="$REPO_ROOT/.claude/skills/fec-filing"
OUTPUT_FILE="$REPO_ROOT/fec-filing-skill.zip"

# Remove existing zip if present
rm -f "$OUTPUT_FILE"

# Create zip from the skill directory
cd "$SKILL_DIR"
zip -r "$OUTPUT_FILE" . -x "*.DS_Store"

echo "Created: $OUTPUT_FILE"
echo ""
echo "To use:"
echo "  1. Go to Claude Settings > Capabilities"
echo "  2. In the Skills section, click 'Upload skill'"
echo "  3. Upload fec-filing-skill.zip"
