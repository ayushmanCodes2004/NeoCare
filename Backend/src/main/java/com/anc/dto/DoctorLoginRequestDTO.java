package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.Data;

/**
 * { "phone": "9988776655", "password": "SecurePass123" }
 */
@Data
public class DoctorLoginRequestDTO {

    @NotBlank(message = "Phone number is required")
    @Pattern(regexp = "^[6-9]\\d{9}$", message = "Enter a valid 10-digit Indian mobile number")
    @JsonProperty("phone")
    private String phone;

    @NotBlank(message = "Password is required")
    @JsonProperty("password")
    private String password;
}
