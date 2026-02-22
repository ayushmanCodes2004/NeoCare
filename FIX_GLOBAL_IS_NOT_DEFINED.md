# Fix: "global is not defined" Error

## Problem
After installing SockJS-client, got error:
```
ReferenceError: global is not defined
at node_modules/sockjs-client/lib/utils/browser-crypto.js
```

## Root Cause
SockJS-client was written for older bundlers and expects a `global` variable. Vite uses ES modules and doesn't provide `global` by default.

## Solution Applied ✅

Updated `Frontend/lovable-frontend/vite.config.ts` to define `global` as `globalThis`:

```typescript
export default defineConfig(({ mode }) => ({
  // ... other config
  define: {
    global: 'globalThis',
  },
}));
```

## What This Does
- Maps `global` to `globalThis` (the standard way to access global scope)
- Makes SockJS-client compatible with Vite
- No runtime overhead - it's a build-time replacement

## Next Step
Restart the frontend dev server:

```bash
# Stop with Ctrl+C
cd Frontend/lovable-frontend
npm run dev
```

The error should be gone and WebRTC should work!

## Alternative Solutions (Not Needed)

### Option 1: Install vite-plugin-node-polyfills
```bash
npm install --save-dev vite-plugin-node-polyfills
```

### Option 2: Add to index.html
```html
<script>
  window.global = window;
</script>
```

We used the simplest solution (define in vite.config) which is the recommended approach.

## Status
✅ Fixed - `global` is now defined as `globalThis`
⏳ Pending - Restart frontend to apply changes
