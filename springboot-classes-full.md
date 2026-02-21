# Spring Boot ANC Service - Complete Class Reference (with Full Source Code)

## Project Package: `com.anc`
## Stack: Spring Boot 3.2 + PostgreSQL + RestTemplate → FastAPI

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
│   └── FastApiResponseDTO.java
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
  1. ClinicalSummaryBuilder.build()       → auto-generates clinical_summary
  2. AncVisitMapper.toEntity()            → DTO → Entity
  3. AncVisitRepository.save()            → Save to PostgreSQL (status=REGISTERED)
  4. FastApiClient.analyzeRisk()          → POST to FastAPI /analyze
  5. AncVisitMapper.enrichWithAiResponse()→ Add risk data to entity
  6. AncVisitRepository.save()            → Update PostgreSQL (status=AI_ANALYZED)
  7. AncVisitMapper.toResponseDTO()       → Build response
        ↓
React receives AncVisitResponseDTO
```

---

## REST Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/anc/register-visit` | Register new visit + trigger AI analysis |
| GET | `/api/anc/visits/{visitId}` | Get single visit |
| GET | `/api/anc/patients/{patientId}/visits` | All visits for patient |
| GET | `/api/anc/visits/high-risk` | All HIGH risk visits |

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
    <name>anc-service</name>
    <description>ANC Patient Registration Service</description>

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
        <!-- JSONB support for PostgreSQL -->
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
      ddl-auto: update        # use 'validate' in prod
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
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id          VARCHAR(255) NOT NULL,
    worker_id           VARCHAR(255),
    phc_id              VARCHAR(255),
    clinical_summary    TEXT,
    structured_data     JSONB NOT NULL,
    risk_level          VARCHAR(10),
    risk_score          INTEGER,
    ai_flags            JSONB,
    ai_recommendations  JSONB,
    rag_context_used    TEXT,
    ai_error_message    TEXT,
    status              VARCHAR(30) DEFAULT 'REGISTERED',
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_anc_visits_patient_id   ON anc_visits(patient_id);
CREATE INDEX idx_anc_visits_worker_id    ON anc_visits(worker_id);
CREATE INDEX idx_anc_visits_risk_level   ON anc_visits(risk_level);
CREATE INDEX idx_anc_visits_created_at   ON anc_visits(created_at DESC);
CREATE INDEX idx_anc_visits_structured   ON anc_visits USING GIN(structured_data);
CREATE INDEX idx_anc_visits_ai_flags     ON anc_visits USING GIN(ai_flags);
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

    @NotNull(message = "Patient ID is required")
    @JsonProperty("patientId")
    private String patientId;

    @JsonProperty("workerId")
    private String workerId;

    @JsonProperty("phcId")
    private String phcId;

    // Optional — auto-generated by ClinicalSummaryBuilder if blank
    @JsonProperty("clinical_summary")
    private String clinicalSummary;

    @Valid
    @NotNull(message = "Structured data is required")
    @JsonProperty("structured_data")
    private StructuredDataDTO structuredData;
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

@Data
@Builder
public class AncVisitResponseDTO {

    @JsonProperty("visitId")
    private String visitId;

    @JsonProperty("patientId")
    private String patientId;

    @JsonProperty("status")
    private String status;

    @JsonProperty("riskAssessment")
    private FastApiResponseDTO riskAssessment;

    @JsonProperty("savedAt")
    private LocalDateTime savedAt;

    @JsonProperty("message")
    private String message;
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

## dto/FastApiResponseDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.util.List;

@Data
public class FastApiResponseDTO {

    @JsonProperty("risk_level")
    private String riskLevel;          // HIGH / MEDIUM / LOW

    @JsonProperty("risk_score")
    private Integer riskScore;         // 0–100

    @JsonProperty("flags")
    private List<String> flags;

    @JsonProperty("recommended_actions")
    private List<String> recommendedActions;

    @JsonProperty("rag_context_used")
    private String ragContextUsed;

    @JsonProperty("error")
    private String error;
}
```

---

## entity/AncVisitEntity.java

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

    @Column(name = "patient_id", nullable = false)
    private String patientId;

    @Column(name = "worker_id")
    private String workerId;

    @Column(name = "phc_id")
    private String phcId;

    @Column(name = "clinical_summary", columnDefinition = "TEXT")
    private String clinicalSummary;

    // Full structured input stored as JSONB
    @Type(JsonBinaryType.class)
    @Column(name = "structured_data", columnDefinition = "jsonb")
    private Map<String, Object> structuredData;

    // AI Risk Assessment fields
    @Column(name = "risk_level", length = 10)
    private String riskLevel;

    @Column(name = "risk_score")
    private Integer riskScore;

    @Type(JsonBinaryType.class)
    @Column(name = "ai_flags", columnDefinition = "jsonb")
    private List<String> aiFlags;

    @Type(JsonBinaryType.class)
    @Column(name = "ai_recommendations", columnDefinition = "jsonb")
    private List<String> aiRecommendations;

    @Column(name = "rag_context_used", columnDefinition = "TEXT")
    private String ragContextUsed;

    // Status: REGISTERED | AI_ANALYZED | AI_FAILED
    @Column(name = "status", length = 30)
    private String status;

    @Column(name = "ai_error_message", columnDefinition = "TEXT")
    private String aiErrorMessage;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
```

---

## repository/AncVisitRepository.java

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

    List<AncVisitEntity> findByRiskLevel(String riskLevel);

    @Query("SELECT v FROM AncVisitEntity v WHERE v.patientId = :patientId ORDER BY v.createdAt DESC LIMIT 1")
    AncVisitEntity findLatestByPatientId(@Param("patientId") String patientId);

    @Query("SELECT COUNT(v) FROM AncVisitEntity v WHERE v.riskLevel = 'HIGH'")
    long countHighRiskVisits();
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

    // Handles @Valid annotation failures
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleValidationErrors(
            MethodArgumentNotValidException ex) {

        Map<String, String> fieldErrors = new HashMap<>();
        ex.getBindingResult().getAllErrors().forEach(error -> {
            String field = ((FieldError) error).getField();
            String message = error.getDefaultMessage();
            fieldErrors.put(field, message);
        });

        return buildErrorResponse(HttpStatus.BAD_REQUEST, "Validation failed", fieldErrors);
    }

    // FastAPI connectivity issues — non-fatal, visit is still saved
    @ExceptionHandler(FastApiException.class)
    public ResponseEntity<Map<String, Object>> handleFastApiException(FastApiException ex) {
        log.error("FastAPI error: {}", ex.getMessage());
        return buildErrorResponse(
                HttpStatus.SERVICE_UNAVAILABLE,
                "AI Risk Analysis service is unavailable",
                null
        );
    }

    // Generic fallback
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
     * Calls FastAPI RAG pipeline /analyze endpoint.
     * Sends clinical_summary + structured_data.
     * Returns risk_level, risk_score, flags, recommended_actions.
     */
    public FastApiResponseDTO analyzeRisk(FastApiRequestDTO request) {
        String url = fastApiBaseUrl + "/analyze";

        log.info("Calling FastAPI at: {}", url);
        log.debug("FastAPI Request: {}", toJson(request));

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

            log.info("FastAPI responded with HTTP status: {}", response.getStatusCode());
            return response.getBody();

        } catch (HttpClientErrorException e) {
            log.error("FastAPI client error {}: {}", e.getStatusCode(), e.getResponseBodyAsString());
            throw new FastApiException("FastAPI returned client error: " + e.getStatusCode(), e);

        } catch (HttpServerErrorException e) {
            log.error("FastAPI server error {}: {}", e.getStatusCode(), e.getResponseBodyAsString());
            throw new FastApiException("FastAPI internal server error: " + e.getStatusCode(), e);

        } catch (ResourceAccessException e) {
            log.error("FastAPI unreachable: {}", e.getMessage());
            throw new FastApiException("FastAPI service is unreachable. Please try again later.", e);
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

## mapper/AncVisitMapper.java

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
     * Convert incoming request DTO → JPA Entity for first DB save.
     * Converts StructuredDataDTO → Map<String, Object> for JSONB storage.
     */
    public AncVisitEntity toEntity(AncVisitRequestDTO request) {
        Map<String, Object> structuredDataMap = objectMapper.convertValue(
                request.getStructuredData(),
                new TypeReference<Map<String, Object>>() {}
        );

        return AncVisitEntity.builder()
                .patientId(request.getPatientId())
                .workerId(request.getWorkerId())
                .phcId(request.getPhcId())
                .clinicalSummary(request.getClinicalSummary())
                .structuredData(structuredDataMap)
                .status("REGISTERED")
                .build();
    }

    /**
     * Enrich entity with FastAPI AI risk assessment results.
     * Called after FastApiClient.analyzeRisk() returns.
     */
    public void enrichWithAiResponse(AncVisitEntity entity, FastApiResponseDTO aiResponse) {
        if (aiResponse == null) {
            entity.setStatus("AI_FAILED");
            entity.setAiErrorMessage("No response from AI service");
            return;
        }

        entity.setRiskLevel(aiResponse.getRiskLevel());
        entity.setRiskScore(aiResponse.getRiskScore());
        entity.setAiFlags(aiResponse.getFlags());
        entity.setAiRecommendations(aiResponse.getRecommendedActions());
        entity.setRagContextUsed(aiResponse.getRagContextUsed());
        entity.setStatus("AI_ANALYZED");

        if (aiResponse.getError() != null) {
            entity.setStatus("AI_FAILED");
            entity.setAiErrorMessage(aiResponse.getError());
        }
    }

    /**
     * Convert saved entity + AI response → DTO returned to React.
     */
    public AncVisitResponseDTO toResponseDTO(AncVisitEntity entity, FastApiResponseDTO aiResponse) {
        return AncVisitResponseDTO.builder()
                .visitId(entity.getId())
                .patientId(entity.getPatientId())
                .status(entity.getStatus())
                .riskAssessment(aiResponse)
                .savedAt(entity.getCreatedAt())
                .message(buildStatusMessage(entity.getStatus()))
                .build();
    }

    private String buildStatusMessage(String status) {
        return switch (status) {
            case "AI_ANALYZED" -> "Visit registered and risk analysis completed successfully";
            case "AI_FAILED"   -> "Visit registered but AI analysis failed. Please retry.";
            default            -> "Visit registered successfully";
        };
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
 * Builds a human-readable clinical summary string from structured_data.
 * This summary drives the RAG context retrieval in FastAPI.
 * React does NOT need to send clinical_summary — it's auto-generated here.
 *
 * Example output for test patient:
 * "38-year-old at 30 weeks with severe hypertension (165/110 mmHg),
 *  severe anemia (Hb 6.5 g/dL), twin pregnancy, grand multipara (G6),
 *  previous stillbirth, Rh-negative, proteinuria, headache, visual disturbances, smoker"
 */
@Component
public class ClinicalSummaryBuilder {

    public String build(StructuredDataDTO data) {
        if (data == null) return "ANC visit - no structured data available";

        List<String> parts = new ArrayList<>();

        // ── Patient demographics ───────────────────────────────────────────
        if (data.getPatientInfo() != null) {
            PatientInfoDTO p = data.getPatientInfo();
            parts.add(p.getAge() + "-year-old at " + p.getGestationalWeeks() + " weeks gestation");
        }

        // ── Vitals flags ───────────────────────────────────────────────────
        if (data.getVitals() != null) {
            VitalsDTO v = data.getVitals();
            if (v.getBpSystolic() != null && v.getBpSystolic() >= 160) {
                parts.add("severe hypertension (" + v.getBpSystolic() + "/" + v.getBpDiastolic() + " mmHg)");
            } else if (v.getBpSystolic() != null && v.getBpSystolic() >= 140) {
                parts.add("hypertension (" + v.getBpSystolic() + "/" + v.getBpDiastolic() + " mmHg)");
            }
            if (v.getBmi() != null && v.getBmi() >= 30) {
                parts.add("obese (BMI " + v.getBmi() + ")");
            }
            if (v.getHeightCm() != null && v.getHeightCm() < 140) {
                parts.add("short stature (" + v.getHeightCm() + " cm)");
            }
        }

        // ── Lab flags ──────────────────────────────────────────────────────
        if (data.getLabReports() != null) {
            LabReportsDTO l = data.getLabReports();
            if (l.getHemoglobin() != null) {
                if (l.getHemoglobin() < 7) {
                    parts.add("severe anemia (Hb " + l.getHemoglobin() + " g/dL)");
                } else if (l.getHemoglobin() < 11) {
                    parts.add("anemia (Hb " + l.getHemoglobin() + " g/dL)");
                }
            }
            if (Boolean.TRUE.equals(l.getUrineProtein()))  parts.add("proteinuria");
            if (Boolean.TRUE.equals(l.getRhNegative()))    parts.add("Rh-negative");
            if (Boolean.TRUE.equals(l.getHivPositive()))   parts.add("HIV positive");
            if (Boolean.TRUE.equals(l.getSyphilisPositive())) parts.add("syphilis positive");
        }

        // ── Obstetric history flags ────────────────────────────────────────
        if (data.getObstetricHistory() != null) {
            ObstetricHistoryDTO o = data.getObstetricHistory();
            if (o.getBirthOrder() != null && o.getBirthOrder() >= 5) {
                parts.add("grand multipara (G" + o.getBirthOrder() + ")");
            }
            if (o.getInterPregnancyInterval() != null && o.getInterPregnancyInterval() < 18) {
                parts.add("short inter-pregnancy interval (" + o.getInterPregnancyInterval() + " months)");
            }
        }

        // ── Pregnancy-specific flags ───────────────────────────────────────
        if (data.getPregnancyDetails() != null) {
            PregnancyDetailsDTO pr = data.getPregnancyDetails();
            if (Boolean.TRUE.equals(pr.getTwinPregnancy()))             parts.add("twin pregnancy");
            if (Boolean.TRUE.equals(pr.getPlacentaPrevia()))            parts.add("placenta previa");
            if (Boolean.TRUE.equals(pr.getMalpresentation()))           parts.add("malpresentation");
            if (Boolean.TRUE.equals(pr.getUmbilicalDopplerAbnormal()))  parts.add("abnormal umbilical Doppler");
            if (Boolean.TRUE.equals(pr.getReducedFetalMovement()))      parts.add("reduced fetal movements");
        }

        // ── Medical history flags ──────────────────────────────────────────
        if (data.getMedicalHistory() != null) {
            MedicalHistoryDTO m = data.getMedicalHistory();
            if (Boolean.TRUE.equals(m.getPreviousStillbirth()))   parts.add("previous stillbirth");
            if (Boolean.TRUE.equals(m.getPreviousLscs()))         parts.add("previous LSCS");
            if (Boolean.TRUE.equals(m.getBadObstetricHistory()))  parts.add("bad obstetric history");
            if (Boolean.TRUE.equals(m.getChronicHypertension()))  parts.add("chronic hypertension");
            if (Boolean.TRUE.equals(m.getDiabetes()))             parts.add("diabetes");
            if (Boolean.TRUE.equals(m.getThyroidDisorder()))      parts.add("thyroid disorder");
            if (Boolean.TRUE.equals(m.getSmoking()))              parts.add("smoker");
            if (Boolean.TRUE.equals(m.getTobaccoUse()))           parts.add("tobacco use");
            if (Boolean.TRUE.equals(m.getAlcoholUse()))           parts.add("alcohol use");
            if (m.getSystemicIllness() != null
                    && !m.getSystemicIllness().isBlank()
                    && !m.getSystemicIllness().equalsIgnoreCase("None")) {
                parts.add("systemic illness: " + m.getSystemicIllness());
            }
        }

        // ── Current symptoms ───────────────────────────────────────────────
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

        // First part = base sentence; remaining = comma-joined complications
        String base = parts.get(0);
        if (parts.size() == 1) return base;

        List<String> complications = parts.subList(1, parts.size());
        return base + " with " + String.join(", ", complications);
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
     * Main entry point called by the controller.
     *
     * Flow:
     *  1. Auto-generate clinical_summary if not provided by React
     *  2. Map DTO → Entity, save to DB (status = REGISTERED)
     *  3. Call FastAPI RAG pipeline for risk analysis
     *  4. Update entity with AI results, save again (status = AI_ANALYZED or AI_FAILED)
     *  5. Return combined response to React
     *
     * AI failure is intentionally non-blocking:
     * the visit is saved regardless of FastAPI availability.
     */
    @Transactional
    public AncVisitResponseDTO registerVisit(AncVisitRequestDTO request) {

        log.info("Registering ANC visit for patient: {}", request.getPatientId());

        // Step 1: Auto-generate clinical summary if blank
        if (request.getClinicalSummary() == null || request.getClinicalSummary().isBlank()) {
            String generatedSummary = summaryBuilder.build(request.getStructuredData());
            request.setClinicalSummary(generatedSummary);
            log.debug("Auto-generated clinical summary: {}", generatedSummary);
        }

        // Step 2: Save initial visit record to DB
        AncVisitEntity visitEntity = mapper.toEntity(request);
        visitEntity = visitRepository.save(visitEntity);
        log.info("Visit saved to DB — ID: {}, Status: REGISTERED", visitEntity.getId());

        // Step 3: Call FastAPI RAG pipeline
        FastApiResponseDTO aiResponse = null;
        try {
            FastApiRequestDTO fastApiRequest = FastApiRequestDTO.builder()
                    .clinicalSummary(request.getClinicalSummary())
                    .structuredData(request.getStructuredData())
                    .build();

            aiResponse = fastApiClient.analyzeRisk(fastApiRequest);
            log.info("FastAPI analysis complete — Risk Level: {}, Score: {}",
                    aiResponse.getRiskLevel(), aiResponse.getRiskScore());

        } catch (FastApiException e) {
            // Non-blocking: log error, visit remains saved with status AI_FAILED
            log.error("FastAPI call failed for visitId: {}. Error: {}", visitEntity.getId(), e.getMessage());
        }

        // Step 4: Enrich entity with AI results and update DB
        mapper.enrichWithAiResponse(visitEntity, aiResponse);
        visitEntity = visitRepository.save(visitEntity);
        log.info("Visit updated — ID: {}, Final Status: {}", visitEntity.getId(), visitEntity.getStatus());

        // Step 5: Return combined response to React
        return mapper.toResponseDTO(visitEntity, aiResponse);
    }

    /** Fetch all visits for a patient (visit history) */
    public List<AncVisitEntity> getVisitsByPatient(String patientId) {
        return visitRepository.findByPatientIdOrderByCreatedAtDesc(patientId);
    }

    /** Fetch single visit by ID */
    public AncVisitEntity getVisitById(String visitId) {
        return visitRepository.findById(visitId)
                .orElseThrow(() -> new RuntimeException("Visit not found with ID: " + visitId));
    }

    /** Fetch all HIGH risk visits for supervisor/dashboard alerts */
    public List<AncVisitEntity> getHighRiskVisits() {
        return visitRepository.findByRiskLevel("HIGH");
    }
}
```

---

## controller/AncVisitController.java

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
@CrossOrigin(origins = "*")   // Restrict to your React origin in production
public class AncVisitController {

    private final AncVisitService visitService;

    /**
     * POST /api/anc/register-visit
     *
     * Called by React after ANC worker fills the registration form.
     * Saves visit to PostgreSQL and triggers FastAPI risk analysis.
     *
     * Returns:
     * - visitId, patientId, status
     * - riskAssessment { risk_level, risk_score, flags, recommended_actions }
     * - savedAt, message
     */
    @PostMapping("/register-visit")
    public ResponseEntity<AncVisitResponseDTO> registerVisit(
            @Valid @RequestBody AncVisitRequestDTO request) {

        log.info("Received ANC registration for patient: {}", request.getPatientId());
        AncVisitResponseDTO response = visitService.registerVisit(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * GET /api/anc/visits/{visitId}
     * Retrieve a single visit record by ID.
     */
    @GetMapping("/visits/{visitId}")
    public ResponseEntity<AncVisitEntity> getVisit(@PathVariable String visitId) {
        AncVisitEntity visit = visitService.getVisitById(visitId);
        return ResponseEntity.ok(visit);
    }

    /**
     * GET /api/anc/patients/{patientId}/visits
     * Retrieve full visit history for a patient (most recent first).
     */
    @GetMapping("/patients/{patientId}/visits")
    public ResponseEntity<List<AncVisitEntity>> getPatientVisits(@PathVariable String patientId) {
        List<AncVisitEntity> visits = visitService.getVisitsByPatient(patientId);
        return ResponseEntity.ok(visits);
    }

    /**
     * GET /api/anc/visits/high-risk
     * Retrieve all HIGH risk visits — used by supervisor dashboard.
     */
    @GetMapping("/visits/high-risk")
    public ResponseEntity<List<AncVisitEntity>> getHighRiskVisits() {
        List<AncVisitEntity> visits = visitService.getHighRiskVisits();
        return ResponseEntity.ok(visits);
    }
}
```

---

## Key Design Decisions

| Decision | Detail |
|----------|--------|
| AI failure is non-blocking | Visit always saved; status = `AI_FAILED` if FastAPI down |
| `ClinicalSummaryBuilder` | Auto-generates rich RAG query string from structured_data — React doesn't send it |
| JSONB storage | `structured_data`, `ai_flags`, `ai_recommendations` stored as native PostgreSQL JSONB |
| GIN indexes | Fast querying on JSONB columns |
| `@Transactional` | Both DB saves (REGISTERED + AI_ANALYZED) in one transaction scope |
| Status lifecycle | `REGISTERED` → `AI_ANALYZED` or `AI_FAILED` |
| `X-API-KEY` header | Spring Boot authenticates to FastAPI via shared secret |
| `@CrossOrigin("*")` | Change to React origin URL in production |

---

## Sample Auto-Generated Clinical Summary for Test Patient

**Input JSON** → **ClinicalSummaryBuilder output:**

```
38-year-old at 30 weeks gestation with severe hypertension (165/110 mmHg),
obese (BMI 32), short stature (135 cm), severe anemia (Hb 6.5 g/dL),
proteinuria, Rh-negative, grand multipara (G6), short inter-pregnancy interval
(8 months), twin pregnancy, previous stillbirth, smoker, headache, visual disturbances
```

This string is sent as `clinical_summary` to FastAPI for RAG retrieval against the PMSMA PDFs.
