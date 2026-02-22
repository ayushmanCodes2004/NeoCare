# ANC Portal - Startup Status

## Current Status

### ✅ Backend (Spring Boot)
- **Status**: Starting up
- **Terminal ID**: 3
- **Command**: `mvn spring-boot:run`
- **Directory**: `Backend/`
- **Expected Port**: 8080
- **Status**: Building and compiling...

### ⚠️ Frontend (React + Vite)
- **Status**: Dependency issue
- **Terminal ID**: 2 (stopped)
- **Command**: `npm run dev`
- **Directory**: `Frontend/anc-frontend/`
- **Expected Port**: 5173
- **Issue**: Missing `clsx` dependency + file lock issue

## Problem

The frontend has a file lock issue preventing npm from installing dependencies. This is a common Windows issue with Vite/Rolldown.

## Solution Options

### Option 1: Manual Fix (Recommended)
1. Close ALL terminals and editors
2. Open a NEW terminal
3. Navigate to `Frontend/anc-frontend`
4. Run: `npm install`
5. Run: `npm run dev`

### Option 2: Use PowerShell Admin
```powershell
# Open PowerShell as Administrator
cd "C:\Users\Ayushman M\OneDrive\Desktop\NeoSure\Frontend\anc-frontend"
npm cache clean --force
Remove-Item node_modules -Recurse -Force
npm install
npm run dev
```

### Option 3: Restart Computer
Sometimes Windows file locks require a system restart to clear.

## What's Working

✅ **Backend**: Starting up successfully
✅ **Database**: PostgreSQL configured
✅ **Medical RAG Pipeline**: Ready (needs separate start)

## What Needs Attention

⚠️ **Frontend**: File lock preventing dependency installation

## Next Steps

1. **Fix Frontend Dependencies**:
   - Close all terminals
   - Manually run `npm install` in a fresh terminal
   - Start with `npm run dev`

2. **Verify Backend Started**:
   - Check terminal output
   - Should see "Started AncServiceApplication" message
   - Test: http://localhost:8080/actuator/health

3. **Start Medical RAG Pipeline** (if needed):
   ```bash
   cd "Medical RAG Pipeline"
   python api_server.py
   ```

## Access URLs (Once Running)

- **Frontend**: http://localhost:5173
  - Worker Portal: http://localhost:5173/login
  - Doctor Portal: http://localhost:5173/doctor/login

- **Backend API**: http://localhost:8080
  - Health Check: http://localhost:8080/actuator/health
  - API Docs: http://localhost:8080/swagger-ui.html

- **Medical RAG API**: http://localhost:8000
  - Health: http://localhost:8000/health
  - Docs: http://localhost:8000/docs

## Troubleshooting

### Frontend Won't Start
```bash
# Kill any Node processes
taskkill /F /IM node.exe

# Clean and reinstall
cd Frontend/anc-frontend
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Backend Won't Start
```bash
# Check if port 8080 is in use
netstat -ano | findstr :8080

# Kill process if needed
taskkill /F /PID <process_id>

# Restart
cd Backend
mvn clean spring-boot:run
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
# Check connection in application.yml
# Run migration:
psql -U postgres -d NeoSure -f Backend/src/main/resources/doctor_module_schema.sql
```

## Current Process Status

Run this to check running processes:
```bash
# Check Node processes
tasklist | findstr node

# Check Java processes
tasklist | findstr java

# Check Python processes
tasklist | findstr python
```

---

**Last Updated**: $(Get-Date)
**Status**: Backend starting, Frontend needs manual fix
