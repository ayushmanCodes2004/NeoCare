package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Builder;
import lombok.Data;

/**
 * Returned to React after doctor signup/login.
 * role = "DOCTOR" — React uses this to show the doctor portal UI.
 */
@Data
@Builder
public class DoctorAuthResponseDTO {

    @JsonProperty("token")
    private String token;

    @JsonProperty("role")
    private String role;               // always "DOCTOR"

    @JsonProperty("doctorId")
    private String doctorId;

    @JsonProperty("fullName")
    private String fullName;

    @JsonProperty("phone")
    private String phone;

    @JsonProperty("email")
    private String email;

    @JsonProperty("specialization")
    private String specialization;

    @JsonProperty("hospital")
    private String hospital;

    @JsonProperty("district")
    private String district;

    @JsonProperty("registrationNo")
    private String registrationNo;

    @JsonProperty("isAvailable")
    private Boolean isAvailable;

    @JsonProperty("message")
    private String message;
}
