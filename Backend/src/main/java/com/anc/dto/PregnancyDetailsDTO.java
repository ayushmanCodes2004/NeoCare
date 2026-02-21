package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class PregnancyDetailsDTO {

    @JsonProperty("twinPregnancy")
    private Boolean twinPregnancy;

    @JsonProperty("malpresentation")
    private Boolean malpresentation;

    @JsonProperty("placentaPrevia")
    private Boolean placentaPrevia;

    @JsonProperty("reducedFetalMovement")
    private Boolean reducedFetalMovement;

    @JsonProperty("amnioticFluidNormal")
    private Boolean amnioticFluidNormal;

    @JsonProperty("umbilicalDopplerAbnormal")
    private Boolean umbilicalDopplerAbnormal;
}
