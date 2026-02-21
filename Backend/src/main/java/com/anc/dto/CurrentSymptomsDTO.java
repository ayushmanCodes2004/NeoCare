package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class CurrentSymptomsDTO {

    @JsonProperty("headache")
    private Boolean headache;

    @JsonProperty("visualDisturbance")
    private Boolean visualDisturbance;

    @JsonProperty("epigastricPain")
    private Boolean epigastricPain;

    @JsonProperty("decreasedUrineOutput")
    private Boolean decreasedUrineOutput;

    @JsonProperty("bleedingPerVagina")
    private Boolean bleedingPerVagina;

    @JsonProperty("convulsions")
    private Boolean convulsions;
}
