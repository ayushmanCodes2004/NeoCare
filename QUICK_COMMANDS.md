# ⚡ Quick Commands Reference

## 🚀 Start Everything

### One Command (Recommended)
```bash
START_ALL_SERVICES.bat
```

### Manual Start
```bash
# Terminal 1: Backend
cd Backend && ./run.bat

# Terminal 2: RAG
cd "Medical RAG Pipeline" && python api_server.py

# Terminal 3: Frontend
cd Frontend/lovable-frontend && npm run dev
```

---

## 🌐 URLs

```
Frontend:  http://localhost:5173
Backend:   http://localhost:8080
Swagger:   http://localhost:8080/swagger-ui/index.html
API Test:  http://localhost:8080/api-tester.html
RAG API:   http://localhost:8000
```

---

## 📦 Frontend Commands

```bash
cd Frontend/lovable-frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm run test

# Lint code
npm run lint
```

---

## 🔧 Backend Commands

```bash
cd Backend

# Start backend
./run.bat
# Or: mvn spring-boot:run

# Build
mvn clean install

# Run tests
mvn test
```

---

## 🤖 RAG Pipeline Commands

```bash
cd "Medical RAG Pipeline"

# Start server
python api_server.py

# Test health
curl http://localhost:8000/health
```

---

## 🐛 Troubleshooting

### Kill Process on Port
```bash
# Find process
netstat -ano | findstr :5173

# Kill it
taskkill /PID <PID> /F
```

### Clear Frontend Cache
```bash
cd Frontend/lovable-frontend
rm -rf node_modules package-lock.json
npm install
```

### Restart Backend
```bash
cd Backend
mvn clean install
./run.bat
```

---

## 📚 Documentation

```
INTEGRATION_COMPLETE_SUMMARY.md      # Start here!
FRONTEND_BACKEND_INTEGRATION.md      # Full integration guide
LOVABLE_FRONTEND_SPECIFICATION.md    # Complete API spec
LOVABLE_QUICK_START.md               # Quick reference
```

---

## 🧪 Test Credentials

### Worker
```
Phone: 9876543210
Password: SecurePass123
```

### Doctor
```
Phone: 9988776655
Password: DoctorPass123
```

(Create these via signup first)

---

## 🎯 Quick Test Flow

1. Start all services: `START_ALL_SERVICES.bat`
2. Open: http://localhost:5173
3. Worker signup → Create patient → Register visit
4. Doctor signup → View queue → Accept consultation
5. Done! ✅

---

**That's it! You're ready to go! 🚀**
