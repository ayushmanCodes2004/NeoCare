package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
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
public class ConsultationRequestDTO {

    @NotNull(message = "Patient ID is required")
    @JsonProperty("patientId")
    private UUID patientId;

    @NotNull(message = "Doctor ID is required")
    @JsonProperty("doctorId")
    private UUID doctorId;

    @NotBlank(message = "Visit ID is required")
    @JsonProperty("visitId")
    private String visitId;

    @NotBlank(message = "Risk level is required")
    @JsonProperty("riskLevel")
    private String riskLevel;

    @JsonProperty("scheduledAt")
    private LocalDateTime scheduledAt;

    @JsonProperty("notes")
    private String notes;
}
