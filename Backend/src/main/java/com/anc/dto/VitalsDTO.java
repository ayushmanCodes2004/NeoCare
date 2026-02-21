package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class VitalsDTO {

    @JsonProperty("heightCm")
    private Double heightCm;

    @JsonProperty("bmi")
    private Double bmi;

    @JsonProperty("bpSystolic")
    private Integer bpSystolic;

    @JsonProperty("bpDiastolic")
    private Integer bpDiastolic;
}
