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
