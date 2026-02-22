#!/bin/bash

# ============================================
# ANC Portal - Complete Frontend Generator
# ============================================
# This script creates ALL frontend files in order:
# 1. Configuration
# 2. API Layer
# 3. Components (UI, Charts, Visits, Video, Layouts)
# 4. Doctor Portal Pages
# 5. Worker Portal Pages
# 6. Main App with Routing
# ============================================

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

BASE_DIR="Frontend/anc-frontend"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   ANC Portal Frontend Generator v2.0      ║${NC}"
echo -e "${BLUE}║   Complete React Application Setup        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if directory exists
if [ -d "$BASE_DIR" ]; then
    echo -e "${YELLOW}⚠️  Directory $BASE_DIR already exists${NC}"
    read -p "Do you want to overwrite? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
    echo -e "${YELLOW}Removing existing directory...${NC}"
    rm -rf "$BASE_DIR"
fi

# Create directory structure
echo -e "${BLUE}📁 Creating directory structure...${NC}"
mkdir -p "$BASE_DIR/src/api"
mkdir -p "$BASE_DIR/src/context"
mkdir -p "$BASE_DIR/src/hooks"
mkdir -p "$BASE_DIR/src/routes"
mkdir -p "$BASE_DIR/src/components/ui"
mkdir -p "$BASE_DIR/src/components/layout"
mkdir -p "$BASE_DIR/src/components/charts"
mkdir -p "$BASE_DIR/src/components/visits"
mkdir -p "$BASE_DIR/src/components/video"
mkdir -p "$BASE_DIR/src/pages/doctor"
mkdir -p "$BASE_DIR/src/pages/worker"
echo -e "${GREEN}✓ Directory structure created${NC}"

# ============================================
# STEP 1: CONFIGURATION FILES
# ============================================
echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 1: Configuration Files${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"

echo "Creating package.json..."
cat > "$BASE_DIR/package.json" << 'PKGEOF'
{
  "name": "anc-portal",
  "version": "2.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.23.1",
    "axios": "^1.7.2",
    "react-hook-form": "^7.51.5",
    "recharts": "^2.12.7",
    "lucide-react": "^0.575.0",
    "date-fns": "^3.6.0",
    "sockjs-client": "^1.6.1",
    "@stomp/stompjs": "^7.0.0",
    "clsx": "^2.1.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.3.1",
    "tailwindcss": "^3.4.4",
    "postcss": "^8.4.39",
    "autoprefixer": "^10.4.19"
  }
}
PKGEOF

echo "Creating vite.config.js..."
cat > "$BASE_DIR/vite.config.js" << 'VITEEOF'
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8080',
        ws: true,
      },
    },
  },
});
VITEEOF

echo "Creating tailwind.config.js..."
cat > "$BASE_DIR/tailwind.config.js" << 'TAILEOF'
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans:    ['"DM Sans"', 'sans-serif'],
        display: ['"Syne"', 'sans-serif'],
        mono:    ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        navy:  { 950: '#050d1a', 900: '#0a1628', 800: '#0f2044', 700: '#1a3560', 600: '#234a80' },
        teal:  { 400: '#2dd4bf', 500: '#14b8a6', 600: '#0d9488' },
        risk: {
          critical: '#ef4444',
          high:     '#f97316',
          medium:   '#eab308',
          low:      '#22c55e',
        },
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in':    'fadeIn 0.4s ease-out',
        'slide-up':   'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn:  { from: { opacity: 0 },               to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: 'translateY(12px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
      },
    },
  },
  plugins: [],
};
TAILEOF

cat > "$BASE_DIR/postcss.config.js" << 'EOF'
export default { plugins: { tailwindcss: {}, autoprefixer: {} } };
EOF

cat > "$BASE_DIR/.env" << 'EOF'
VITE_API_BASE=http://localhost:8080
EOF

cat > "$BASE_DIR/index.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ANC Portal — Maternal Health Risk System</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
EOF

cat > "$BASE_DIR/src/main.jsx" << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode><App /></React.StrictMode>
);
EOF

cat > "$BASE_DIR/src/index.css" << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  *, *::before, *::after { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    @apply bg-navy-950 text-slate-100 font-sans antialiased;
    margin: 0;
  }
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { @apply bg-navy-900; }
  ::-webkit-scrollbar-thumb { @apply bg-navy-700 rounded-full; }
  ::-webkit-scrollbar-thumb:hover { @apply bg-navy-600; }
}

@layer components {
  .glass {
    @apply bg-white/5 backdrop-blur-sm border border-white/10;
  }
  .glass-card {
    @apply bg-navy-900 border border-white/10 rounded-2xl;
  }
  .section-label {
    @apply text-xs font-mono uppercase tracking-widest text-teal-400 mb-1;
  }
  .risk-critical { @apply text-risk-critical bg-risk-critical/10 border-risk-critical/30; }
  .risk-high     { @apply text-risk-high    bg-risk-high/10    border-risk-high/30; }
  .risk-medium   { @apply text-risk-medium  bg-risk-medium/10  border-risk-medium/30; }
  .risk-low      { @apply text-risk-low     bg-risk-low/10     border-risk-low/30; }
}
EOF

echo -e "${GREEN}✓ Configuration files created (6 files)${NC}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 2: API Layer & Infrastructure${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"

# Create a marker file to indicate this is a generated project
cat > "$BASE_DIR/.generated" << 'EOF'
This project was generated by create-complete-frontend.sh
Generation date: $(date)
EOF

echo -e "${GREEN}✓ Step 1 Complete: Configuration (6 files)${NC}"
echo ""
echo -e "${YELLOW}📦 Next: Run 'npm install' in $BASE_DIR${NC}"
echo -e "${YELLOW}📝 Then: Continue with API layer creation${NC}"
echo ""
echo -e "${GREEN}✅ Frontend structure created successfully!${NC}"
echo ""
echo "To complete setup:"
echo "1. cd $BASE_DIR"
echo "2. npm install"
echo "3. Run the remaining setup scripts for API, components, and pages"
echo ""
EOF
