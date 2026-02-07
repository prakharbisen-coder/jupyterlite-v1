#!/bin/bash
# Resolve symlinks in _site for S3 deployment

echo "Resolving symlinks in _site directory..."

# Replace config-utils.js symlink with actual file
if [ -L "_site/config-utils.js" ]; then
    echo "Replacing config-utils.js symlink..."
    rm _site/config-utils.js
    cp app/config-utils.js _site/config-utils.js
    echo "✓ config-utils.js copied"
fi

# Replace service-worker.js symlink with actual file
if [ -L "_site/service-worker.js" ]; then
    echo "Replacing service-worker.js symlink..."
    rm _site/service-worker.js
    cp app/service-worker.js _site/service-worker.js
    echo "✓ service-worker.js copied"
fi

# Replace build directory symlink with actual directory
if [ -L "_site/build" ]; then
    echo "Replacing build/ symlink..."
    rm _site/build
    cp -r app/build _site/build
    echo "✓ build/ directory copied"
fi

echo ""
echo "✅ All symlinks resolved! _site is now ready for S3 deployment."
echo ""
echo "Verify with: ls -la _site/ | grep -E '(config-utils|service-worker|build)'"
