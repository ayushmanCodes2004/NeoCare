package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Full consultation response sent to React.
 * Includes embedded patient snapshot and visit risk data
 * so the doctor doesn't need to make separate API calls.
 */
@Data
@Builder
public class ConsultationResponseDTO {

    @JsonProperty("consultationId")
    private String consultationId;

    @JsonProperty("status")
    private String status;

    @JsonProperty("riskLevel")
    private String riskLevel;

    @JsonProperty("isHighRisk")
    private Boolean isHighRisk;

    @JsonProperty("priorityScore")
    private Integer priorityScore;

    // ─── Patient snapshot ─────────────────────────────────────────────────────
    @JsonProperty("patientId")
    private String patientId;

    @JsonProperty("patientName")
    private String patientName;

    @JsonProperty("patientAge")
    private Integer patientAge;

    @JsonProperty("patientPhone")
    private String patientPhone;

    @JsonProperty("village")
    private String village;

    @JsonProperty("district")
    private String district;

    @JsonProperty("bloodGroup")
    private String bloodGroup;

    // ─── Visit + AI risk data ─────────────────────────────────────────────────
    @JsonProperty("visitId")
    private String visitId;

    @JsonProperty("gestationalWeeks")
    private Integer gestationalWeeks;

    @JsonProperty("detectedRisks")
    private List<String> detectedRisks;

    @JsonProperty("explanation")
    private String explanation;

    @JsonProperty("confidence")
    private Double confidence;

    @JsonProperty("recommendation")
    private String recommendation;

    // ─── Worker info ──────────────────────────────────────────────────────────
    @JsonProperty("workerId")
    private String workerId;

    @JsonProperty("workerName")
    private String workerName;

    @JsonProperty("workerPhone")
    private String workerPhone;

    @JsonProperty("healthCenter")
    private String healthCenter;

    // ─── Doctor info ──────────────────────────────────────────────────────────
    @JsonProperty("doctorId")
    private String doctorId;

    @JsonProperty("doctorName")
    private String doctorName;

    // ─── Video call ───────────────────────────────────────────────────────────
    @JsonProperty("roomUrl")
    private String roomUrl;

    @JsonProperty("doctorToken")
    private String doctorToken;

    @JsonProperty("workerToken")
    private String workerToken;

    // ─── Doctor notes ─────────────────────────────────────────────────────────
    @JsonProperty("doctorNotes")
    private String doctorNotes;

    @JsonProperty("diagnosis")
    private String diagnosis;

    @JsonProperty("actionPlan")
    private String actionPlan;

    // ─── Timestamps ───────────────────────────────────────────────────────────
    @JsonProperty("acceptedAt")
    private LocalDateTime acceptedAt;

    @JsonProperty("callStartedAt")
    private LocalDateTime callStartedAt;

    @JsonProperty("completedAt")
    private LocalDateTime completedAt;

    @JsonProperty("createdAt")
    private LocalDateTime createdAt;
}
