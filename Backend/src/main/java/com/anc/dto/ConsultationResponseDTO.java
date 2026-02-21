package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ConsultationResponseDTO {

    @JsonProperty("consultationId")
    private UUID consultationId;

    @JsonProperty("patientId")
    private UUID patientId;

    @JsonProperty("patientName")
    private String patientName;

    @JsonProperty("workerId")
    private UUID workerId;

    @JsonProperty("workerName")
    private String workerName;

    @JsonProperty("doctorId")
    private UUID doctorId;

    @JsonProperty("doctorName")
    private String doctorName;

    @JsonProperty("visitId")
    private String visitId;

    @JsonProperty("status")
    private String status;

    @JsonProperty("riskLevel")
    private String riskLevel;

    @JsonProperty("roomId")
    private String roomId;

    @JsonProperty("scheduledAt")
    private LocalDateTime scheduledAt;

    @JsonProperty("startedAt")
    private LocalDateTime startedAt;

    @JsonProperty("completedAt")
    private LocalDateTime completedAt;

    @JsonProperty("doctorNotes")
    private String doctorNotes;

    @JsonProperty("prescription")
    private String prescription;

    @JsonProperty("recommendations")
    private String recommendations;

    @JsonProperty("createdAt")
    private LocalDateTime createdAt;
}
