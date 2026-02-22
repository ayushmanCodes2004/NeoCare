package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * Doctor signup request:
 * {
 *   "fullName":       "Dr. Priya Sharma",
 *   "phone":          "9988776655",
 *   "email":          "priya@hospital.in",
 *   "password":       "SecurePass123",
 *   "specialization": "Obstetrics & Gynaecology",
 *   "hospital":       "District Hospital Bangalore Rural",
 *   "district":       "Bangalore Rural",
 *   "registrationNo": "KA-12345"
 * }
 */
@Data
public class DoctorSignupRequestDTO {

    @NotBlank(message = "Full name is required")
    @JsonProperty("fullName")
    private String fullName;

    @NotBlank(message = "Phone number is required")
    @Pattern(regexp = "^[6-9]\\d{9}$", message = "Enter a valid 10-digit Indian mobile number")
    @JsonProperty("phone")
    private String phone;

    @Email(message = "Enter a valid email address")
    @JsonProperty("email")
    private String email;

    @NotBlank(message = "Password is required")
    @Size(min = 8, message = "Password must be at least 8 characters")
    @JsonProperty("password")
    private String password;

    @JsonProperty("specialization")
    private String specialization;

    @NotBlank(message = "Hospital name is required")
    @JsonProperty("hospital")
    private String hospital;

    @NotBlank(message = "District is required")
    @JsonProperty("district")
    private String district;

    @JsonProperty("registrationNo")
    private String registrationNo;
}
