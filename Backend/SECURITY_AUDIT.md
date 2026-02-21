# Security Audit Report - NeoSure ANC System

## 🔒 Current Security Status

### ✅ What IS Protected (Currently Implemented)

#### 1. Password Security
- **Status**: ✅ PROTECTED
- **Method**: BCrypt hashing with strength 12
- **Details**: 
  - Passwords are NEVER stored in plain text
  - One-way hashing (cannot be reversed)
  - Salt automatically added by BCrypt
  - Stored in `password_hash` column
- **Location**: `AncWorkerEntity.passwordHash`

#### 2. JWT Token Security
- **Status**: ✅ PROTECTED
- **Method**: HMAC-SHA256 signing
- **Details**:
  - Tokens are cryptographically signed
  - Cannot be tampered with
  - 24-hour expiration
  - Contains workerId and phone claims
- **Location**: `JwtService.java`

#### 3. Authentication & Authorization
- **Status**: ✅ PROTECTED
- **Method**: Spring Security + JWT
- **Details**:
  - All endpoints except signup/login require authentication
  - Stateless session management
  - JWT validation on every request
  - Data isolation (workers only see their own patients)
- **Location**: `SecurityConfig.java`, `JwtAuthenticationFilter.java`

#### 4. API Communication (Internal)
- **Status**: ⚠️ PARTIALLY PROTECTED
- **Method**: HTTP (not HTTPS)
- **Details**:
  - Spring Boot ↔ FastAPI: Plain HTTP (localhost only)
  - Client ↔ Spring Boot: Plain HTTP (should be HTTPS in production)

---

### ❌ What is NOT Protected (Security Gaps)

#### 1. Database Data at Rest
- **Status**: ❌ NOT ENCRYPTED
- **Risk**: HIGH
- **Details**:
  - Patient names, addresses, phone numbers stored in plain text
  - Medical data (Hb, BP, symptoms) stored in plain text
  - ANC visit records stored in plain text
  - If database is compromised, all data is readable
- **Affected Tables**: `patients`, `anc_visits`, `anc_workers`

#### 2. Database Connection
- **Status**: ❌ NOT ENCRYPTED
- **Risk**: MEDIUM
- **Details**:
  - PostgreSQL connection uses plain text protocol
  - Database password in `application.yml` is plain text
  - Network traffic between app and database is unencrypted
- **Location**: `application.yml`

#### 3. Sensitive Configuration
- **Status**: ❌ NOT ENCRYPTED
- **Risk**: HIGH
- **Details**:
  - Database password: `ayushman@2004` (plain text in config)
  - JWT secret key: plain text in config
  - OpenAI API key: plain text in config
  - FastAPI key: plain text in config
- **Location**: `application.yml`, `config.py`

#### 4. API Keys in Transit
- **Status**: ❌ NOT ENCRYPTED
- **Risk**: HIGH
- **Details**:
  - OpenAI API key sent over internet (but HTTPS to OpenAI)
  - FastAPI communication over HTTP (localhost)
- **Location**: `controlled_generator.py`

#### 5. Logging
- **Status**: ❌ POTENTIALLY LEAKING DATA
- **Risk**: MEDIUM
- **Details**:
  - SQL queries logged (may contain sensitive data)
  - Debug logs may contain patient information
  - Logs stored in plain text files
- **Location**: `application.yml` (show-sql: true)

#### 6. CORS Configuration
- **Status**: ⚠️ TOO PERMISSIVE
- **Risk**: MEDIUM
- **Details**:
  - Allows ALL origins (`*`)
  - Should be restricted to specific domains in production
- **Location**: `SecurityConfig.java`

---

## 🚨 Critical Security Risks

### Risk Level: HIGH

1. **Sensitive Patient Data in Plain Text**
   - Patient names, addresses, phone numbers
   - Medical records (Hb, BP, symptoms)
   - Pregnancy details
   - **Impact**: HIPAA/data privacy violation if breached

2. **Database Credentials Exposed**
   - Password in plain text config file
   - Anyone with file access can read database
   - **Impact**: Complete database compromise

3. **API Keys Exposed**
   - OpenAI API key in plain text
   - Could be used by unauthorized parties
   - **Impact**: Financial loss, API abuse

### Risk Level: MEDIUM

4. **Unencrypted Database Connection**
   - Data transmitted in plain text
   - **Impact**: Network sniffing could expose data

5. **Overly Permissive CORS**
   - Any website can call your API
   - **Impact**: CSRF attacks, unauthorized access

6. **Sensitive Data in Logs**
   - SQL queries logged with patient data
   - **Impact**: Log files contain sensitive information

---

## 🛡️ Recommended Security Enhancements

### Priority 1: CRITICAL (Implement Immediately)

#### 1. Encrypt Sensitive Database Columns

**What to encrypt**:
- Patient names
- Phone numbers
- Addresses
- Medical data (if required by regulations)

**Implementation**: Use JPA AttributeConverter with AES-256

```java
@Converter
public class StringEncryptor implements AttributeConverter<String, String> {
    private static final String ALGORITHM = "AES/GCM/NoPadding";
    private static final String SECRET_KEY = System.getenv("DB_ENCRYPTION_KEY");
    
    @Override
    public String convertToDatabaseColumn(String attribute) {
        // Encrypt before storing
        return encrypt(attribute);
    }
    
    @Override
    public String convertToEntityAttribute(String dbData) {
        // Decrypt when reading
        return decrypt(dbData);
    }
}
```

Apply to sensitive fields:
```java
@Convert(converter = StringEncryptor.class)
@Column(name = "full_name")
private String fullName;
```

#### 2. Move Secrets to Environment Variables

**Current** (application.yml):
```yaml
datasource:
  password: ayushman@2004  # ❌ EXPOSED
jwt:
  secret: anc-service-jwt-secret-key...  # ❌ EXPOSED
```

**Recommended** (application.yml):
```yaml
datasource:
  password: ${DB_PASSWORD}  # ✅ From environment
jwt:
  secret: ${JWT_SECRET}  # ✅ From environment
```

Set environment variables:
```bash
export DB_PASSWORD=ayushman@2004
export JWT_SECRET=anc-service-jwt-secret-key...
export OPENAI_API_KEY=sk-proj-...
```

#### 3. Enable SSL/TLS for Database Connection

**Update** (application.yml):
```yaml
datasource:
  url: jdbc:postgresql://localhost:5432/NeoSure?ssl=true&sslmode=require
```

Configure PostgreSQL to use SSL certificates.

### Priority 2: HIGH (Implement Soon)

#### 4. Enable HTTPS for Spring Boot

Add SSL certificate:
```yaml
server:
  port: 8443
  ssl:
    enabled: true
    key-store: classpath:keystore.p12
    key-store-password: ${KEYSTORE_PASSWORD}
    key-store-type: PKCS12
```

#### 5. Restrict CORS Origins

```java
configuration.setAllowedOrigins(List.of(
    "https://yourdomain.com",
    "https://app.yourdomain.com"
));
```

#### 6. Disable SQL Logging in Production

```yaml
logging:
  level:
    org.hibernate.SQL: WARN  # Don't log SQL queries
```

### Priority 3: MEDIUM (Implement Later)

#### 7. Add Rate Limiting

Prevent brute force attacks:
```java
@Bean
public RateLimiter rateLimiter() {
    return RateLimiter.create(100); // 100 requests per second
}
```

#### 8. Add Audit Logging

Log all data access:
```java
@Entity
@EntityListeners(AuditingEntityListener.class)
public class PatientEntity {
    @CreatedBy
    private String createdBy;
    
    @LastModifiedBy
    private String lastModifiedBy;
}
```

#### 9. Implement Data Masking

Mask sensitive data in responses:
```java
@JsonProperty(access = JsonProperty.Access.WRITE_ONLY)
private String phone;  // Only accept, never return
```

#### 10. Add Security Headers

```java
http.headers()
    .contentSecurityPolicy("default-src 'self'")
    .xssProtection()
    .frameOptions().deny()
    .httpStrictTransportSecurity();
```

---

## 📋 Implementation Checklist

### Immediate Actions (This Week)

- [ ] Move database password to environment variable
- [ ] Move JWT secret to environment variable
- [ ] Move OpenAI API key to environment variable
- [ ] Restrict CORS to specific origins
- [ ] Disable SQL logging in production
- [ ] Add HTTPS support for Spring Boot

### Short-term Actions (This Month)

- [ ] Implement database column encryption for sensitive fields
- [ ] Enable SSL for PostgreSQL connection
- [ ] Add rate limiting for authentication endpoints
- [ ] Implement audit logging
- [ ] Add security headers

### Long-term Actions (Next Quarter)

- [ ] Implement data masking for API responses
- [ ] Add intrusion detection
- [ ] Implement automated security scanning
- [ ] Add data retention policies
- [ ] Implement backup encryption

---

## 🔐 Encryption Summary

### Currently Encrypted:
1. ✅ Passwords (BCrypt)
2. ✅ JWT tokens (HMAC-SHA256 signed)

### NOT Encrypted (Needs Implementation):
1. ❌ Patient personal data (names, addresses, phones)
2. ❌ Medical records (Hb, BP, symptoms)
3. ❌ Database connection
4. ❌ Configuration secrets
5. ❌ Log files

---

## 💰 Cost of Implementation

### Free (No Cost):
- Environment variables
- CORS restrictions
- Disable SQL logging
- Security headers

### Low Cost (<$100):
- SSL certificates (Let's Encrypt is free)
- Database encryption (code changes only)

### Medium Cost ($100-$500):
- Security audit tools
- Penetration testing

---

## 📊 Compliance Status

### HIPAA Compliance:
- ❌ **NOT COMPLIANT** - Patient data not encrypted at rest
- ❌ **NOT COMPLIANT** - Audit logging not implemented
- ⚠️ **PARTIAL** - Access controls implemented (JWT)

### GDPR Compliance:
- ❌ **NOT COMPLIANT** - No data encryption
- ❌ **NOT COMPLIANT** - No data retention policies
- ⚠️ **PARTIAL** - Access controls implemented

### Indian IT Act 2000:
- ❌ **NOT COMPLIANT** - Sensitive personal data not protected
- ⚠️ **PARTIAL** - Authentication implemented

---

## 🎯 Recommended Priority

**Phase 1 (Week 1)**: Environment variables + CORS + HTTPS
**Phase 2 (Week 2-3)**: Database encryption + SSL connection
**Phase 3 (Month 2)**: Audit logging + Rate limiting
**Phase 4 (Month 3)**: Security headers + Data masking

---

## 📞 Need Help?

For implementing these security measures:
1. Database encryption: Use Jasypt or custom AttributeConverter
2. SSL certificates: Use Let's Encrypt (free)
3. Environment variables: Use Spring Boot profiles
4. Security audit: Use OWASP ZAP or Burp Suite

---

## ⚠️ IMPORTANT DISCLAIMER

**Your system currently has SIGNIFICANT security gaps.**

For production deployment with real patient data:
1. **MUST** implement database encryption
2. **MUST** use environment variables for secrets
3. **MUST** enable HTTPS
4. **MUST** enable database SSL
5. **MUST** restrict CORS
6. **MUST** comply with healthcare data regulations

**DO NOT deploy to production without addressing Priority 1 items!**

---

## 📝 Summary

**Current Security Score**: 4/10

**Strengths**:
- ✅ Password hashing (BCrypt)
- ✅ JWT authentication
- ✅ Data isolation

**Critical Weaknesses**:
- ❌ No data encryption at rest
- ❌ Secrets in plain text
- ❌ No database connection encryption
- ❌ Overly permissive CORS

**Recommendation**: Implement Priority 1 security enhancements before production deployment.
