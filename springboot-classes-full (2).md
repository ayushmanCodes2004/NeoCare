# Spring Boot ANC Service — Complete Class Reference
## Updated to match actual FastAPI Response Structure

**Package:** `com.anc` | **Stack:** Spring Boot 3.2 + PostgreSQL + RestTemplate → FastAPI

---

## Actual FastAPI `/analyze` Response (Source of Truth)

```json
{
    "isHighRisk": true,
    "riskLevel": "CRITICAL",
    "detectedRisks": [
        "Severe Anaemia",
        "Severe Pre Eclampsia",
        "GDM Screening Overdue",
        "Elderly Gravida",
        "Twin Pregnancy"
    ],
    "explanation": "Risk Assessment: CRITICAL. Patient presents with 5 significant risk factors...",
    "confidence": 0.7,
    "recommendation": "URGENT: Immediate referral to CEmOC/District Hospital required.",
    "patientId": null,
    "patientName": null,
    "age": 38,
    "gestationalWeeks": 30,
    "visitMetadata": null
}
```

---

## Project Structure

```
com.anc/
├── AncServiceApplication.java
├── controller/
│   └── AncVisitController.java
├── service/
│   ├── AncVisitService.java
│   └── ClinicalSummaryBuilder.java
├── client/
│   └── FastApiClient.java
├── entity/
│   └── AncVisitEntity.java
├── repository/
│   └── AncVisitRepository.java
├── mapper/
│   └── AncVisitMapper.java
├── dto/
│   ├── AncVisitRequestDTO.java
│   ├── AncVisitResponseDTO.java
│   ├── StructuredDataDTO.java
│   ├── PatientInfoDTO.java
│   ├── MedicalHistoryDTO.java
│   ├── VitalsDTO.java
│   ├── LabReportsDTO.java
│   ├── ObstetricHistoryDTO.java
│   ├── PregnancyDetailsDTO.java
│   ├── CurrentSymptomsDTO.java
│   ├── FastApiRequestDTO.java
│   └── FastApiResponseDTO.java     ← matches actual FastAPI output
├── exception/
│   ├── FastApiException.java
│   └── GlobalExceptionHandler.java
└── config/
    ├── RestTemplateConfig.java
    └── JacksonConfig.java
resources/
├── application.yml
└── schema.sql
```

---

## Data Flow

```
React POST /api/anc/register-visit
               ↓
   AncVisitController.registerVisit()
               ↓
   AncVisitService.registerVisit()
     1. ClinicalSummaryBuilder.build()        → auto-build clinical_summary string
     2. AncVisitMapper.toEntity()             → DTO → Entity
     3. visitRepository.save()               → PostgreSQL  (status = REGISTERED)
     4. FastApiClient.analyzeRisk()          → POST /analyze to FastAPI
     5. AncVisitMapper.enrichWithAiResponse()→ map isHighRisk, riskLevel,
                                               detectedRisks, explanation,
                                               confidence, recommendation,
                                               visitMetadata onto entity
     6. visitRepository.save()              → PostgreSQL  (status = AI_ANALYZED)
     7. AncVisitMapper.toResponseDTO()      → build final response
               ↓
   React receives AncVisitResponseDTO
```

---

## REST Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/anc/register-visit` | Register visit + trigger FastAPI risk analysis |
| GET | `/api/anc/visits/{visitId}` | Get single visit |
| GET | `/api/anc/patients/{patientId}/visits` | All visits for a patient |
| GET | `/api/anc/visits/high-risk` | All visits where `isHighRisk = true` |
| GET | `/api/anc/visits/critical` | Only `riskLevel = CRITICAL` visits |

---

## pom.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
        <relativePath/>
    </parent>

    <groupId>com.anc</groupId>
    <artifactId>anc-service</artifactId>
    <version>1.0.0</version>
    <description>ANC Patient Registration and Risk Assessment Service</description>

    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.datatype</groupId>
            <artifactId>jackson-datatype-jsr310</artifactId>
        </dependency>
        <!-- JSONB column support for PostgreSQL -->
        <dependency>
            <groupId>io.hypersistence</groupId>
            <artifactId>hypersistence-utils-hibernate-62</artifactId>
            <version>3.7.0</version>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

---

## resources/application.yml

```yaml
spring:
  application:
    name: anc-service

  datasource:
    url: jdbc:postgresql://localhost:5432/anc_db
    username: postgres
    password: yourpassword
    driver-class-name: org.postgresql.Driver
    hikari:
      maximum-pool-size: 10
      minimum-idle: 5
      connection-timeout: 30000

  jpa:
    hibernate:
      ddl-auto: update          # use 'validate' in production
    show-sql: true
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        format_sql: true
    open-in-view: false

server:
  port: 8080

fastapi:
  base-url: http://localhost:8000
  connect-timeout: 5000
  read-timeout: 30000
  api-key: your-fastapi-secret-key

logging:
  level:
    com.anc: DEBUG
    org.hibernate.SQL: DEBUG
```

---

## resources/schema.sql

```sql
CREATE DATABASE anc_db;
\c anc_db;

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS anc_visits (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Patient & worker identifiers
    patient_id        VARCHAR(255),
    patient_name      VARCHAR(255),
    worker_id         VARCHAR(255),
    phc_id            VARCHAR(255),

    -- ANC input from React
    clinical_summary  TEXT,
    structured_data   JSONB NOT NULL,

    -- FastAPI /analyze output (exact field names from response)
    is_high_risk      BOOLEAN,
    risk_level        VARCHAR(20),        -- CRITICAL / HIGH / MEDIUM / LOW
    detected_risks    JSONB,              -- ["Severe Anaemia", "Twin Pregnancy", ...]
    explanation       TEXT,
    confidence        NUMERIC(4,3),       -- 0.000 to 1.000
    recommendation    TEXT,
    visit_metadata    JSONB,              -- nullable extra metadata from FastAPI

    -- Processing lifecycle
    status            VARCHAR(30) DEFAULT 'REGISTERED',  -- REGISTERED/AI_ANALYZED/AI_FAILED
    ai_error_message  TEXT,

    -- Timestamps
    created_at        TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Standard indexes
CREATE INDEX idx_anc_patient_id     ON anc_visits(patient_id);
CREATE INDEX idx_anc_worker_id      ON anc_visits(worker_id);
CREATE INDEX idx_anc_risk_level     ON anc_visits(risk_level);
CREATE INDEX idx_anc_is_high_risk   ON anc_visits(is_high_risk);
CREATE INDEX idx_anc_created_at     ON anc_visits(created_at DESC);

-- GIN indexes for JSONB columns
CREATE INDEX idx_anc_structured     ON anc_visits USING GIN(structured_data);
CREATE INDEX idx_anc_detected_risks ON anc_visits USING GIN(detected_risks);
```

---

## AncServiceApplication.java

```java
package com.anc;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class AncServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(AncServiceApplication.class, args);
    }
}
```

---

## config/RestTemplateConfig.java

```java
package com.anc.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;

@Configuration
public class RestTemplateConfig {

    @Value("${fastapi.connect-timeout:5000}")
    private int connectTimeout;

    @Value("${fastapi.read-timeout:30000}")
    private int readTimeout;

    @Bean
    public RestTemplate restTemplate() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(connectTimeout);
        factory.setReadTimeout(readTimeout);
        return new RestTemplate(factory);
    }
}
```

---

## config/JacksonConfig.java

```java
package com.anc.config;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

@Configuration
public class JacksonConfig {

    @Bean
    @Primary
    public ObjectMapper objectMapper() {
        ObjectMapper mapper = new ObjectMapper();
        mapper.registerModule(new JavaTimeModule());
        mapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
        // Prevents failure if FastAPI adds new fields later
        mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        return mapper;
    }
}
```

---

## dto/PatientInfoDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class PatientInfoDTO {

    @NotNull
    @Min(value = 15, message = "Age must be at least 15")
    @Max(value = 55, message = "Age must be at most 55")
    @JsonProperty("age")
    private Integer age;

    @NotNull
    @Min(value = 1, message = "Gestational weeks must be at least 1")
    @Max(value = 42, message = "Gestational weeks cannot exceed 42")
    @JsonProperty("gestationalWeeks")
    private Integer gestationalWeeks;
}
```

---

## dto/MedicalHistoryDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class MedicalHistoryDTO {

    @JsonProperty("previousLSCS")
    private Boolean previousLscs;

    @JsonProperty("badObstetricHistory")
    private Boolean badObstetricHistory;

    @JsonProperty("previousStillbirth")
    private Boolean previousStillbirth;

    @JsonProperty("previousPretermDelivery")
    private Boolean previousPretermDelivery;

    @JsonProperty("previousAbortion")
    private Boolean previousAbortion;

    @JsonProperty("systemicIllness")
    private String systemicIllness;

    @JsonProperty("chronicHypertension")
    private Boolean chronicHypertension;

    @JsonProperty("diabetes")
    private Boolean diabetes;

    @JsonProperty("thyroidDisorder")
    private Boolean thyroidDisorder;

    @JsonProperty("smoking")
    private Boolean smoking;

    @JsonProperty("tobaccoUse")
    private Boolean tobaccoUse;

    @JsonProperty("alcoholUse")
    private Boolean alcoholUse;
}
```

---

## dto/VitalsDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class VitalsDTO {

    @JsonProperty("heightCm")
    private Double heightCm;

    @JsonProperty("bmi")
    private Double bmi;

    @JsonProperty("bpSystolic")
    private Integer bpSystolic;

    @JsonProperty("bpDiastolic")
    private Integer bpDiastolic;
}
```

---

## dto/LabReportsDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class LabReportsDTO {

    @JsonProperty("hemoglobin")
    private Double hemoglobin;

    @JsonProperty("rhNegative")
    private Boolean rhNegative;

    @JsonProperty("hivPositive")
    private Boolean hivPositive;

    @JsonProperty("syphilisPositive")
    private Boolean syphilisPositive;

    @JsonProperty("urineProtein")
    private Boolean urineProtein;

    @JsonProperty("urineSugar")
    private Boolean urineSugar;
}
```

---

## dto/ObstetricHistoryDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class ObstetricHistoryDTO {

    @JsonProperty("birthOrder")
    private Integer birthOrder;

    @JsonProperty("interPregnancyInterval")
    private Integer interPregnancyInterval;

    @JsonProperty("stillbirthCount")
    private Integer stillbirthCount;

    @JsonProperty("abortionCount")
    private Integer abortionCount;

    @JsonProperty("pretermHistory")
    private Boolean pretermHistory;
}
```

---

## dto/PregnancyDetailsDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class PregnancyDetailsDTO {

    @JsonProperty("twinPregnancy")
    private Boolean twinPregnancy;

    @JsonProperty("malpresentation")
    private Boolean malpresentation;

    @JsonProperty("placentaPrevia")
    private Boolean placentaPrevia;

    @JsonProperty("reducedFetalMovement")
    private Boolean reducedFetalMovement;

    @JsonProperty("amnioticFluidNormal")
    private Boolean amnioticFluidNormal;

    @JsonProperty("umbilicalDopplerAbnormal")
    private Boolean umbilicalDopplerAbnormal;
}
```

---

## dto/CurrentSymptomsDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class CurrentSymptomsDTO {

    @JsonProperty("headache")
    private Boolean headache;

    @JsonProperty("visualDisturbance")
    private Boolean visualDisturbance;

    @JsonProperty("epigastricPain")
    private Boolean epigastricPain;

    @JsonProperty("decreasedUrineOutput")
    private Boolean decreasedUrineOutput;

    @JsonProperty("bleedingPerVagina")
    private Boolean bleedingPerVagina;

    @JsonProperty("convulsions")
    private Boolean convulsions;
}
```

---

## dto/StructuredDataDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class StructuredDataDTO {

    @JsonProperty("patient_info")
    private PatientInfoDTO patientInfo;

    @JsonProperty("medical_history")
    private MedicalHistoryDTO medicalHistory;

    @JsonProperty("vitals")
    private VitalsDTO vitals;

    @JsonProperty("lab_reports")
    private LabReportsDTO labReports;

    @JsonProperty("obstetric_history")
    private ObstetricHistoryDTO obstetricHistory;

    @JsonProperty("pregnancy_details")
    private PregnancyDetailsDTO pregnancyDetails;

    @JsonProperty("current_symptoms")
    private CurrentSymptomsDTO currentSymptoms;
}
```

---

## dto/AncVisitRequestDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class AncVisitRequestDTO {

    @JsonProperty("patientId")
    private String patientId;

    @JsonProperty("patientName")
    private String patientName;

    @JsonProperty("workerId")
    private String workerId;

    @JsonProperty("phcId")
    private String phcId;

    // Optional — auto-generated by ClinicalSummaryBuilder if not sent
    @JsonProperty("clinical_summary")
    private String clinicalSummary;

    @Valid
    @NotNull(message = "Structured data is required")
    @JsonProperty("structured_data")
    private StructuredDataDTO structuredData;
}
```

---

## dto/FastApiRequestDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FastApiRequestDTO {

    @JsonProperty("clinical_summary")
    private String clinicalSummary;

    @JsonProperty("structured_data")
    private StructuredDataDTO structuredData;
}
```

---

## dto/FastApiResponseDTO.java  ← UPDATED: exact FastAPI field mapping

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.util.List;
import java.util.Map;

/**
 * Exact mapping of the FastAPI /analyze response JSON:
 *
 * {
 *   "isHighRisk": true,
 *   "riskLevel": "CRITICAL",
 *   "detectedRisks": ["Severe Anaemia", "Severe Pre Eclampsia", ...],
 *   "explanation": "Risk Assessment: CRITICAL...",
 *   "confidence": 0.7,
 *   "recommendation": "URGENT: Immediate referral to CEmOC...",
 *   "patientId": null,
 *   "patientName": null,
 *   "age": 38,
 *   "gestationalWeeks": 30,
 *   "visitMetadata": null
 * }
 */
@Data
public class FastApiResponseDTO {

    /** true = high risk pregnancy, false = low risk */
    @JsonProperty("isHighRisk")
    private Boolean isHighRisk;

    /** Risk tier: CRITICAL / HIGH / MEDIUM / LOW */
    @JsonProperty("riskLevel")
    private String riskLevel;

    /** Detected PMSMA risk conditions e.g. ["Severe Anaemia", "Twin Pregnancy"] */
    @JsonProperty("detectedRisks")
    private List<String> detectedRisks;

    /** Human-readable LLM explanation of the risk assessment */
    @JsonProperty("explanation")
    private String explanation;

    /** RAG model confidence score: 0.0 to 1.0 */
    @JsonProperty("confidence")
    private Double confidence;

    /** Primary clinical recommendation */
    @JsonProperty("recommendation")
    private String recommendation;

    /** Patient identifiers echoed back by FastAPI (may be null) */
    @JsonProperty("patientId")
    private String patientId;

    @JsonProperty("patientName")
    private String patientName;

    /** Patient age echoed back from structured_data.patient_info */
    @JsonProperty("age")
    private Integer age;

    /** Gestational weeks echoed back from structured_data.patient_info */
    @JsonProperty("gestationalWeeks")
    private Integer gestationalWeeks;

    /** Optional metadata map from FastAPI — null in current response */
    @JsonProperty("visitMetadata")
    private Map<String, Object> visitMetadata;
}
```

---

## dto/AncVisitResponseDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * Final response returned to React after:
 *  - Visit saved to PostgreSQL
 *  - FastAPI RAG risk analysis completed
 */
@Data
@Builder
public class AncVisitResponseDTO {

    @JsonProperty("visitId")
    private String visitId;

    @JsonProperty("patientId")
    private String patientId;

    @JsonProperty("patientName")
    private String patientName;

    /** REGISTERED / AI_ANALYZED / AI_FAILED */
    @JsonProperty("status")
    private String status;

    /** Full FastAPI risk assessment block */
    @JsonProperty("riskAssessment")
    private FastApiResponseDTO riskAssessment;

    @JsonProperty("savedAt")
    private LocalDateTime savedAt;

    /** Human-readable status message for React to display */
    @JsonProperty("message")
    private String message;
}
```

---

## entity/AncVisitEntity.java  ← UPDATED: columns match actual FastAPI response

```java
package com.anc.entity;

import io.hypersistence.utils.hibernate.type.json.JsonBinaryType;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.Type;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Entity
@Table(name = "anc_visits")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AncVisitEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id", updatable = false, nullable = false)
    private String id;

    // ── Patient & worker identifiers ──────────────────────────────────────
    @Column(name = "patient_id")
    private String patientId;

    @Column(name = "patient_name")
    private String patientName;

    @Column(name = "worker_id")
    private String workerId;

    @Column(name = "phc_id")
    private String phcId;

    // ── ANC Input ─────────────────────────────────────────────────────────
    @Column(name = "clinical_summary", columnDefinition = "TEXT")
    private String clinicalSummary;

    @Type(JsonBinaryType.class)
    @Column(name = "structured_data", columnDefinition = "jsonb")
    private Map<String, Object> structuredData;

    // ── FastAPI /analyze Output ───────────────────────────────────────────

    /** FastAPI: isHighRisk — boolean flag for quick DB filtering */
    @Column(name = "is_high_risk")
    private Boolean isHighRisk;

    /** FastAPI: riskLevel — CRITICAL / HIGH / MEDIUM / LOW */
    @Column(name = "risk_level", length = 20)
    private String riskLevel;

    /** FastAPI: detectedRisks — ["Severe Anaemia", "Twin Pregnancy", ...] */
    @Type(JsonBinaryType.class)
    @Column(name = "detected_risks", columnDefinition = "jsonb")
    private List<String> detectedRisks;

    /** FastAPI: explanation — full LLM explanation text */
    @Column(name = "explanation", columnDefinition = "TEXT")
    private String explanation;

    /** FastAPI: confidence — model confidence 0.0 to 1.0 */
    @Column(name = "confidence")
    private Double confidence;

    /** FastAPI: recommendation — primary action string */
    @Column(name = "recommendation", columnDefinition = "TEXT")
    private String recommendation;

    /** FastAPI: visitMetadata — nullable extra metadata */
    @Type(JsonBinaryType.class)
    @Column(name = "visit_metadata", columnDefinition = "jsonb")
    private Map<String, Object> visitMetadata;

    // ── Status lifecycle ──────────────────────────────────────────────────
    /** REGISTERED → AI_ANALYZED or AI_FAILED */
    @Column(name = "status", length = 30)
    private String status;

    @Column(name = "ai_error_message", columnDefinition = "TEXT")
    private String aiErrorMessage;

    // ── Timestamps ────────────────────────────────────────────────────────
    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
```

---

## repository/AncVisitRepository.java  ← UPDATED: new query methods

```java
package com.anc.repository;

import com.anc.entity.AncVisitEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AncVisitRepository extends JpaRepository<AncVisitEntity, String> {

    List<AncVisitEntity> findByPatientIdOrderByCreatedAtDesc(String patientId);

    List<AncVisitEntity> findByWorkerIdOrderByCreatedAtDesc(String workerId);

    /** All visits where isHighRisk = true (covers CRITICAL + HIGH) */
    List<AncVisitEntity> findByIsHighRiskTrueOrderByCreatedAtDesc();

    /** Filter by specific riskLevel: CRITICAL / HIGH / MEDIUM / LOW */
    List<AncVisitEntity> findByRiskLevelOrderByCreatedAtDesc(String riskLevel);

    /** CRITICAL only — for urgent supervisor alert panel */
    @Query("SELECT v FROM AncVisitEntity v WHERE v.riskLevel = 'CRITICAL' ORDER BY v.createdAt DESC")
    List<AncVisitEntity> findAllCriticalVisits();

    /** Most recent visit for a patient */
    @Query("SELECT v FROM AncVisitEntity v WHERE v.patientId = :patientId ORDER BY v.createdAt DESC LIMIT 1")
    AncVisitEntity findLatestByPatientId(@Param("patientId") String patientId);

    /** Dashboard stat: total high risk count */
    @Query("SELECT COUNT(v) FROM AncVisitEntity v WHERE v.isHighRisk = true")
    long countHighRiskVisits();

    /** Dashboard stat: total critical count */
    @Query("SELECT COUNT(v) FROM AncVisitEntity v WHERE v.riskLevel = 'CRITICAL'")
    long countCriticalVisits();
}
```

---

## exception/FastApiException.java

```java
package com.anc.exception;

public class FastApiException extends RuntimeException {

    public FastApiException(String message) {
        super(message);
    }

    public FastApiException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

---

## exception/GlobalExceptionHandler.java

```java
package com.anc.exception;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleValidationErrors(
            MethodArgumentNotValidException ex) {

        Map<String, String> fieldErrors = new HashMap<>();
        ex.getBindingResult().getAllErrors().forEach(error -> {
            String field = ((FieldError) error).getField();
            fieldErrors.put(field, error.getDefaultMessage());
        });

        return buildErrorResponse(HttpStatus.BAD_REQUEST, "Validation failed", fieldErrors);
    }

    @ExceptionHandler(FastApiException.class)
    public ResponseEntity<Map<String, Object>> handleFastApiException(FastApiException ex) {
        log.error("FastAPI error: {}", ex.getMessage());
        return buildErrorResponse(
                HttpStatus.SERVICE_UNAVAILABLE,
                "AI Risk Analysis unavailable. Visit has been saved — retry later.",
                null
        );
    }

    @ExceptionHandler(RuntimeException.class)
    public ResponseEntity<Map<String, Object>> handleRuntimeException(RuntimeException ex) {
        log.error("Unhandled error: {}", ex.getMessage(), ex);
        return buildErrorResponse(HttpStatus.INTERNAL_SERVER_ERROR, ex.getMessage(), null);
    }

    private ResponseEntity<Map<String, Object>> buildErrorResponse(
            HttpStatus status, String message, Object details) {

        Map<String, Object> body = new HashMap<>();
        body.put("timestamp", LocalDateTime.now().toString());
        body.put("status", status.value());
        body.put("error", status.getReasonPhrase());
        body.put("message", message);
        if (details != null) body.put("details", details);

        return ResponseEntity.status(status).body(body);
    }
}
```

---

## client/FastApiClient.java

```java
package com.anc.client;

import com.anc.dto.FastApiRequestDTO;
import com.anc.dto.FastApiResponseDTO;
import com.anc.exception.FastApiException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

@Slf4j
@Component
public class FastApiClient {

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    @Value("${fastapi.base-url}")
    private String fastApiBaseUrl;

    @Value("${fastapi.api-key}")
    private String fastApiKey;

    public FastApiClient(RestTemplate restTemplate, ObjectMapper objectMapper) {
        this.restTemplate = restTemplate;
        this.objectMapper = objectMapper;
    }

    /**
     * POST to FastAPI /analyze endpoint.
     *
     * Returns FastApiResponseDTO with actual fields:
     *   isHighRisk, riskLevel (CRITICAL/HIGH/MEDIUM/LOW),
     *   detectedRisks[], explanation, confidence (0.0-1.0),
     *   recommendation, patientId, patientName, age,
     *   gestationalWeeks, visitMetadata
     */
    public FastApiResponseDTO analyzeRisk(FastApiRequestDTO request) {
        String url = fastApiBaseUrl + "/analyze";

        log.info("Calling FastAPI at: {}", url);
        log.debug("Request payload: {}", toJson(request));

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("X-API-KEY", fastApiKey);

        HttpEntity<FastApiRequestDTO> entity = new HttpEntity<>(request, headers);

        try {
            ResponseEntity<FastApiResponseDTO> response = restTemplate.exchange(
                    url,
                    HttpMethod.POST,
                    entity,
                    FastApiResponseDTO.class
            );

            FastApiResponseDTO body = response.getBody();
            if (body != null) {
                log.info("FastAPI result — isHighRisk: {}, riskLevel: {}, confidence: {}, detectedRisks: {}",
                        body.getIsHighRisk(),
                        body.getRiskLevel(),
                        body.getConfidence(),
                        body.getDetectedRisks());
            }
            return body;

        } catch (HttpClientErrorException e) {
            log.error("FastAPI 4xx error {}: {}", e.getStatusCode(), e.getResponseBodyAsString());
            throw new FastApiException("FastAPI client error: " + e.getStatusCode(), e);

        } catch (HttpServerErrorException e) {
            log.error("FastAPI 5xx error {}: {}", e.getStatusCode(), e.getResponseBodyAsString());
            throw new FastApiException("FastAPI server error: " + e.getStatusCode(), e);

        } catch (ResourceAccessException e) {
            log.error("FastAPI unreachable: {}", e.getMessage());
            throw new FastApiException("FastAPI service is unreachable.", e);
        }
    }

    private String toJson(Object obj) {
        try {
            return objectMapper.writeValueAsString(obj);
        } catch (Exception e) {
            return "[SERIALIZATION ERROR]";
        }
    }
}
```

---

## mapper/AncVisitMapper.java  ← UPDATED: maps actual FastAPI fields

```java
package com.anc.mapper;

import com.anc.dto.AncVisitRequestDTO;
import com.anc.dto.AncVisitResponseDTO;
import com.anc.dto.FastApiResponseDTO;
import com.anc.entity.AncVisitEntity;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.Map;

@Slf4j
@Component
@RequiredArgsConstructor
public class AncVisitMapper {

    private final ObjectMapper objectMapper;

    /**
     * DTO → Entity for first DB save (status = REGISTERED).
     * Converts StructuredDataDTO to Map<String, Object> for JSONB storage.
     */
    public AncVisitEntity toEntity(AncVisitRequestDTO request) {
        Map<String, Object> structuredDataMap = objectMapper.convertValue(
                request.getStructuredData(),
                new TypeReference<Map<String, Object>>() {}
        );

        return AncVisitEntity.builder()
                .patientId(request.getPatientId())
                .patientName(request.getPatientName())
                .workerId(request.getWorkerId())
                .phcId(request.getPhcId())
                .clinicalSummary(request.getClinicalSummary())
                .structuredData(structuredDataMap)
                .status("REGISTERED")
                .build();
    }

    /**
     * Enrich entity with actual FastAPI response fields.
     *
     * Maps every field from the real FastAPI output:
     *   isHighRisk, riskLevel, detectedRisks, explanation,
     *   confidence, recommendation, visitMetadata
     *
     * NOTE: patientId/patientName/age/gestationalWeeks from FastAPI
     * are NOT stored separately — they're already in structured_data.
     */
    public void enrichWithAiResponse(AncVisitEntity entity, FastApiResponseDTO ai) {
        if (ai == null) {
            entity.setStatus("AI_FAILED");
            entity.setAiErrorMessage("No response received from FastAPI");
            return;
        }

        entity.setIsHighRisk(ai.getIsHighRisk());
        entity.setRiskLevel(ai.getRiskLevel());
        entity.setDetectedRisks(ai.getDetectedRisks());
        entity.setExplanation(ai.getExplanation());
        entity.setConfidence(ai.getConfidence());
        entity.setRecommendation(ai.getRecommendation());
        entity.setVisitMetadata(ai.getVisitMetadata());
        entity.setStatus("AI_ANALYZED");

        log.info("Enriched — isHighRisk: {}, riskLevel: {}, detectedRisks count: {}, confidence: {}",
                ai.getIsHighRisk(),
                ai.getRiskLevel(),
                ai.getDetectedRisks() != null ? ai.getDetectedRisks().size() : 0,
                ai.getConfidence());
    }

    /**
     * Entity + FastAPI response → final DTO for React.
     */
    public AncVisitResponseDTO toResponseDTO(AncVisitEntity entity, FastApiResponseDTO aiResponse) {
        return AncVisitResponseDTO.builder()
                .visitId(entity.getId())
                .patientId(entity.getPatientId())
                .patientName(entity.getPatientName())
                .status(entity.getStatus())
                .riskAssessment(aiResponse)
                .savedAt(entity.getCreatedAt())
                .message(buildMessage(entity))
                .build();
    }

    private String buildMessage(AncVisitEntity entity) {
        if ("AI_FAILED".equals(entity.getStatus())) {
            return "Visit registered but AI analysis failed. Please retry.";
        }
        if (Boolean.TRUE.equals(entity.getIsHighRisk())) {
            return "ALERT: High risk pregnancy detected — "
                    + entity.getRiskLevel() + ". Immediate action required.";
        }
        return "Visit registered. Risk analysis complete — " + entity.getRiskLevel() + " risk.";
    }
}
```

---

## service/ClinicalSummaryBuilder.java

```java
package com.anc.service;

import com.anc.dto.*;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

/**
 * Builds the clinical_summary string sent to FastAPI as the RAG query.
 *
 * Example output for test patient:
 * "38-year-old at 30 weeks gestation with severe hypertension (165/110 mmHg),
 *  obese (BMI 32.0), short stature (135.0 cm), severe anemia (Hb 6.5 g/dL),
 *  proteinuria, Rh-negative, grand multipara (G6), short inter-pregnancy
 *  interval (8 months), twin pregnancy, previous stillbirth, smoker,
 *  headache, visual disturbances"
 */
@Component
public class ClinicalSummaryBuilder {

    public String build(StructuredDataDTO data) {
        if (data == null) return "ANC visit - no structured data available";

        List<String> parts = new ArrayList<>();

        // ── Base: demographics ────────────────────────────────────────────
        if (data.getPatientInfo() != null) {
            PatientInfoDTO p = data.getPatientInfo();
            parts.add(p.getAge() + "-year-old at " + p.getGestationalWeeks() + " weeks gestation");
        }

        // ── Vitals ────────────────────────────────────────────────────────
        if (data.getVitals() != null) {
            VitalsDTO v = data.getVitals();
            if (v.getBpSystolic() != null && v.getBpSystolic() >= 160) {
                parts.add("severe hypertension (" + v.getBpSystolic() + "/" + v.getBpDiastolic() + " mmHg)");
            } else if (v.getBpSystolic() != null && v.getBpSystolic() >= 140) {
                parts.add("hypertension (" + v.getBpSystolic() + "/" + v.getBpDiastolic() + " mmHg)");
            }
            if (v.getBmi() != null && v.getBmi() >= 30)       parts.add("obese (BMI " + v.getBmi() + ")");
            if (v.getHeightCm() != null && v.getHeightCm() < 140) parts.add("short stature (" + v.getHeightCm() + " cm)");
        }

        // ── Lab reports ───────────────────────────────────────────────────
        if (data.getLabReports() != null) {
            LabReportsDTO l = data.getLabReports();
            if (l.getHemoglobin() != null) {
                if (l.getHemoglobin() < 7.0)       parts.add("severe anemia (Hb " + l.getHemoglobin() + " g/dL)");
                else if (l.getHemoglobin() < 11.0) parts.add("anemia (Hb " + l.getHemoglobin() + " g/dL)");
            }
            if (Boolean.TRUE.equals(l.getUrineProtein()))     parts.add("proteinuria");
            if (Boolean.TRUE.equals(l.getRhNegative()))       parts.add("Rh-negative");
            if (Boolean.TRUE.equals(l.getHivPositive()))      parts.add("HIV positive");
            if (Boolean.TRUE.equals(l.getSyphilisPositive())) parts.add("syphilis positive");
        }

        // ── Obstetric history ─────────────────────────────────────────────
        if (data.getObstetricHistory() != null) {
            ObstetricHistoryDTO o = data.getObstetricHistory();
            if (o.getBirthOrder() != null && o.getBirthOrder() >= 5)
                parts.add("grand multipara (G" + o.getBirthOrder() + ")");
            if (o.getInterPregnancyInterval() != null && o.getInterPregnancyInterval() < 18)
                parts.add("short inter-pregnancy interval (" + o.getInterPregnancyInterval() + " months)");
        }

        // ── Pregnancy details ─────────────────────────────────────────────
        if (data.getPregnancyDetails() != null) {
            PregnancyDetailsDTO pr = data.getPregnancyDetails();
            if (Boolean.TRUE.equals(pr.getTwinPregnancy()))            parts.add("twin pregnancy");
            if (Boolean.TRUE.equals(pr.getPlacentaPrevia()))           parts.add("placenta previa");
            if (Boolean.TRUE.equals(pr.getMalpresentation()))          parts.add("malpresentation");
            if (Boolean.TRUE.equals(pr.getUmbilicalDopplerAbnormal())) parts.add("abnormal umbilical Doppler");
            if (Boolean.TRUE.equals(pr.getReducedFetalMovement()))     parts.add("reduced fetal movements");
        }

        // ── Medical history ───────────────────────────────────────────────
        if (data.getMedicalHistory() != null) {
            MedicalHistoryDTO m = data.getMedicalHistory();
            if (Boolean.TRUE.equals(m.getPreviousStillbirth()))  parts.add("previous stillbirth");
            if (Boolean.TRUE.equals(m.getPreviousLscs()))        parts.add("previous LSCS");
            if (Boolean.TRUE.equals(m.getBadObstetricHistory())) parts.add("bad obstetric history");
            if (Boolean.TRUE.equals(m.getChronicHypertension())) parts.add("chronic hypertension");
            if (Boolean.TRUE.equals(m.getDiabetes()))            parts.add("diabetes");
            if (Boolean.TRUE.equals(m.getThyroidDisorder()))     parts.add("thyroid disorder");
            if (Boolean.TRUE.equals(m.getSmoking()))             parts.add("smoker");
            if (Boolean.TRUE.equals(m.getTobaccoUse()))          parts.add("tobacco use");
            if (Boolean.TRUE.equals(m.getAlcoholUse()))          parts.add("alcohol use");
            if (m.getSystemicIllness() != null
                    && !m.getSystemicIllness().isBlank()
                    && !m.getSystemicIllness().equalsIgnoreCase("None")) {
                parts.add("systemic illness: " + m.getSystemicIllness());
            }
        }

        // ── Current symptoms ──────────────────────────────────────────────
        if (data.getCurrentSymptoms() != null) {
            CurrentSymptomsDTO s = data.getCurrentSymptoms();
            if (Boolean.TRUE.equals(s.getConvulsions()))          parts.add("convulsions");
            if (Boolean.TRUE.equals(s.getHeadache()))             parts.add("headache");
            if (Boolean.TRUE.equals(s.getVisualDisturbance()))    parts.add("visual disturbances");
            if (Boolean.TRUE.equals(s.getEpigastricPain()))       parts.add("epigastric pain");
            if (Boolean.TRUE.equals(s.getDecreasedUrineOutput())) parts.add("decreased urine output");
            if (Boolean.TRUE.equals(s.getBleedingPerVagina()))    parts.add("bleeding per vagina");
        }

        if (parts.isEmpty()) return "ANC visit with no significant findings";
        String base = parts.get(0);
        if (parts.size() == 1) return base;
        return base + " with " + String.join(", ", parts.subList(1, parts.size()));
    }
}
```

---

## service/AncVisitService.java

```java
package com.anc.service;

import com.anc.client.FastApiClient;
import com.anc.dto.*;
import com.anc.entity.AncVisitEntity;
import com.anc.exception.FastApiException;
import com.anc.mapper.AncVisitMapper;
import com.anc.repository.AncVisitRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class AncVisitService {

    private final AncVisitRepository visitRepository;
    private final FastApiClient fastApiClient;
    private final AncVisitMapper mapper;
    private final ClinicalSummaryBuilder summaryBuilder;

    /**
     * Main registration flow:
     *
     *  1. Auto-generate clinical_summary if not provided by React
     *  2. Save visit  → DB status = REGISTERED
     *  3. POST to FastAPI /analyze
     *  4. Persist FastAPI output (isHighRisk, riskLevel, detectedRisks,
     *     explanation, confidence, recommendation, visitMetadata)
     *  5. Update DB  → status = AI_ANALYZED or AI_FAILED
     *  6. Return AncVisitResponseDTO to React
     *
     * AI failure is NON-BLOCKING: visit is always saved.
     */
    @Transactional
    public AncVisitResponseDTO registerVisit(AncVisitRequestDTO request) {
        log.info("Registering ANC visit for patient: {}", request.getPatientId());

        // Step 1 — Build clinical summary if absent
        if (request.getClinicalSummary() == null || request.getClinicalSummary().isBlank()) {
            String summary = summaryBuilder.build(request.getStructuredData());
            request.setClinicalSummary(summary);
            log.debug("Auto-generated summary: {}", summary);
        }

        // Step 2 — Persist initial visit
        AncVisitEntity entity = mapper.toEntity(request);
        entity = visitRepository.save(entity);
        log.info("Visit saved — ID: {}, Status: REGISTERED", entity.getId());

        // Step 3 — Call FastAPI RAG pipeline
        FastApiResponseDTO aiResponse = null;
        try {
            FastApiRequestDTO fastApiReq = FastApiRequestDTO.builder()
                    .clinicalSummary(request.getClinicalSummary())
                    .structuredData(request.getStructuredData())
                    .build();

            aiResponse = fastApiClient.analyzeRisk(fastApiReq);

            log.info("FastAPI result — isHighRisk: {}, riskLevel: {}, detectedRisks: {}, confidence: {}",
                    aiResponse.getIsHighRisk(),
                    aiResponse.getRiskLevel(),
                    aiResponse.getDetectedRisks(),
                    aiResponse.getConfidence());

        } catch (FastApiException e) {
            log.error("FastAPI failed for visitId: {}. Error: {}", entity.getId(), e.getMessage());
            // aiResponse = null → enrichWithAiResponse will set status = AI_FAILED
        }

        // Step 4 & 5 — Enrich and re-save
        mapper.enrichWithAiResponse(entity, aiResponse);
        entity = visitRepository.save(entity);
        log.info("Visit updated — ID: {}, Status: {}", entity.getId(), entity.getStatus());

        // Step 6 — Return to React
        return mapper.toResponseDTO(entity, aiResponse);
    }

    public List<AncVisitEntity> getVisitsByPatient(String patientId) {
        return visitRepository.findByPatientIdOrderByCreatedAtDesc(patientId);
    }

    public AncVisitEntity getVisitById(String visitId) {
        return visitRepository.findById(visitId)
                .orElseThrow(() -> new RuntimeException("Visit not found: " + visitId));
    }

    /** isHighRisk = true visits (CRITICAL + HIGH) */
    public List<AncVisitEntity> getHighRiskVisits() {
        return visitRepository.findByIsHighRiskTrueOrderByCreatedAtDesc();
    }

    /** CRITICAL only — for urgent alert panel */
    public List<AncVisitEntity> getCriticalVisits() {
        return visitRepository.findAllCriticalVisits();
    }
}
```

---

## controller/AncVisitController.java  ← UPDATED: added /critical endpoint

```java
package com.anc.controller;

import com.anc.dto.AncVisitRequestDTO;
import com.anc.dto.AncVisitResponseDTO;
import com.anc.entity.AncVisitEntity;
import com.anc.service.AncVisitService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/anc")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")   // lock down to React origin in production
public class AncVisitController {

    private final AncVisitService visitService;

    /**
     * POST /api/anc/register-visit
     *
     * Main endpoint. React sends structured_data after ANC worker
     * completes the form. Returns full risk assessment to display.
     *
     * Response:
     *  visitId, patientId, patientName, status, savedAt, message,
     *  riskAssessment {
     *    isHighRisk, riskLevel, detectedRisks[],
     *    explanation, confidence, recommendation,
     *    patientId, patientName, age, gestationalWeeks, visitMetadata
     *  }
     */
    @PostMapping("/register-visit")
    public ResponseEntity<AncVisitResponseDTO> registerVisit(
            @Valid @RequestBody AncVisitRequestDTO request) {

        log.info("Registration request for patient: {}", request.getPatientId());
        AncVisitResponseDTO response = visitService.registerVisit(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * GET /api/anc/visits/{visitId}
     */
    @GetMapping("/visits/{visitId}")
    public ResponseEntity<AncVisitEntity> getVisit(@PathVariable String visitId) {
        return ResponseEntity.ok(visitService.getVisitById(visitId));
    }

    /**
     * GET /api/anc/patients/{patientId}/visits
     * Full visit history, newest first.
     */
    @GetMapping("/patients/{patientId}/visits")
    public ResponseEntity<List<AncVisitEntity>> getPatientVisits(@PathVariable String patientId) {
        return ResponseEntity.ok(visitService.getVisitsByPatient(patientId));
    }

    /**
     * GET /api/anc/visits/high-risk
     * All visits where isHighRisk = true (CRITICAL + HIGH).
     * Used by supervisor dashboard.
     */
    @GetMapping("/visits/high-risk")
    public ResponseEntity<List<AncVisitEntity>> getHighRiskVisits() {
        return ResponseEntity.ok(visitService.getHighRiskVisits());
    }

    /**
     * GET /api/anc/visits/critical
     * CRITICAL risk visits only — urgent alert panel.
     */
    @GetMapping("/visits/critical")
    public ResponseEntity<List<AncVisitEntity>> getCriticalVisits() {
        return ResponseEntity.ok(visitService.getCriticalVisits());
    }
}
```

---

## FastAPI Field → Spring Boot Mapping Reference

| FastAPI JSON Field | Java Type | DB Column | Entity Field | Stored? |
|---|---|---|---|---|
| `isHighRisk` | `Boolean` | `is_high_risk` | `isHighRisk` | ✅ |
| `riskLevel` | `String` | `risk_level` | `riskLevel` | ✅ |
| `detectedRisks` | `List<String>` | `detected_risks` JSONB | `detectedRisks` | ✅ |
| `explanation` | `String` | `explanation` | `explanation` | ✅ |
| `confidence` | `Double` | `confidence` | `confidence` | ✅ |
| `recommendation` | `String` | `recommendation` | `recommendation` | ✅ |
| `visitMetadata` | `Map<String,Object>` | `visit_metadata` JSONB | `visitMetadata` | ✅ |
| `patientId` | `String` | `patient_id` | `patientId` | ✅ (from request) |
| `patientName` | `String` | `patient_name` | `patientName` | ✅ (from request) |
| `age` | `Integer` | _(in structured_data)_ | — | via JSONB |
| `gestationalWeeks` | `Integer` | _(in structured_data)_ | — | via JSONB |

---

## Sample Final Response to React

```json
{
  "visitId": "550e8400-e29b-41d4-a716-446655440000",
  "patientId": "patient-123",
  "patientName": null,
  "status": "AI_ANALYZED",
  "message": "ALERT: High risk pregnancy detected — CRITICAL. Immediate action required.",
  "savedAt": "2026-02-21T10:30:00",
  "riskAssessment": {
    "isHighRisk": true,
    "riskLevel": "CRITICAL",
    "detectedRisks": [
      "Severe Anaemia",
      "Severe Pre Eclampsia",
      "GDM Screening Overdue",
      "Elderly Gravida",
      "Twin Pregnancy"
    ],
    "explanation": "Risk Assessment: CRITICAL. Patient presents with 5 significant risk factors...",
    "confidence": 0.7,
    "recommendation": "URGENT: Immediate referral to CEmOC/District Hospital required.",
    "patientId": null,
    "patientName": null,
    "age": 38,
    "gestationalWeeks": 30,
    "visitMetadata": null
  }
}
```
