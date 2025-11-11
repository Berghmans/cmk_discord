#!/bin/bash
set -e

# Get version from pyproject.toml or use argument
if [ -n "$1" ]; then
    VERSION="$1"
else
    VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
fi

echo "Building MKP package for version $VERSION"

# Clean up any existing build artifacts
rm -f notifications.tar discord-*.mkp

# Create notifications.tar containing just cmk_discord.py (uncompressed tar)
echo "Creating notifications.tar..."
tar -cf notifications.tar -C src/notifications cmk_discord.py

# Create the MKP (tar.gz renamed to .mkp)
echo "Creating discord-$VERSION.mkp..."
tar -czf "discord-$VERSION.mkp" -C src info info.json -C .. notifications.tar

# Clean up intermediate file
rm -f notifications.tar

echo "✓ Successfully created discord-$VERSION.mkp"
echo ""
echo "To test the package contents:"
echo "  tar -tzf discord-$VERSION.mkp"
echo ""
echo "To extract and inspect:"
echo "  mkdir -p test-mkp && cd test-mkp"
echo "  tar -xzf ../discord-$VERSION.mkp"
