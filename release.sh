#!/usr/bin/env bash
set -euo pipefail

# Extract version from plugin.json (primary source of truth)
VERSION=$(grep '"version"' .claude-plugin/plugin.json | sed 's/.*"version": *"\([^"]*\)".*/\1/')

if [[ -z "$VERSION" ]]; then
    echo "Error: Could not extract version from .claude-plugin/plugin.json"
    exit 1
fi

echo "Releasing version $VERSION"

# Verify version matches in SKILL.md
SKILL_VERSION=$(grep -A2 '^metadata:' skills/fecfile/SKILL.md | grep 'version:' | sed 's/.*version: *"\([^"]*\)".*/\1/')
if [[ "$VERSION" != "$SKILL_VERSION" ]]; then
    echo "Error: Version mismatch!"
    echo "  plugin.json: $VERSION"
    echo "  SKILL.md: $SKILL_VERSION"
    echo "Update both files to match before releasing."
    exit 1
fi

# Check for uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "Error: Uncommitted changes. Commit first."
    exit 1
fi

# Create version tag
if git rev-parse "$VERSION" >/dev/null 2>&1; then
    echo "Tag $VERSION already exists"
else
    git tag -a "$VERSION" -m "Release $VERSION"
    echo "Created tag $VERSION"
fi

# Move latest tag
git tag -d latest 2>/dev/null || true
git tag -a latest -m "Latest stable release"
echo "Updated latest tag"

# Push tags
git push origin "$VERSION"
git push origin latest --force

echo "Released $VERSION"
