# 🚀 Quick Start Guide - Test Your ANC Portal

## ✅ All Systems Running

- Backend: http://localhost:8080
- Frontend: http://localhost:5173
- Medical RAG: http://localhost:8000

## 📝 Step-by-Step Testing

### Step 1: Create a Worker Account

1. Open your browser: **http://localhost:5173**
2. You'll be redirected to the login page
3. Click **"Create one now"** (or go to http://localhost:5173/signup)
4. Fill in the signup form:
   - Full Name: `Test Worker`
   - Phone: `9876543210`
   - Email: `worker@test.com`
   - Password: `password123`
   - Health Center: `PHC Test Center`
   - District: `Test District`
5. Click **"Create Account"**
6. You should be automatically logged in and redirected to the dashboard

### Step 2: Test Worker Login

1. If you're logged in, logout first
2. Go to http://localhost:5173/login
3. Enter:
   - Phone: `9876543210`
   - Password: `password123`
4. Click **"Sign In"**
5. You should be redirected to `/dashboard`

### Step 3: Create a Doctor Account

1. Go to **http://localhost:5173/doctor/signup**
2. Fill in the form:
   - Full Name: `Dr. Test Doctor`
   - Phone: `9876543211` (different from worker)
   - Email: `doctor@test.com`
   - Password: `password123`
   - Specialization: `Obstetrics & Gynaecology`
   - Hospital: `Test Hospital`
   - District: `Test District`
   - Registration No: `MCI12345`
3. Click **"Create Account"**
4. You should be redirected to the doctor dashboard

### Step 4: Test Doctor Login

1. Go to **http://localhost:5173/doctor/login**
2. Enter:
   - Phone: `9876543211`
   - Password: `password123`
3. Click **"Sign In"**
4. You should see the doctor dashboard

---

## 🔧 Troubleshooting

### Issue: "Login failed" or "Signup failed"

**Check Backend:**
```powershell
# Test if backend is responding
curl http://localhost:8080/api/auth/health
```

If you get an error, check Terminal ID 8 for backend logs.

### Issue: Button doesn't do anything

**Open Browser Console:**
1. Press F12 in your browser
2. Go to the "Console" tab
3. Try clicking the button again
4. Look for any red error messages

Common errors:
- `Network Error` - Backend is not running
- `404 Not Found` - API endpoint doesn't exist
- `CORS Error` - CORS configuration issue

### Issue: "Cannot read property of undefined"

This usually means the API response format doesn't match what the frontend expects.

**Check the response:**
1. Open Browser DevTools (F12)
2. Go to "Network" tab
3. Click the login button
4. Look for the `/api/auth/login` request
5. Click on it and check the "Response" tab

---

## 🎯 Expected Behavior

### After Successful Login (Worker):
- URL changes to `/dashboard`
- You see the worker dashboard with:
  - Welcome message
  - Patient statistics
  - Recent visits
  - Quick actions

### After Successful Login (Doctor):
- URL changes to `/doctor/dashboard`
- You see the doctor dashboard with:
  - Consultation queue
  - Priority cases
  - Statistics

---

## 📊 Test Data

### Worker Account
- Phone: `9876543210`
- Password: `password123`

### Doctor Account
- Phone: `9876543211`
- Password: `password123`

---

## 🐛 Common Issues

### 1. Backend Not Responding

**Symptoms:**
- Login button does nothing
- Network errors in console
- "Failed to fetch" errors

**Solution:**
```powershell
# Check if backend is running
netstat -ano | findstr :8080

# If not running, check Terminal ID 8
# Restart if needed
```

### 2. CORS Errors

**Symptoms:**
- "CORS policy" error in console
- Request blocked by browser

**Solution:**
The backend should already have CORS configured. If you see this error, check `Backend/src/main/java/com/anc/security/SecurityConfig.java`.

### 3. Database Connection Issues

**Symptoms:**
- Backend logs show "Connection refused"
- "Unable to connect to database"

**Solution:**
```powershell
# Check if PostgreSQL is running
# Windows: Check Services for PostgreSQL
```

### 4. Frontend Not Loading

**Symptoms:**
- Blank page
- "Cannot GET /" error

**Solution:**
```powershell
# Check if frontend is running
netstat -ano | findstr :5173

# If not running, restart
cd Frontend/anc-frontend
npm run dev
```

---

## 🎓 Next Steps

Once login works:

1. **Register a Patient** (Worker)
   - Go to Patients → New Patient
   - Fill in patient details
   - Save

2. **Create ANC Visit** (Worker)
   - Select a patient
   - Click "New Visit"
   - Fill all 7 steps
   - Submit for AI analysis

3. **View Risk Assessment** (Worker)
   - After submitting visit
   - View AI-generated risk assessment
   - See recommendations

4. **Accept Consultation** (Doctor)
   - Login as doctor
   - View priority queue
   - Accept a high-risk case
   - Start video consultation

---

## 💡 Tips

- Use Chrome or Edge for best compatibility
- Keep browser console open (F12) to see errors
- Check all three terminal windows for logs
- Test signup before login
- Use different phone numbers for worker and doctor

---

## 🆘 Still Having Issues?

1. **Check all services are running:**
   ```powershell
   netstat -ano | findstr "5173 8080 8000"
   ```

2. **Check browser console** (F12 → Console tab)

3. **Check backend logs** (Terminal ID 8)

4. **Try a different browser**

5. **Clear browser cache and localStorage:**
   - F12 → Application → Local Storage → Clear All
   - Refresh page (Ctrl+R)

---

**Status**: Ready to test!
**Next**: Open http://localhost:5173 and create your first account!
