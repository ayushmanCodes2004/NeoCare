package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class MedicalHistoryDTO {

    @JsonProperty("previousLSCS")
    private Boolean previousLscs;

    @JsonProperty("badObstetricHistory")
    private Boolean badObstetricHistory;

    @JsonProperty("previousStillbirth")
    private Boolean previousStillbirth;

    @JsonProperty("previousPretermDelivery")
    private Boolean previousPretermDelivery;

    @JsonProperty("previousAbortion")
    private Boolean previousAbortion;

    @JsonProperty("systemicIllness")
    private String systemicIllness;

    @JsonProperty("chronicHypertension")
    private Boolean chronicHypertension;

    @JsonProperty("diabetes")
    private Boolean diabetes;

    @JsonProperty("thyroidDisorder")
    private Boolean thyroidDisorder;

    @JsonProperty("smoking")
    private Boolean smoking;

    @JsonProperty("tobaccoUse")
    private Boolean tobaccoUse;

    @JsonProperty("alcoholUse")
    private Boolean alcoholUse;
}
