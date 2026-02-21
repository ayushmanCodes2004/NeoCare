package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PatientResponseDTO {

    @JsonProperty("patientId")
    private UUID patientId;

    @JsonProperty("workerId")
    private UUID workerId;

    @JsonProperty("fullName")
    private String fullName;

    @JsonProperty("phone")
    private String phone;

    @JsonProperty("age")
    private Integer age;

    @JsonProperty("address")
    private String address;

    @JsonProperty("village")
    private String village;

    @JsonProperty("district")
    private String district;

    @JsonProperty("lmpDate")
    private LocalDate lmpDate;

    @JsonProperty("eddDate")
    private LocalDate eddDate;

    @JsonProperty("bloodGroup")
    private String bloodGroup;

    @JsonProperty("createdAt")
    private LocalDateTime createdAt;
}
