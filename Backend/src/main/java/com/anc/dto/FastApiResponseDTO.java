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
