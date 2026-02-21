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
