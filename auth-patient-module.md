# ANC Worker Authentication Module
## JWT Auth + Spring Security — Complete Implementation

**Package:** `com.anc` | **Auth:** JWT (JJWT 0.12.3) + Spring Security 6

---

## What This Builds

```
┌─────────────────────────────────────────────────────────────────┐
│                        FULL AUTH FLOW                           │
│                                                                 │
│  POST /api/auth/signup  →  Create worker account  →  JWT       │
│  POST /api/auth/login   →  Verify credentials    →  JWT        │
│                                                                 │
│  React stores JWT in localStorage                               │
│  Sends every request with: Authorization: Bearer <token>        │
│                                                                 │
│  JwtAuthFilter intercepts → validates token → sets worker       │
│  in SecurityContext → Controller gets worker via               │
│  @AuthenticationPrincipal                                       │
│                                                                 │
│  Worker can then:                                               │
│    POST /api/patients          → register patient               │
│    GET  /api/patients          → see their patient list         │
│    GET  /api/patients/{id}     → view one patient               │
│    POST /api/anc/register-visit → submit ANC visit → FastAPI   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Full Project Structure After This Module

```
com.anc/
│
├── AncServiceApplication.java
│
├── config/
│   ├── RestTemplateConfig.java          (existing)
│   └── JacksonConfig.java               (existing)
│
├── security/                            ← NEW package
│   ├── SecurityConfig.java              ← Spring Security filter chain + BCrypt
│   ├── JwtAuthFilter.java               ← OncePerRequestFilter — validates JWT
│   └── CustomUserDetailsService.java    ← loads worker by phone from DB
│
├── controller/
│   ├── AncVisitController.java          (existing — now protected by JWT)
│   ├── AuthController.java              ← NEW: /signup, /login, /me
│   └── PatientController.java           ← NEW: /patients CRUD
│
├── service/
│   ├── AncVisitService.java             (existing)
│   ├── ClinicalSummaryBuilder.java      (existing)
│   ├── JwtService.java                  ← NEW: generate + parse + validate JWT
│   ├── AuthService.java                 ← NEW: signup + login business logic
│   └── PatientService.java              ← NEW: patient CRUD
│
├── entity/
│   ├── AncVisitEntity.java              (existing)
│   ├── AncWorkerEntity.java             ← NEW: implements UserDetails
│   └── PatientEntity.java               ← NEW: patient record
│
├── repository/
│   ├── AncVisitRepository.java          (existing)
│   ├── AncWorkerRepository.java         ← NEW
│   └── PatientRepository.java           ← NEW
│
├── dto/
│   ├── (all existing ANC visit DTOs)    (existing)
│   ├── WorkerSignupRequestDTO.java      ← NEW
│   ├── WorkerLoginRequestDTO.java       ← NEW
│   ├── AuthResponseDTO.java             ← NEW
│   ├── PatientCreateRequestDTO.java     ← NEW
│   └── PatientResponseDTO.java          ← NEW
│
└── exception/
    ├── FastApiException.java            (existing)
    └── GlobalExceptionHandler.java      (existing — add new auth handlers)

resources/
├── application.yml                      ← UPDATE: add jwt config
└── schema.sql                           ← UPDATE: add new tables
```

---

## API Endpoints

| Method | URL | Auth Required | Description |
|--------|-----|:---:|-------------|
| POST | `/api/auth/signup` | ❌ | Register new ANC worker |
| POST | `/api/auth/login` | ❌ | Login, returns JWT |
| GET | `/api/auth/me` | ✅ JWT | Get logged-in worker's profile |
| POST | `/api/patients` | ✅ JWT | Create new patient |
| GET | `/api/patients` | ✅ JWT | List this worker's patients |
| GET | `/api/patients/{patientId}` | ✅ JWT | Get one patient |
| POST | `/api/anc/register-visit` | ✅ JWT | Submit ANC visit → FastAPI |
| GET | `/api/anc/patients/{id}/visits` | ✅ JWT | Visit history |
| GET | `/api/anc/visits/high-risk` | ✅ JWT | All high risk visits |
| GET | `/api/anc/visits/critical` | ✅ JWT | All critical visits |

---

## Signup + Login JSON

**Signup request:**
```json
{
  "fullName": "Anjali Devi",
  "phone": "9876543210",
  "email": "anjali@phc.in",
  "password": "StrongPassword123",
  "healthCenter": "PHC Angondhalli",
  "district": "Bangalore Rural"
}
```

**Login request:**
```json
{
  "phone": "9876543210",
  "password": "StrongPassword123"
}
```

**Auth response (both signup and login):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwid29ya2VySWQiOiJ1dWlkLWhlcmUiLCJpYXQiOjE3MDAwMDAwMDAsImV4cCI6MTcwMDA4NjQwMH0.signature",
  "workerId": "550e8400-e29b-41d4-a716-446655440000",
  "fullName": "Anjali Devi",
  "phone": "9876543210",
  "email": "anjali@phc.in",
  "healthCenter": "PHC Angondhalli",
  "district": "Bangalore Rural",
  "message": "Login successful"
}
```

---

## pom.xml — Add These Dependencies

```xml
<!-- Add to existing pom.xml <dependencies> section -->

<!-- Spring Security -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>

<!-- JJWT API -->
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-api</artifactId>
    <version>0.12.3</version>
</dependency>

<!-- JJWT implementation (runtime only) -->
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-impl</artifactId>
    <version>0.12.3</version>
    <scope>runtime</scope>
</dependency>

<!-- JJWT Jackson support (runtime only) -->
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-jackson</artifactId>
    <version>0.12.3</version>
    <scope>runtime</scope>
</dependency>
```

---

## application.yml — Add JWT Config

```yaml
# Add to existing application.yml

jwt:
  # Must be at least 32 characters. Change this in production!
  secret: "anc-service-secret-key-2026-change-in-production-min-32-chars"
  # Token validity: 86400000 ms = 24 hours
  expiration: 86400000
```

---

## schema.sql — Add New Tables

```sql
-- ─── ANC Worker accounts ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS anc_workers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name       VARCHAR(255)    NOT NULL,
    phone           VARCHAR(15)     NOT NULL UNIQUE,   -- login username
    email           VARCHAR(255)    UNIQUE,
    password_hash   VARCHAR(255)    NOT NULL,           -- BCrypt
    health_center   VARCHAR(255),
    district        VARCHAR(255),
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_worker_phone    ON anc_workers(phone);
CREATE INDEX        idx_worker_district ON anc_workers(district);

-- ─── Patient records (owned by an ANC worker) ────────────────────────────────
CREATE TABLE IF NOT EXISTS patients (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    worker_id       VARCHAR(255)    NOT NULL,           -- FK to anc_workers.id
    full_name       VARCHAR(255)    NOT NULL,
    phone           VARCHAR(15),
    age             INTEGER,
    address         TEXT,
    village         VARCHAR(255),
    district        VARCHAR(255),
    lmp_date        DATE,                               -- Last Menstrual Period
    edd_date        DATE,                               -- Estimated Due Date
    blood_group     VARCHAR(10),
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_patient_worker_id  ON patients(worker_id);
CREATE INDEX idx_patient_phone      ON patients(phone);
CREATE INDEX idx_patient_district   ON patients(district);

-- ─── NOTE: existing anc_visits table already has patient_id and worker_id ────
-- No changes needed to anc_visits.
```

---

## entity/AncWorkerEntity.java

```java
package com.anc.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.time.LocalDateTime;
import java.util.Collection;
import java.util.List;

/**
 * ANC Worker account entity.
 *
 * Implements Spring Security's UserDetails so this entity can be used
 * directly throughout the security layer without any adapters.
 *
 * Login identifier: phone number (unique across all workers)
 * Password:         BCrypt hashed, stored in password_hash column
 *
 * When @AuthenticationPrincipal is used in a controller, Spring injects
 * this entity directly — no extra lookup needed.
 */
@Entity
@Table(name = "anc_workers")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AncWorkerEntity implements UserDetails {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id", updatable = false, nullable = false)
    private String id;

    @Column(name = "full_name", nullable = false)
    private String fullName;

    /**
     * Phone is the unique login identifier.
     * Validated as a 10-digit Indian mobile number in the DTO.
     */
    @Column(name = "phone", nullable = false, unique = true, length = 15)
    private String phone;

    @Column(name = "email", unique = true)
    private String email;

    /**
     * BCrypt-hashed password.
     * The raw password from the request is NEVER stored here.
     */
    @Column(name = "password_hash", nullable = false)
    private String passwordHash;

    @Column(name = "health_center")
    private String healthCenter;

    @Column(name = "district")
    private String district;

    /**
     * Set to false to block a worker without deleting their records.
     * isAccountNonLocked() returns false when this is false.
     */
    @Column(name = "is_active")
    @Builder.Default
    private Boolean isActive = true;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    // ─── UserDetails interface ────────────────────────────────────────────────

    /**
     * No roles implemented yet. Add "ROLE_WORKER", "ROLE_SUPERVISOR" etc here
     * when role-based access control is needed.
     */
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return List.of();
    }

    /** Spring Security calls getPassword() to compare against the submitted password */
    @Override
    public String getPassword() {
        return passwordHash;
    }

    /** Spring Security uses phone as the username (principal name) */
    @Override
    public String getUsername() {
        return phone;
    }

    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    /** Returns false when is_active = false — blocks the worker from logging in */
    @Override
    public boolean isAccountNonLocked() {
        return Boolean.TRUE.equals(isActive);
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    @Override
    public boolean isEnabled() {
        return Boolean.TRUE.equals(isActive);
    }
}
```

---

## entity/PatientEntity.java

```java
package com.anc.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * Patient record created and owned by an ANC worker.
 *
 * Relationship:
 *   One AncWorkerEntity → many PatientEntity (via worker_id)
 *   One PatientEntity   → many AncVisitEntity (via patient_id in anc_visits)
 *
 * worker_id is stored as a plain String (not a JPA @ManyToOne join)
 * so that we avoid lazy-loading issues in REST responses.
 */
@Entity
@Table(name = "patients")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PatientEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id", updatable = false, nullable = false)
    private String id;

    /** UUID of the ANC worker who registered this patient */
    @Column(name = "worker_id", nullable = false)
    private String workerId;

    @Column(name = "full_name", nullable = false)
    private String fullName;

    @Column(name = "phone", length = 15)
    private String phone;

    @Column(name = "age")
    private Integer age;

    @Column(name = "address", columnDefinition = "TEXT")
    private String address;

    @Column(name = "village")
    private String village;

    @Column(name = "district")
    private String district;

    /** Last Menstrual Period — used to calculate current gestational age */
    @Column(name = "lmp_date")
    private LocalDate lmpDate;

    /** Estimated Due Date */
    @Column(name = "edd_date")
    private LocalDate eddDate;

    @Column(name = "blood_group", length = 10)
    private String bloodGroup;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
```

---

## repository/AncWorkerRepository.java

```java
package com.anc.repository;

import com.anc.entity.AncWorkerEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * Data access for ANC worker accounts.
 *
 * Primary query is findByPhone — used in:
 *   - CustomUserDetailsService (Spring Security authentication)
 *   - AuthService.login() (to load worker after successful auth)
 *   - JwtAuthFilter (indirectly via CustomUserDetailsService)
 */
@Repository
public interface AncWorkerRepository extends JpaRepository<AncWorkerEntity, String> {

    /**
     * Load worker by phone number.
     * Called by Spring Security during every authenticated request.
     */
    Optional<AncWorkerEntity> findByPhone(String phone);

    /**
     * Pre-check during signup to return a helpful error
     * before hitting the DB unique constraint.
     */
    boolean existsByPhone(String phone);

    /** Pre-check email uniqueness during signup */
    boolean existsByEmail(String email);
}
```

---

## repository/PatientRepository.java

```java
package com.anc.repository;

import com.anc.entity.PatientEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Data access for patient records.
 * All queries are scoped by workerId to enforce data isolation —
 * a worker can only see and manage their own patients.
 */
@Repository
public interface PatientRepository extends JpaRepository<PatientEntity, String> {

    /**
     * Fetch all patients for a specific worker, newest first.
     * Used by GET /api/patients (worker's own patient list).
     */
    List<PatientEntity> findByWorkerIdOrderByCreatedAtDesc(String workerId);

    /**
     * Find a patient by phone within a specific worker's patients.
     * Used to prevent duplicate patient registration.
     */
    Optional<PatientEntity> findByPhoneAndWorkerId(String phone, String workerId);

    /** Dashboard stat: how many patients has this worker registered */
    long countByWorkerId(String workerId);
}
```

---

## service/JwtService.java

```java
package com.anc.service;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.MalformedJwtException;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.UnsupportedJwtException;
import io.jsonwebtoken.security.Keys;
import io.jsonwebtoken.security.SignatureException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Service;

import java.security.Key;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Function;

/**
 * Handles all JWT operations:
 *   - generateToken()   → called after successful signup/login
 *   - isTokenValid()    → called by JwtAuthFilter on every request
 *   - extractPhone()    → get the username (phone) from token subject
 *   - extractWorkerId() → get workerId from token custom claims
 *
 * Token structure:
 * {
 *   "sub": "9876543210",           ← phone number (username)
 *   "workerId": "uuid-here",       ← custom claim
 *   "iat": 1700000000,             ← issued at (epoch seconds)
 *   "exp": 1700086400              ← expires at (iat + 24h)
 * }
 */
@Slf4j
@Service
public class JwtService {

    @Value("${jwt.secret}")
    private String secretKey;

    @Value("${jwt.expiration:86400000}")
    private long jwtExpiration;

    // ─── Token generation ─────────────────────────────────────────────────────

    /**
     * Generate a signed JWT for a successfully authenticated worker.
     *
     * @param phone    the worker's phone — becomes the JWT subject
     * @param workerId the worker's UUID — stored as a custom claim
     */
    public String generateToken(String phone, String workerId) {
        Map<String, Object> extraClaims = new HashMap<>();
        extraClaims.put("workerId", workerId);
        return buildToken(extraClaims, phone);
    }

    private String buildToken(Map<String, Object> extraClaims, String subject) {
        return Jwts.builder()
                .setClaims(extraClaims)
                .setSubject(subject)
                .setIssuedAt(new Date(System.currentTimeMillis()))
                .setExpiration(new Date(System.currentTimeMillis() + jwtExpiration))
                .signWith(getSigningKey(), SignatureAlgorithm.HS256)
                .compact();
    }

    // ─── Token validation ─────────────────────────────────────────────────────

    /**
     * Validates token against the UserDetails loaded from DB.
     * Checks: phone matches + token not expired.
     * Called by JwtAuthFilter on every protected request.
     */
    public boolean isTokenValid(String token, UserDetails userDetails) {
        try {
            final String phone = extractPhone(token);
            return phone.equals(userDetails.getUsername()) && !isTokenExpired(token);
        } catch (ExpiredJwtException e) {
            log.warn("JWT expired: {}", e.getMessage());
            return false;
        } catch (SignatureException e) {
            log.warn("JWT signature invalid: {}", e.getMessage());
            return false;
        } catch (MalformedJwtException e) {
            log.warn("JWT malformed: {}", e.getMessage());
            return false;
        } catch (UnsupportedJwtException e) {
            log.warn("JWT unsupported: {}", e.getMessage());
            return false;
        } catch (Exception e) {
            log.warn("JWT validation error: {}", e.getMessage());
            return false;
        }
    }

    // ─── Claim extraction ─────────────────────────────────────────────────────

    /** Extract phone number from JWT subject */
    public String extractPhone(String token) {
        return extractClaim(token, Claims::getSubject);
    }

    /** Extract workerId from JWT custom claims */
    public String extractWorkerId(String token) {
        return extractClaim(token, claims -> claims.get("workerId", String.class));
    }

    /** Extract token expiry date */
    public Date extractExpiration(String token) {
        return extractClaim(token, Claims::getExpiration);
    }

    private <T> T extractClaim(String token, Function<Claims, T> claimsResolver) {
        final Claims claims = extractAllClaims(token);
        return claimsResolver.apply(claims);
    }

    private Claims extractAllClaims(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(getSigningKey())
                .build()
                .parseClaimsJws(token)
                .getBody();
    }

    private boolean isTokenExpired(String token) {
        return extractExpiration(token).before(new Date());
    }

    /**
     * HMAC-SHA256 signing key.
     * Secret must be at least 32 characters (256 bits) for HS256.
     */
    private Key getSigningKey() {
        byte[] keyBytes = secretKey.getBytes();
        return Keys.hmacShaKeyFor(keyBytes);
    }
}
```

---

## security/CustomUserDetailsService.java

```java
package com.anc.security;

import com.anc.repository.AncWorkerRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

/**
 * Bridges Spring Security with the ANC worker database.
 *
 * Spring Security calls loadUserByUsername(phone) in two places:
 *   1. During login — DaoAuthenticationProvider uses it to verify credentials
 *   2. During JWT filter — JwtAuthFilter calls it to validate the token subject
 *
 * AncWorkerEntity already implements UserDetails, so we return it directly.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class CustomUserDetailsService implements UserDetailsService {

    private final AncWorkerRepository workerRepository;

    /**
     * Load worker by phone number.
     * The "username" here is the phone number — that is our unique login identifier.
     *
     * @param phone the phone number extracted from login request or JWT token
     * @throws UsernameNotFoundException if no worker exists with this phone
     */
    @Override
    public UserDetails loadUserByUsername(String phone) throws UsernameNotFoundException {
        log.debug("Loading worker by phone: {}", phone);
        return workerRepository.findByPhone(phone)
                .orElseThrow(() -> {
                    log.warn("Worker not found for phone: {}", phone);
                    return new UsernameNotFoundException(
                            "No ANC worker registered with phone: " + phone
                    );
                });
    }
}
```

---

## security/JwtAuthFilter.java

```java
package com.anc.security;

import com.anc.service.JwtService;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.lang.NonNull;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

/**
 * JWT Authentication Filter — runs once per request.
 *
 * HOW IT WORKS:
 *   1. Read "Authorization: Bearer <token>" header
 *   2. Extract phone number from JWT subject
 *   3. Load worker from DB via CustomUserDetailsService
 *   4. Validate token (signature + expiry + phone match)
 *   5. If valid → set UsernamePasswordAuthenticationToken in SecurityContext
 *      This makes the worker available via @AuthenticationPrincipal in controllers
 *
 * If token is missing, expired, or invalid → do nothing.
 * Spring Security will reject the request at the endpoint level.
 *
 * Skipped for public endpoints (/api/auth/signup, /api/auth/login)
 * because SecurityConfig.permitAll() skips auth for those paths.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class JwtAuthFilter extends OncePerRequestFilter {

    private final JwtService jwtService;
    private final CustomUserDetailsService userDetailsService;

    @Override
    protected void doFilterInternal(
            @NonNull HttpServletRequest request,
            @NonNull HttpServletResponse response,
            @NonNull FilterChain filterChain
    ) throws ServletException, IOException {

        final String authHeader = request.getHeader("Authorization");

        // ── Step 1: Check header exists and has Bearer prefix ─────────────
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            log.debug("No Bearer token found for: {} {}", request.getMethod(), request.getRequestURI());
            filterChain.doFilter(request, response);
            return;
        }

        // ── Step 2: Extract JWT from header ──────────────────────────────
        final String jwt = authHeader.substring(7);  // Remove "Bearer " prefix

        try {
            // ── Step 3: Extract phone from JWT subject ────────────────────
            final String phone = jwtService.extractPhone(jwt);

            // ── Step 4: Only proceed if phone found and not already authenticated
            if (phone != null && SecurityContextHolder.getContext().getAuthentication() == null) {

                // ── Step 5: Load worker from DB ───────────────────────────
                UserDetails userDetails = userDetailsService.loadUserByUsername(phone);

                // ── Step 6: Validate token ────────────────────────────────
                if (jwtService.isTokenValid(jwt, userDetails)) {

                    // ── Step 7: Create auth token and set in SecurityContext
                    UsernamePasswordAuthenticationToken authToken =
                            new UsernamePasswordAuthenticationToken(
                                    userDetails,          // principal — AncWorkerEntity
                                    null,                 // credentials — null after auth
                                    userDetails.getAuthorities()
                            );
                    authToken.setDetails(
                            new WebAuthenticationDetailsSource().buildDetails(request)
                    );
                    SecurityContextHolder.getContext().setAuthentication(authToken);

                    log.debug("JWT authenticated: phone={}, URI={}", phone, request.getRequestURI());
                } else {
                    log.warn("JWT validation failed for phone: {}", phone);
                }
            }

        } catch (Exception e) {
            // Log and continue — Spring Security will reject unauthenticated access
            log.error("JWT filter error for URI {}: {}", request.getRequestURI(), e.getMessage());
        }

        filterChain.doFilter(request, response);
    }
}
```

---

## security/SecurityConfig.java

```java
package com.anc.security;

import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

/**
 * Spring Security configuration for the ANC service.
 *
 * KEY DECISIONS:
 *   - STATELESS sessions (no server-side session, JWT carries all state)
 *   - CSRF disabled (not needed for stateless REST APIs)
 *   - BCrypt strength 12 for password hashing
 *   - Public routes: /api/auth/signup and /api/auth/login only
 *   - All other routes: require valid JWT
 *   - JwtAuthFilter runs BEFORE UsernamePasswordAuthenticationFilter
 *
 * AUTHENTICATION FLOW:
 *   Login → DaoAuthenticationProvider.authenticate()
 *         → CustomUserDetailsService.loadUserByUsername(phone)
 *         → BCrypt.matches(rawPassword, hashedPassword)
 *         → If match: return authenticated token
 *         → If not:   throw BadCredentialsException
 */
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthFilter jwtAuthFilter;
    private final CustomUserDetailsService customUserDetailsService;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            // Disable CSRF — not needed for stateless JWT REST APIs
            .csrf(AbstractHttpConfigurer::disable)

            // Authorization rules
            .authorizeHttpRequests(auth -> auth
                // Public — no token needed
                .requestMatchers("/api/auth/signup").permitAll()
                .requestMatchers("/api/auth/login").permitAll()
                // Everything else needs a valid JWT
                .anyRequest().authenticated()
            )

            // Stateless — no HttpSession, JWT carries all state
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )

            // Use our DaoAuthenticationProvider (phone + BCrypt)
            .authenticationProvider(authenticationProvider())

            // Run JWT filter BEFORE Spring's default username/password filter
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    /**
     * Wires CustomUserDetailsService + BCryptPasswordEncoder into
     * Spring Security's authentication mechanism.
     * Used by AuthenticationManager during login.
     */
    @Bean
    public AuthenticationProvider authenticationProvider() {
        DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
        provider.setUserDetailsService(customUserDetailsService);
        provider.setPasswordEncoder(passwordEncoder());
        return provider;
    }

    /**
     * AuthenticationManager is used by AuthService.login() to trigger
     * the full authentication flow (load user → compare password → throw on failure).
     */
    @Bean
    public AuthenticationManager authenticationManager(
            AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }

    /**
     * BCrypt with strength 12.
     * Strength 12 = ~250ms hash time on modern hardware — good balance
     * of security vs performance for a healthcare application.
     */
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12);
    }
}
```

---

## dto/WorkerSignupRequestDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * Signup request body from React:
 *
 * {
 *   "fullName":     "Anjali Devi",
 *   "phone":        "9876543210",
 *   "email":        "anjali@phc.in",
 *   "password":     "StrongPassword123",
 *   "healthCenter": "PHC Angondhalli",
 *   "district":     "Bangalore Rural"
 * }
 */
@Data
public class WorkerSignupRequestDTO {

    @NotBlank(message = "Full name is required")
    @JsonProperty("fullName")
    private String fullName;

    @NotBlank(message = "Phone number is required")
    @Pattern(
        regexp = "^[6-9]\\d{9}$",
        message = "Enter a valid 10-digit Indian mobile number"
    )
    @JsonProperty("phone")
    private String phone;

    @Email(message = "Enter a valid email address")
    @JsonProperty("email")
    private String email;

    @NotBlank(message = "Password is required")
    @Size(min = 8, message = "Password must be at least 8 characters")
    @JsonProperty("password")
    private String password;

    @NotBlank(message = "Health center name is required")
    @JsonProperty("healthCenter")
    private String healthCenter;

    @NotBlank(message = "District is required")
    @JsonProperty("district")
    private String district;
}
```

---

## dto/WorkerLoginRequestDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.Data;

/**
 * Login request body from React:
 *
 * {
 *   "phone":    "9876543210",
 *   "password": "StrongPassword123"
 * }
 */
@Data
public class WorkerLoginRequestDTO {

    @NotBlank(message = "Phone number is required")
    @Pattern(
        regexp = "^[6-9]\\d{9}$",
        message = "Enter a valid 10-digit Indian mobile number"
    )
    @JsonProperty("phone")
    private String phone;

    @NotBlank(message = "Password is required")
    @JsonProperty("password")
    private String password;
}
```

---

## dto/AuthResponseDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Builder;
import lombok.Data;

/**
 * Response returned to React after signup or login.
 *
 * React should:
 *   1. Store token in localStorage: localStorage.setItem('anc_token', token)
 *   2. Set on every API call: Authorization: Bearer <token>
 *   3. Store workerId, fullName etc for UI display
 */
@Data
@Builder
public class AuthResponseDTO {

    /** JWT — React sends this as Authorization: Bearer <token> */
    @JsonProperty("token")
    private String token;

    @JsonProperty("workerId")
    private String workerId;

    @JsonProperty("fullName")
    private String fullName;

    @JsonProperty("phone")
    private String phone;

    @JsonProperty("email")
    private String email;

    @JsonProperty("healthCenter")
    private String healthCenter;

    @JsonProperty("district")
    private String district;

    /** "Login successful" or "Account created successfully" */
    @JsonProperty("message")
    private String message;
}
```

---

## dto/PatientCreateRequestDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

import java.time.LocalDate;

/**
 * Request body when ANC worker registers a new patient.
 *
 * workerId is NOT included here — it is extracted from the JWT token
 * by @AuthenticationPrincipal in the controller.
 * This prevents a worker from creating patients under another worker's ID.
 */
@Data
public class PatientCreateRequestDTO {

    @NotBlank(message = "Patient full name is required")
    @JsonProperty("fullName")
    private String fullName;

    @JsonProperty("phone")
    private String phone;

    @JsonProperty("age")
    private Integer age;

    @JsonProperty("address")
    private String address;

    @JsonProperty("village")
    private String village;

    @JsonProperty("district")
    private String district;

    /** Last Menstrual Period — format: YYYY-MM-DD */
    @JsonProperty("lmpDate")
    private LocalDate lmpDate;

    /** Estimated Due Date — format: YYYY-MM-DD */
    @JsonProperty("eddDate")
    private LocalDate eddDate;

    @JsonProperty("bloodGroup")
    private String bloodGroup;
}
```

---

## dto/PatientResponseDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Builder;
import lombok.Data;

import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * Patient data returned to React after create or fetch.
 */
@Data
@Builder
public class PatientResponseDTO {

    @JsonProperty("patientId")
    private String patientId;

    @JsonProperty("workerId")
    private String workerId;

    @JsonProperty("fullName")
    private String fullName;

    @JsonProperty("phone")
    private String phone;

    @JsonProperty("age")
    private Integer age;

    @JsonProperty("address")
    private String address;

    @JsonProperty("village")
    private String village;

    @JsonProperty("district")
    private String district;

    @JsonProperty("lmpDate")
    private LocalDate lmpDate;

    @JsonProperty("eddDate")
    private LocalDate eddDate;

    @JsonProperty("bloodGroup")
    private String bloodGroup;

    @JsonProperty("createdAt")
    private LocalDateTime createdAt;
}
```

---

## service/AuthService.java

```java
package com.anc.service;

import com.anc.dto.AuthResponseDTO;
import com.anc.dto.WorkerLoginRequestDTO;
import com.anc.dto.WorkerSignupRequestDTO;
import com.anc.entity.AncWorkerEntity;
import com.anc.repository.AncWorkerRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

/**
 * Business logic for ANC worker authentication.
 *
 * SIGNUP FLOW:
 *   1. Check phone uniqueness (throw if duplicate)
 *   2. Check email uniqueness if provided (throw if duplicate)
 *   3. Hash password with BCrypt
 *   4. Save AncWorkerEntity to DB
 *   5. Generate JWT
 *   6. Return AuthResponseDTO with token + worker info
 *
 * LOGIN FLOW:
 *   1. Call AuthenticationManager.authenticate(phone, rawPassword)
 *      → internally: CustomUserDetailsService.loadUserByUsername(phone)
 *      → internally: BCrypt.matches(rawPassword, storedHash)
 *      → throws BadCredentialsException if wrong — caught by GlobalExceptionHandler
 *   2. If authenticated: load worker from DB
 *   3. Generate JWT
 *   4. Return AuthResponseDTO with token + worker info
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AuthService {

    private final AncWorkerRepository workerRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final AuthenticationManager authenticationManager;

    public AuthResponseDTO signup(WorkerSignupRequestDTO request) {
        log.info("Processing signup for phone: {}", request.getPhone());

        // ── Uniqueness checks ─────────────────────────────────────────────
        if (workerRepository.existsByPhone(request.getPhone())) {
            throw new RuntimeException(
                "Phone number already registered. Please login instead."
            );
        }

        if (request.getEmail() != null && !request.getEmail().isBlank()
                && workerRepository.existsByEmail(request.getEmail())) {
            throw new RuntimeException(
                "Email address already registered: " + request.getEmail()
            );
        }

        // ── Build and save worker ─────────────────────────────────────────
        AncWorkerEntity worker = AncWorkerEntity.builder()
                .fullName(request.getFullName())
                .phone(request.getPhone())
                .email(request.getEmail())
                .passwordHash(passwordEncoder.encode(request.getPassword()))
                .healthCenter(request.getHealthCenter())
                .district(request.getDistrict())
                .isActive(true)
                .build();

        worker = workerRepository.save(worker);
        log.info("Worker account created — ID: {}, Phone: {}", worker.getId(), worker.getPhone());

        // ── Generate JWT ──────────────────────────────────────────────────
        String token = jwtService.generateToken(worker.getPhone(), worker.getId());

        return buildAuthResponse(worker, token, "Account created successfully");
    }

    public AuthResponseDTO login(WorkerLoginRequestDTO request) {
        log.info("Processing login for phone: {}", request.getPhone());

        // ── Delegate credential check to Spring Security ──────────────────
        // This throws BadCredentialsException if phone/password don't match.
        // It throws DisabledException if the worker's isActive = false.
        // Both are caught by GlobalExceptionHandler.
        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        request.getPhone(),    // principal (username)
                        request.getPassword()  // credentials (raw password)
                )
        );

        // ── If we reach here, credentials are valid ───────────────────────
        AncWorkerEntity worker = workerRepository.findByPhone(request.getPhone())
                .orElseThrow(() -> new RuntimeException("Worker not found after authentication"));

        String token = jwtService.generateToken(worker.getPhone(), worker.getId());
        log.info("Login successful for worker ID: {}", worker.getId());

        return buildAuthResponse(worker, token, "Login successful");
    }

    private AuthResponseDTO buildAuthResponse(AncWorkerEntity worker, String token, String message) {
        return AuthResponseDTO.builder()
                .token(token)
                .workerId(worker.getId())
                .fullName(worker.getFullName())
                .phone(worker.getPhone())
                .email(worker.getEmail())
                .healthCenter(worker.getHealthCenter())
                .district(worker.getDistrict())
                .message(message)
                .build();
    }
}
```

---

## service/PatientService.java

```java
package com.anc.service;

import com.anc.dto.PatientCreateRequestDTO;
import com.anc.dto.PatientResponseDTO;
import com.anc.entity.PatientEntity;
import com.anc.repository.PatientRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Patient CRUD for ANC workers.
 *
 * SECURITY NOTE: workerId is always passed from the controller after
 * being extracted from @AuthenticationPrincipal — never from the request body.
 * This ensures a worker cannot create or view another worker's patients.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class PatientService {

    private final PatientRepository patientRepository;

    /**
     * Register a new patient under the logged-in worker.
     *
     * @param request  patient details from React form
     * @param workerId extracted from JWT by @AuthenticationPrincipal in controller
     */
    public PatientResponseDTO createPatient(PatientCreateRequestDTO request, String workerId) {
        log.info("Creating patient '{}' for worker: {}", request.getFullName(), workerId);

        PatientEntity patient = PatientEntity.builder()
                .workerId(workerId)
                .fullName(request.getFullName())
                .phone(request.getPhone())
                .age(request.getAge())
                .address(request.getAddress())
                .village(request.getVillage())
                .district(request.getDistrict())
                .lmpDate(request.getLmpDate())
                .eddDate(request.getEddDate())
                .bloodGroup(request.getBloodGroup())
                .build();

        patient = patientRepository.save(patient);
        log.info("Patient registered — ID: {}", patient.getId());

        return toResponseDTO(patient);
    }

    /**
     * Get all patients belonging to this worker.
     * Workers never see patients registered by other workers.
     */
    public List<PatientResponseDTO> getMyPatients(String workerId) {
        log.debug("Fetching all patients for worker: {}", workerId);
        return patientRepository.findByWorkerIdOrderByCreatedAtDesc(workerId)
                .stream()
                .map(this::toResponseDTO)
                .collect(Collectors.toList());
    }

    /**
     * Get a single patient by ID.
     * Verifies the patient belongs to the requesting worker — throws if not.
     *
     * @param patientId the UUID of the patient to fetch
     * @param workerId  the JWT-authenticated worker's ID
     */
    public PatientResponseDTO getPatientById(String patientId, String workerId) {
        PatientEntity patient = patientRepository.findById(patientId)
                .orElseThrow(() -> new RuntimeException("Patient not found: " + patientId));

        // Security check — prevent cross-worker data access
        if (!patient.getWorkerId().equals(workerId)) {
            log.warn("Worker {} attempted to access patient {} belonging to worker {}",
                    workerId, patientId, patient.getWorkerId());
            throw new RuntimeException("Access denied: this patient is not registered under your account");
        }

        return toResponseDTO(patient);
    }

    private PatientResponseDTO toResponseDTO(PatientEntity p) {
        return PatientResponseDTO.builder()
                .patientId(p.getId())
                .workerId(p.getWorkerId())
                .fullName(p.getFullName())
                .phone(p.getPhone())
                .age(p.getAge())
                .address(p.getAddress())
                .village(p.getVillage())
                .district(p.getDistrict())
                .lmpDate(p.getLmpDate())
                .eddDate(p.getEddDate())
                .bloodGroup(p.getBloodGroup())
                .createdAt(p.getCreatedAt())
                .build();
    }
}
```

---

## controller/AuthController.java

```java
package com.anc.controller;

import com.anc.dto.AuthResponseDTO;
import com.anc.dto.WorkerLoginRequestDTO;
import com.anc.dto.WorkerSignupRequestDTO;
import com.anc.entity.AncWorkerEntity;
import com.anc.service.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")  // Lock to React origin URL in production
public class AuthController {

    private final AuthService authService;

    /**
     * POST /api/auth/signup
     *
     * Public endpoint — no JWT needed.
     *
     * Request body:
     * {
     *   "fullName":     "Anjali Devi",
     *   "phone":        "9876543210",
     *   "email":        "anjali@phc.in",
     *   "password":     "StrongPassword123",
     *   "healthCenter": "PHC Angondhalli",
     *   "district":     "Bangalore Rural"
     * }
     *
     * Response: { token, workerId, fullName, phone, healthCenter, district, message }
     */
    @PostMapping("/signup")
    public ResponseEntity<AuthResponseDTO> signup(
            @Valid @RequestBody WorkerSignupRequestDTO request) {

        log.info("Signup request for phone: {}", request.getPhone());
        AuthResponseDTO response = authService.signup(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * POST /api/auth/login
     *
     * Public endpoint — no JWT needed.
     *
     * Request body:
     * {
     *   "phone":    "9876543210",
     *   "password": "StrongPassword123"
     * }
     *
     * Response: { token, workerId, fullName, phone, healthCenter, district, message }
     */
    @PostMapping("/login")
    public ResponseEntity<AuthResponseDTO> login(
            @Valid @RequestBody WorkerLoginRequestDTO request) {

        log.info("Login request for phone: {}", request.getPhone());
        AuthResponseDTO response = authService.login(request);
        return ResponseEntity.ok(response);
    }

    /**
     * GET /api/auth/me
     *
     * Protected endpoint — requires: Authorization: Bearer <token>
     *
     * Returns the logged-in worker's profile.
     * @AuthenticationPrincipal injects the AncWorkerEntity set by JwtAuthFilter.
     * No DB call needed — already loaded during JWT filter.
     */
    @GetMapping("/me")
    public ResponseEntity<AuthResponseDTO> getMe(
            @AuthenticationPrincipal AncWorkerEntity worker) {

        AuthResponseDTO response = AuthResponseDTO.builder()
                .workerId(worker.getId())
                .fullName(worker.getFullName())
                .phone(worker.getPhone())
                .email(worker.getEmail())
                .healthCenter(worker.getHealthCenter())
                .district(worker.getDistrict())
                .message("Profile fetched successfully")
                .build();

        return ResponseEntity.ok(response);
    }
}
```

---

## controller/PatientController.java

```java
package com.anc.controller;

import com.anc.dto.PatientCreateRequestDTO;
import com.anc.dto.PatientResponseDTO;
import com.anc.entity.AncWorkerEntity;
import com.anc.service.PatientService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Patient management endpoints.
 *
 * ALL endpoints require: Authorization: Bearer <token>
 *
 * @AuthenticationPrincipal AncWorkerEntity worker
 *   → injected by Spring Security after JwtAuthFilter validates the token
 *   → worker.getId() gives the authenticated workerId
 *   → workerId is NEVER taken from the request body
 */
@Slf4j
@RestController
@RequestMapping("/api/patients")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class PatientController {

    private final PatientService patientService;

    /**
     * POST /api/patients
     *
     * Header: Authorization: Bearer <token>
     *
     * Request body:
     * {
     *   "fullName":   "Meena Kumari",
     *   "phone":      "9123456789",
     *   "age":        24,
     *   "address":    "123 Main St",
     *   "village":    "Hebbal",
     *   "district":   "Bangalore Rural",
     *   "lmpDate":    "2025-10-01",
     *   "eddDate":    "2026-07-08",
     *   "bloodGroup": "B+"
     * }
     *
     * Response: { patientId, workerId, fullName, phone, lmpDate, eddDate, ... }
     */
    @PostMapping
    public ResponseEntity<PatientResponseDTO> createPatient(
            @Valid @RequestBody PatientCreateRequestDTO request,
            @AuthenticationPrincipal AncWorkerEntity worker) {

        log.info("Worker {} registering patient: {}", worker.getId(), request.getFullName());
        PatientResponseDTO response = patientService.createPatient(request, worker.getId());
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * GET /api/patients
     *
     * Header: Authorization: Bearer <token>
     *
     * Returns all patients registered by the logged-in worker, newest first.
     * Workers CANNOT see patients registered by other workers.
     */
    @GetMapping
    public ResponseEntity<List<PatientResponseDTO>> getMyPatients(
            @AuthenticationPrincipal AncWorkerEntity worker) {

        log.info("Fetching patient list for worker: {}", worker.getId());
        List<PatientResponseDTO> patients = patientService.getMyPatients(worker.getId());
        return ResponseEntity.ok(patients);
    }

    /**
     * GET /api/patients/{patientId}
     *
     * Header: Authorization: Bearer <token>
     *
     * Returns a single patient record.
     * Returns 500 if patient belongs to a different worker.
     */
    @GetMapping("/{patientId}")
    public ResponseEntity<PatientResponseDTO> getPatient(
            @PathVariable String patientId,
            @AuthenticationPrincipal AncWorkerEntity worker) {

        log.info("Worker {} fetching patient: {}", worker.getId(), patientId);
        PatientResponseDTO patient = patientService.getPatientById(patientId, worker.getId());
        return ResponseEntity.ok(patient);
    }
}
```

---

## exception/GlobalExceptionHandler.java — Add Auth Error Handlers

```java
// Add these new @ExceptionHandler methods to the existing GlobalExceptionHandler class
// Keep all existing handlers (validation, FastAPI, runtime) and add these below:

import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.DisabledException;
import org.springframework.security.authentication.LockedException;
import org.springframework.security.core.userdetails.UsernameNotFoundException;

/**
 * Wrong phone number or wrong password during login.
 * AuthenticationManager throws this automatically.
 * We return 401 with a generic message (don't reveal which field is wrong).
 */
@ExceptionHandler(BadCredentialsException.class)
public ResponseEntity<Map<String, Object>> handleBadCredentials(BadCredentialsException ex) {
    return buildErrorResponse(
            HttpStatus.UNAUTHORIZED,
            "Invalid phone number or password",
            null
    );
}

/**
 * Worker's isActive = false — account has been disabled by supervisor.
 */
@ExceptionHandler(DisabledException.class)
public ResponseEntity<Map<String, Object>> handleDisabledAccount(DisabledException ex) {
    return buildErrorResponse(
            HttpStatus.FORBIDDEN,
            "Your account has been disabled. Please contact your supervisor.",
            null
    );
}

/**
 * Account is locked (isAccountNonLocked = false on AncWorkerEntity).
 */
@ExceptionHandler(LockedException.class)
public ResponseEntity<Map<String, Object>> handleLockedAccount(LockedException ex) {
    return buildErrorResponse(
            HttpStatus.FORBIDDEN,
            "Your account is locked. Please contact your supervisor.",
            null
    );
}

/**
 * Phone number not found — should not normally reach the client
 * (BadCredentialsException is thrown instead during login),
 * but included as a safety net.
 */
@ExceptionHandler(UsernameNotFoundException.class)
public ResponseEntity<Map<String, Object>> handleUsernameNotFound(UsernameNotFoundException ex) {
    return buildErrorResponse(
            HttpStatus.UNAUTHORIZED,
            "Invalid phone number or password",
            null
    );
}
```

---

## Security Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                    SIGNUP / LOGIN (public)                            │
│                                                                      │
│  React                  AuthController         AuthService           │
│    │                         │                      │                │
│    │── POST /api/auth/login ─►│                      │                │
│    │   { phone, password }    │                      │                │
│    │                         │── authService.login()►│                │
│    │                         │                      │                │
│    │                         │              authManager.authenticate()│
│    │                         │              (phone, rawPassword)      │
│    │                         │                      │                │
│    │                         │              CustomUserDetailsService  │
│    │                         │              .loadUserByUsername(phone)│
│    │                         │              → AncWorkerEntity         │
│    │                         │                      │                │
│    │                         │              BCrypt.matches(           │
│    │                         │                rawPassword,           │
│    │                         │                storedHash)            │
│    │                         │                      │                │
│    │                         │              jwtService.generateToken()│
│    │                         │                      │                │
│    │◄── 200 { token, ... } ──│◄─ AuthResponseDTO ───│                │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                  PROTECTED REQUESTS (JWT required)                   │
│                                                                      │
│  React               JwtAuthFilter    Controller    Service          │
│    │                      │               │            │             │
│    │── POST /api/patients ►│               │            │             │
│    │  Authorization:       │               │            │             │
│    │  Bearer <token>       │               │            │             │
│    │                       │               │            │             │
│    │              extract phone from JWT   │            │             │
│    │              loadUserByUsername(phone)│            │             │
│    │              isTokenValid(jwt, worker)│            │             │
│    │              setAuthentication(worker)│            │             │
│    │                       │               │            │             │
│    │                       │──────────────►│            │             │
│    │                    @AuthenticationPrincipal        │             │
│    │                    AncWorkerEntity worker          │             │
│    │                               │──────────────────►│             │
│    │                               │  patientService   │             │
│    │                               │  .createPatient() │             │
│    │                               │  (request,        │             │
│    │                               │   worker.getId()) │             │
│    │◄── 201 { patientId, ... } ────│◄──────────────────│             │
└──────────────────────────────────────────────────────────────────────┘
```

---

## React Usage Guide

```javascript
// ─── 1. SIGNUP ───────────────────────────────────────────────────────────────
const res = await fetch('http://localhost:8080/api/auth/signup', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    fullName:     'Anjali Devi',
    phone:        '9876543210',
    email:        'anjali@phc.in',
    password:     'StrongPassword123',
    healthCenter: 'PHC Angondhalli',
    district:     'Bangalore Rural'
  })
});
const { token, workerId, fullName } = await res.json();
localStorage.setItem('anc_token', token);


// ─── 2. LOGIN ────────────────────────────────────────────────────────────────
const res = await fetch('http://localhost:8080/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone:    '9876543210',
    password: 'StrongPassword123'
  })
});
const { token } = await res.json();
localStorage.setItem('anc_token', token);


// ─── 3. HELPER — attach token to every protected call ────────────────────────
const authFetch = (url, options = {}) => {
  const token = localStorage.getItem('anc_token');
  return fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers
    }
  });
};


// ─── 4. CREATE PATIENT ───────────────────────────────────────────────────────
const patient = await authFetch('http://localhost:8080/api/patients', {
  method: 'POST',
  body: JSON.stringify({
    fullName:   'Meena Kumari',
    phone:      '9123456789',
    age:        24,
    village:    'Hebbal',
    district:   'Bangalore Rural',
    lmpDate:    '2025-10-01',
    eddDate:    '2026-07-08',
    bloodGroup: 'B+'
  })
}).then(r => r.json());
// → { patientId, workerId, fullName, lmpDate, eddDate, ... }


// ─── 5. GET MY PATIENTS ──────────────────────────────────────────────────────
const patients = await authFetch('http://localhost:8080/api/patients')
  .then(r => r.json());
// → [ { patientId, fullName, age, ... }, ... ]


// ─── 6. SUBMIT ANC VISIT ─────────────────────────────────────────────────────
const visit = await authFetch('http://localhost:8080/api/anc/register-visit', {
  method: 'POST',
  body: JSON.stringify({
    patientId:   patient.patientId,
    structured_data: {
      patient_info:     { age: 24, gestationalWeeks: 28 },
      vitals:           { bpSystolic: 130, bpDiastolic: 85, bmi: 24.5 },
      lab_reports:      { hemoglobin: 9.5, urineProtein: false },
      medical_history:  { previousLSCS: false, smoking: false },
      obstetric_history:{ birthOrder: 1, interPregnancyInterval: null },
      pregnancy_details:{ twinPregnancy: false, placentaPrevia: false },
      current_symptoms: { headache: false, convulsions: false }
    }
  })
}).then(r => r.json());
// → { visitId, status, riskAssessment: { isHighRisk, riskLevel, detectedRisks, ... } }
```

---

## Entity Relationship

```
anc_workers
  id (UUID PK)
  phone (UNIQUE)
  password_hash
  full_name, email, health_center, district, is_active
       │
       │ 1:Many (worker_id)
       ▼
  patients
    id (UUID PK)
    worker_id ──────────────────► anc_workers.id
    full_name, phone, age
    lmp_date, edd_date, blood_group
         │
         │ 1:Many (patient_id)
         ▼
    anc_visits
      id (UUID PK)
      patient_id ─────────────► patients.id
      worker_id  ─────────────► anc_workers.id
      structured_data (JSONB)
      is_high_risk, risk_level
      detected_risks (JSONB)
      explanation, confidence, recommendation
      status: REGISTERED / AI_ANALYZED / AI_FAILED
```

---

## Security Checklist

| Item | Implementation |
|------|----------------|
| Password hashing | BCrypt strength 12 |
| Token algorithm | HMAC-SHA256 (HS256) |
| Token expiry | 24 hours (configurable) |
| Session management | Stateless — no server-side session |
| CSRF | Disabled — not needed for stateless JWT APIs |
| workerId source | Always JWT claims — never request body |
| Patient isolation | Enforced in PatientService — cross-worker access throws |
| Account blocking | Set `is_active = false` to block without deleting |
| Error messages | Generic "Invalid phone or password" — never reveals which field failed |
| Public endpoints | Only `/api/auth/signup` and `/api/auth/login` |
