package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import lombok.Data;

import java.time.LocalDate;

@Data
public class PatientRequestDTO {

    @NotBlank(message = "Full name is required")
    @JsonProperty("fullName")
    private String fullName;

    @NotBlank(message = "Phone number is required")
    @Pattern(regexp = "^[6-9]\\d{9}$", message = "Phone number must be a valid 10-digit Indian mobile number starting with 6-9")
    @JsonProperty("phone")
    private String phone;

    @NotNull(message = "Age is required")
    @Min(value = 1, message = "Age must be at least 1")
    @JsonProperty("age")
    private Integer age;

    @NotBlank(message = "Address is required")
    @JsonProperty("address")
    private String address;

    @NotBlank(message = "Village is required")
    @JsonProperty("village")
    private String village;

    @NotBlank(message = "District is required")
    @JsonProperty("district")
    private String district;

    @NotNull(message = "LMP date is required")
    @JsonProperty("lmpDate")
    private LocalDate lmpDate;

    @NotNull(message = "EDD date is required")
    @JsonProperty("eddDate")
    private LocalDate eddDate;

    @JsonProperty("bloodGroup")
    private String bloodGroup;
}
