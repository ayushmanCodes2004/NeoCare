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
