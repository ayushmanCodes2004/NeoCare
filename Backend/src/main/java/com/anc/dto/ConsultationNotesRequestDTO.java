package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * Doctor submits notes when completing consultation:
 * {
 *   "doctorNotes": "Patient has severe pre-eclampsia with HELLP syndrome features...",
 *   "diagnosis":   "Severe Pre-eclampsia with superimposed anaemia",
 *   "actionPlan":  "1. Immediate referral to CEmOC. 2. IV MgSO4. 3. Blood transfusion."
 * }
 */
@Data
public class ConsultationNotesRequestDTO {

    @NotBlank(message = "Doctor notes are required")
    @JsonProperty("doctorNotes")
    private String doctorNotes;

    @JsonProperty("diagnosis")
    private String diagnosis;

    @NotBlank(message = "Action plan is required")
    @JsonProperty("actionPlan")
    private String actionPlan;
}
