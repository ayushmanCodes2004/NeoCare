# ✅ Minimal API Tester UI Ready!

## 🚀 Access the API Tester

After restarting the backend, access the minimal UI at:

```
http://localhost:8080/api-tester.html
```

## 🎯 Features

- **Clean, minimal interface** - No clutter, just API testing
- **Pre-filled examples** - All requests have sample data
- **Auto token management** - Token auto-fills after login
- **Color-coded methods** - POST (green), GET (blue), PUT (orange)
- **Response display** - JSON formatted with status codes
- **No dependencies** - Pure HTML/CSS/JS

## 📋 Available Endpoints

### Worker Authentication
- ✅ POST /api/auth/signup - Register worker
- ✅ POST /api/auth/login - Worker login (token auto-fills)

### Doctor Authentication  
- ✅ POST /api/doctor/auth/signup - Register doctor
- ✅ POST /api/doctor/auth/login - Doctor login (token auto-fills)

### Patient Management
- ✅ POST /api/patients - Create patient
- ✅ GET /api/patients - List patients

### Consultations
- ✅ GET /api/consultations/queue - Doctor's queue

## 🔄 Workflow

1. **Sign up** a worker or doctor
2. **Login** - Token automatically fills in the token field
3. **Test protected endpoints** - Token is sent automatically
4. **View responses** - JSON formatted with status codes

## 🎨 UI Design

- Warm terracotta theme matching your landing page
- Card-based layout
- Syntax-highlighted JSON
- Status badges (success/error)
- Responsive design

## 🆚 Swagger vs API Tester

| Feature | Swagger UI | API Tester |
|---------|-----------|------------|
| Documentation | ✅ Full | ❌ Minimal |
| Schema validation | ✅ Yes | ❌ No |
| Try it out | ✅ Yes | ✅ Yes |
| UI Complexity | Complex | Simple |
| Load time | Slower | Instant |
| Customization | Limited | Easy |

## 📝 Usage Example

1. Go to http://localhost:8080/api-tester.html
2. Click "Send Request" on Worker Signup
3. Click "Send Request" on Worker Login
4. Token auto-fills at the top
5. Click "Send Request" on Create Patient
6. See the response!

---

**Both UIs are available:**
- Swagger UI: http://localhost:8080/swagger-ui/index.html
- API Tester: http://localhost:8080/api-tester.html
