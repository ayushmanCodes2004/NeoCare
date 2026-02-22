#!/bin/bash

# ANC Portal Frontend - Complete Setup Script
# This script creates all frontend files according to react2.md specification
# Focus: Doctor Portal first, then Worker Portal

set -e  # Exit on error

echo "🚀 Starting ANC Portal Frontend Setup..."
echo "================================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base directory
BASE_DIR="Frontend/anc-frontend"

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
# PART 1: CONFIGURATION FILES
# ============================================
echo -e "${BLUE}📝 Creating configuration files...${NC}"

# package.json
cat > "$BASE_DIR/package.json" << 'EOF'
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
EOF

# vite.config.js
cat > "$BASE_DIR/vite.config.js" << 'EOF'
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
EOF

# tailwind.config.js
cat > "$BASE_DIR/tailwind.config.js" << 'EOF'
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
EOF

# postcss.config.js
cat > "$BASE_DIR/postcss.config.js" << 'EOF'
export default { plugins: { tailwindcss: {}, autoprefixer: {} } };
EOF

# .env
cat > "$BASE_DIR/.env" << 'EOF'
VITE_API_BASE=http://localhost:8080
EOF

# index.html
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

echo -e "${GREEN}✓ Configuration files created${NC}"

# ============================================
# PART 2: CORE APP FILES
# ============================================
echo -e "${BLUE}📝 Creating core app files...${NC}"

# src/main.jsx
cat > "$BASE_DIR/src/main.jsx" << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode><App /></React.StrictMode>
);
EOF

# src/index.css
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

echo -e "${GREEN}✓ Core app files created${NC}"

echo ""
echo -e "${YELLOW}================================================${NC}"
echo -e "${YELLOW}Phase 1: Configuration Complete${NC}"
echo -e "${YELLOW}================================================${NC}"
echo ""
echo "Next steps:"
echo "1. Run: cd $BASE_DIR && npm install"
echo "2. Run: ./create-frontend-api.sh (for API layer)"
echo "3. Run: ./create-frontend-components.sh (for components)"
echo "4. Run: ./create-frontend-doctor.sh (for doctor portal)"
echo "5. Run: ./create-frontend-worker.sh (for worker portal)"
echo ""
echo -e "${GREEN}✓ Setup script completed successfully!${NC}"
EOF
</invoke>