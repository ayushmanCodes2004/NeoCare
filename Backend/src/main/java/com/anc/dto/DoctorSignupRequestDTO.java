package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DoctorSignupRequestDTO {

    @NotBlank(message = "Full name is required")
    @JsonProperty("fullName")
    private String fullName;

    @NotBlank(message = "Email is required")
    @Email(message = "Invalid email format")
    @JsonProperty("email")
    private String email;

    @NotBlank(message = "Phone is required")
    @Pattern(regexp = "^[0-9]{10}$", message = "Phone must be 10 digits")
    @JsonProperty("phone")
    private String phone;

    @NotBlank(message = "Password is required")
    @JsonProperty("password")
    private String password;

    @NotBlank(message = "Specialization is required")
    @JsonProperty("specialization")
    private String specialization;

    @NotBlank(message = "License number is required")
    @JsonProperty("licenseNumber")
    private String licenseNumber;

    @NotBlank(message = "Hospital is required")
    @JsonProperty("hospital")
    private String hospital;

    @NotBlank(message = "District is required")
    @JsonProperty("district")
    private String district;

    @JsonProperty("yearsOfExperience")
    private Integer yearsOfExperience;
}
