# H2 Database Setup Complete ✅

## Summary

Successfully configured Spring Boot ANC Service to use H2 in-memory database instead of PostgreSQL.

## Changes Made

### 1. Added H2 Dependency
**File:** `Backend/pom.xml`
```xml
<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>runtime</scope>
</dependency>
```

### 2. Updated Database Configuration
**File:** `Backend/src/main/resources/application.yml`

```yaml
spring:
  datasource:
    url: jdbc:h2:mem:ancdb
    driver-class-name: org.h2.Driver
    username: sa
    password: 
    
  h2:
    console:
      enabled: true
      path: /h2-console
      
  sql:
    init:
      mode: never  # Disable schema.sql execution
      
  jpa:
    hibernate:
      ddl-auto: create-drop  # Auto-create tables
    properties:
      hibernate:
        dialect: org.hibernate.dialect.H2Dialect
```

### 3. Fixed Entity JSON Columns
**File:** `Backend/src/main/java/com/anc/entity/AncVisitEntity.java`

Changed from PostgreSQL `jsonb` to H2-compatible `JSON`:
- `structured_data`: `jsonb` → `JSON`
- `detected_risks`: `jsonb` → `JSON`
- `visit_metadata`: `jsonb` → `JSON`

## Application Status

✅ **Spring Boot Application Running**
- Port: 8080
- Database: H2 in-memory (jdbc:h2:mem:ancdb)
- Status: Started successfully
- Tables: Auto-created by Hibernate

## Access Points

### 1. REST API
```bash
# Base URL
http://localhost:8080/api/anc

# Endpoints
GET  /api/anc/visits/high-risk
GET  /api/anc/visits/critical
GET  /api/anc/visits/risk-level/{level}
GET  /api/anc/visits/{visitId}
GET  /api/anc/patients/{patientId}/visits
POST /api/anc/register-visit
```

### 2. H2 Console (Database UI)
```
URL: http://localhost:8080/h2-console
JDBC URL: jdbc:h2:mem:ancdb
Username: sa
Password: (leave empty)
```

## Test the Application

### 1. Check High-Risk Visits (Empty Initially)
```bash
curl http://localhost:8080/api/anc/visits/high-risk
```

**Response:**
```json
[]
```

### 2. Register a Visit
```bash
curl -X POST http://localhost:8080/api/anc/register-visit \
  -H "Content-Type: application/json" \
  -d @Backend/test-payload.json
```

## Next Steps

### 1. Start FastAPI Server
```bash
cd "Medical RAG Pipeline"
python api_server.py
```

### 2. Test Complete Integration
Follow the guide in `Backend/TEST_INTEGRATION.md`

### 3. View Data in H2 Console
1. Open browser: http://localhost:8080/h2-console
2. Enter connection details:
   - JDBC URL: `jdbc:h2:mem:ancdb`
   - Username: `sa`
   - Password: (empty)
3. Click "Connect"
4. Run SQL queries:
   ```sql
   SELECT * FROM anc_visits;
   ```

## Advantages of H2

✅ **No Installation Required**
- Embedded database, no separate server needed
- No password configuration issues

✅ **Fast Development**
- In-memory database (very fast)
- Auto-creates tables on startup
- Resets on restart (clean slate)

✅ **Built-in Console**
- Web-based database viewer
- Run SQL queries directly
- Inspect data easily

✅ **Easy Testing**
- Perfect for development and testing
- No data persistence concerns
- Quick iterations

## Switching Back to PostgreSQL (Optional)

If you want to use PostgreSQL later:

1. Update `application.yml`:
```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/anc_db
    username: postgres
    password: your_password
    driver-class-name: org.postgresql.Driver
    
  jpa:
    hibernate:
      ddl-auto: update
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
```

2. Update entity JSON columns back to `jsonb`:
```java
@Column(name = "structured_data", columnDefinition = "jsonb")
```

3. Create PostgreSQL database:
```sql
CREATE DATABASE anc_db;
```

## Important Notes

⚠️ **Data is NOT Persistent**
- H2 in-memory database resets on application restart
- All data is lost when you stop the application
- Perfect for testing, not for production

⚠️ **For Production**
- Use PostgreSQL or another persistent database
- Configure proper backups
- Use `ddl-auto: validate` instead of `create-drop`

## Troubleshooting

### Port 8080 Already in Use
```bash
# Find process using port 8080
netstat -ano | findstr :8080

# Kill the process (replace PID)
taskkill /F /PID <PID>
```

### Application Won't Start
```bash
# Clean and rebuild
cd Backend
mvn clean compile
mvn spring-boot:run
```

### Can't Access H2 Console
- Ensure application is running
- Check URL: http://localhost:8080/h2-console
- Verify JDBC URL: jdbc:h2:mem:ancdb

---

**Setup Version:** 1.0.0  
**Date:** February 21, 2026  
**Status:** ✅ Complete and Running
