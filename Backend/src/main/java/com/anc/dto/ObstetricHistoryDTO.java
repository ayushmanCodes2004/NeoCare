package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class ObstetricHistoryDTO {

    @JsonProperty("birthOrder")
    private Integer birthOrder;

    @JsonProperty("interPregnancyInterval")
    private Integer interPregnancyInterval;

    @JsonProperty("stillbirthCount")
    private Integer stillbirthCount;

    @JsonProperty("abortionCount")
    private Integer abortionCount;

    @JsonProperty("pretermHistory")
    private Boolean pretermHistory;
}
