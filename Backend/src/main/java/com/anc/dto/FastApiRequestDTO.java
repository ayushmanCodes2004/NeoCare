package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FastApiRequestDTO {

    @JsonProperty("clinical_summary")
    private String clinicalSummary;

    @JsonProperty("structured_data")
    private StructuredDataDTO structuredData;
}
