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
public class WorkerProfileResponseDTO {

    @JsonProperty("workerId")
    private UUID workerId;

    @JsonProperty("fullName")
    private String fullName;

    @JsonProperty("phone")
    private String phone;

    @JsonProperty("email")
    private String email;

    @JsonProperty("healthCenter")
    private String healthCenter;

    @JsonProperty("district")
    private String district;

    @JsonProperty("message")
    private String message;
}
