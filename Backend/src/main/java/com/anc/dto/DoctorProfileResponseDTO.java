package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DoctorProfileResponseDTO {

    @JsonProperty("doctorId")
    private UUID doctorId;

    @JsonProperty("fullName")
    private String fullName;

    @JsonProperty("email")
    private String email;

    @JsonProperty("phone")
    private String phone;

    @JsonProperty("specialization")
    private String specialization;

    @JsonProperty("licenseNumber")
    private String licenseNumber;

    @JsonProperty("hospital")
    private String hospital;

    @JsonProperty("district")
    private String district;

    @JsonProperty("yearsOfExperience")
    private Integer yearsOfExperience;

    @JsonProperty("isAvailable")
    private Boolean isAvailable;

    @JsonProperty("role")
    private String role;
}
