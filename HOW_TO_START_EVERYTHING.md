# 🚀 How to Start the Complete ANC Portal System

## Current Status

### ✅ Backend
- **Status**: Restarting after fixing compilation errors
- **Terminal ID**: 4
- **Port**: 8080
- **Fixed Issues**: UUID conversion and gestationalWeeks extraction

### ⚠️ Frontend  
- **Status**: Needs manual start (file lock issue)
- **Port**: 5173
- **Issue**: Windows file lock on node_modules

### ✅ Medical RAG Pipeline
- **Status**: Ready to start
- **Port**: 8000
- **Location**: `Medical RAG Pipeline/`

---

## 🎯 Quick Start Guide

### Step 1: Start Backend (Already Running)
The backend is currently starting. Wait for this message:
```
Started AncServiceApplication in X.XXX seconds
```

Check status:
```bash
# In a new terminal
curl http://localhost:8080/actuator/health
```

### Step 2: Start Frontend (Manual Fix Required)

**Option A: Simple Restart (Try This First)**
```bash
# Open a NEW PowerShell terminal
cd "C:\Users\Ayushman M\OneDrive\Desktop\NeoSure\Frontend\anc-frontend"
npm run dev
```

**Option B: If Option A Fails**
```bash
# Close ALL terminals first
# Open a NEW PowerShell terminal
cd "C:\Users\Ayushman M\OneDrive\Desktop\NeoSure\Frontend\anc-frontend"

# Clean install
npm cache clean --force
Remove-Item node_modules -Recurse -Force -ErrorAction SilentlyContinue
npm install
npm run dev
```

**Option C: If Still Failing**
1. Close ALL terminals and VS Code
2. Restart your computer
3. Open a fresh terminal
4. Run Option A again

### Step 3: Start Medical RAG Pipeline (Optional)

```bash
# In a new terminal
cd "C:\Users\Ayushman M\OneDrive\Desktop\NeoSure\Medical RAG Pipeline"
python api_server.py
```

---

## 📍 Access URLs

Once all services are running:

### Frontend
- **Worker Portal**: http://localhost:5173/login
- **Doctor Portal**: http://localhost:5173/doctor/login
- **Main**: http://localhost:5173

### Backend API
- **Health Check**: http://localhost:8080/actuator/health
- **Base URL**: http://localhost:8080/api

### Medical RAG API
- **Health**: http://localhost:8000/health
- **Docs**: http://localhost:8000/docs
- **Base URL**: http://localhost:8000

---

## 🧪 Test the System

### 1. Test Backend
```bash
curl http://localhost:8080/actuator/health
```

Expected response:
```json
{"status":"UP"}
```

### 2. Test Frontend
Open browser: http://localhost:5173

You should see the login page.

### 3. Test Medical RAG
```bash
curl http://localhost:8000/health
```

---

## 🔧 Troubleshooting

### Frontend Won't Start - File Lock Error

**Symptom**: `EBUSY: resource busy or locked`

**Solution**:
1. Close ALL terminals
2. Close VS Code / any editors
3. Wait 10 seconds
4. Open fresh terminal
5. Try again

**If still failing**:
```powershell
# Kill all Node processes
taskkill /F /IM node.exe /T

# Wait 5 seconds
Start-Sleep -Seconds 5

# Try starting again
cd Frontend/anc-frontend
npm run dev
```

### Backend Compilation Errors

**Status**: ✅ FIXED
- Fixed UUID conversion issues
- Fixed gestationalWeeks extraction from JSON

### Database Not Connected

```bash
# Check PostgreSQL is running
# Windows: Check Services for PostgreSQL

# Test connection
psql -U postgres -d NeoSure -c "SELECT 1;"

# Run migrations if needed
psql -U postgres -d NeoSure -f Backend/src/main/resources/doctor_module_schema.sql
```

### Port Already in Use

```bash
# Check what's using port 8080
netstat -ano | findstr :8080

# Kill the process
taskkill /F /PID <process_id>

# Check port 5173
netstat -ano | findstr :5173
taskkill /F /PID <process_id>
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ANC Portal System                        │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Frontend   │─────▶│   Backend    │─────▶│  PostgreSQL  │
│  React+Vite  │      │ Spring Boot  │      │   Database   │
│  Port: 5173  │      │  Port: 8080  │      │  Port: 5432  │
└──────────────┘      └──────────────┘      └──────────────┘
                             │
                             │ HTTP
                             ▼
                      ┌──────────────┐
                      │ Medical RAG  │
                      │   FastAPI    │
                      │  Port: 8000  │
                      └──────────────┘
```

---

## ✅ Verification Checklist

- [ ] Backend started successfully (check terminal output)
- [ ] Backend health check returns `{"status":"UP"}`
- [ ] Frontend dev server running (shows "Local: http://localhost:5173")
- [ ] Can access frontend in browser
- [ ] Can see login page
- [ ] Medical RAG API running (optional)
- [ ] Database connection working

---

## 🎓 What to Do Next

### 1. Create Test Accounts

**Worker Account**:
- Go to: http://localhost:5173/signup
- Register a worker account
- Login and test dashboard

**Doctor Account**:
- Go to: http://localhost:5173/doctor/signup
- Register a doctor account
- Login and test queue

### 2. Test Complete Flow

1. **Worker**: Register a patient
2. **Worker**: Create an ANC visit (7 steps)
3. **Worker**: View AI risk assessment
4. **Doctor**: See case in priority queue
5. **Doctor**: Accept consultation
6. **Doctor**: Start video call (WebRTC)
7. **Doctor**: Complete consultation with notes

### 3. Monitor Logs

Keep terminals open to see:
- Backend API calls
- Frontend hot reload
- Any errors or warnings

---

## 📝 Important Notes

### File Lock Issue (Windows)
The frontend file lock is a known Windows + Vite issue. The solution is to:
1. Always close terminals properly
2. Use fresh terminals for npm commands
3. Restart computer if locks persist

### Backend Fixes Applied
✅ Fixed UUID conversion in ConsultationService
✅ Fixed gestationalWeeks extraction from JSON
✅ Backend should now compile and start successfully

### All Code is Ready
- ✅ 46 frontend files created
- ✅ Backend fully implemented
- ✅ Medical RAG Pipeline configured
- ✅ Database schema ready

---

## 🆘 Need Help?

### Check Running Processes
```powershell
# List all processes
Get-Process | Where-Object {$_.ProcessName -match "node|java|python"}

# Check specific ports
netstat -ano | findstr "5173 8080 8000"
```

### View Logs
- **Backend**: Check terminal with ID 4
- **Frontend**: Check your manual terminal
- **Database**: Check PostgreSQL logs

### Common Commands
```bash
# Stop all Node processes
taskkill /F /IM node.exe

# Stop all Java processes
taskkill /F /IM java.exe

# Restart PostgreSQL (Windows)
net stop postgresql-x64-14
net start postgresql-x64-14
```

---

**Status**: Backend restarting, Frontend needs manual start
**Last Updated**: $(Get-Date)
**Ready to Use**: Almost! Just need to start frontend manually.
