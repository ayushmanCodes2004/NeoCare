package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class LabReportsDTO {

    @JsonProperty("hemoglobin")
    private Double hemoglobin;

    @JsonProperty("rhNegative")
    private Boolean rhNegative;

    @JsonProperty("hivPositive")
    private Boolean hivPositive;

    @JsonProperty("syphilisPositive")
    private Boolean syphilisPositive;

    @JsonProperty("urineProtein")
    private Boolean urineProtein;

    @JsonProperty("urineSugar")
    private Boolean urineSugar;
}
