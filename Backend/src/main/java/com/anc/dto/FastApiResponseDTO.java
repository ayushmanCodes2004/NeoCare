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
 * 
 * Also includes frontend-compatible fields for display
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

    // ============================================================
    // Frontend-compatible fields (computed from above)
    // ============================================================

    /** Frontend expects: risk_level (same as riskLevel) */
    @JsonProperty("risk_level")
    public String getRisk_level() {
        return riskLevel;
    }

    /** Frontend expects: risk_score (0-100, computed from confidence and riskLevel) */
    @JsonProperty("risk_score")
    public Integer getRisk_score() {
        if (riskLevel == null) {
            return confidence != null ? (int)(confidence * 100) : 0;
        }
        switch (riskLevel.toUpperCase()) {
            case "CRITICAL": return 95;
            case "HIGH": return 75;
            case "MEDIUM": return 50;
            case "LOW": return 25;
            default: return confidence != null ? (int)(confidence * 100) : 0;
        }
    }

    /** Frontend expects: risk_factors (same as detectedRisks) */
    @JsonProperty("risk_factors")
    public List<String> getRisk_factors() {
        return detectedRisks;
    }

    /** Frontend expects: recommendations (array, convert single recommendation to array) */
    @JsonProperty("recommendations")
    public List<String> getRecommendations() {
        if (recommendation == null || recommendation.isBlank()) {
            return List.of();
        }
        // Split by newlines or periods to create multiple recommendations
        return List.of(recommendation);
    }

    /** Frontend expects: requires_doctor_consultation (same as isHighRisk) */
    @JsonProperty("requires_doctor_consultation")
    public Boolean getRequires_doctor_consultation() {
        return isHighRisk != null ? isHighRisk : false;
    }

    /** Frontend expects: urgency (computed from riskLevel) */
    @JsonProperty("urgency")
    public String getUrgency() {
        if (riskLevel == null) return "routine";
        switch (riskLevel.toUpperCase()) {
            case "CRITICAL": return "emergency";
            case "HIGH": return "urgent";
            case "MEDIUM": return "soon";
            case "LOW": return "routine";
            default: return "routine";
        }
    }

    /** Frontend expects: summary (same as explanation) */
    @JsonProperty("summary")
    public String getSummary() {
        return explanation;
    }
}
