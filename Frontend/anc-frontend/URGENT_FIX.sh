#!/bin/bash
# Quick fix for Tailwind CSS version mismatch

cd "$(dirname "$0")"

echo "Fixing Tailwind CSS version mismatch..."
echo "Current: v4.2.0 (beta) - Expected: v3.4.4 (stable)"

# Remove problematic v4 packages
npm uninstall tailwindcss @tailwindcss/node @tailwindcss/postcss

# Install correct v3 version
npm install tailwindcss@^3.4.4 --save-dev

# Reinstall clsx to be sure
npm install clsx

echo "✅ Fixed! Restart dev server with: npm run dev"
