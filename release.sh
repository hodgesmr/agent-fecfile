#!/usr/bin/env bash
set -euo pipefail

# Extract version from SKILL.md frontmatter
VERSION=$(grep -A2 '^metadata:' skills/fecfile/SKILL.md | grep 'version:' | sed 's/.*version: *"\([^"]*\)".*/\1/')

if [[ -z "$VERSION" ]]; then
    echo "Error: Could not extract version from skills/fecfile/SKILL.md"
    exit 1
fi

echo "Releasing version $VERSION"

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
