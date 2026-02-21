package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class StructuredDataDTO {

    @JsonProperty("patient_info")
    private PatientInfoDTO patientInfo;

    @JsonProperty("medical_history")
    private MedicalHistoryDTO medicalHistory;

    @JsonProperty("vitals")
    private VitalsDTO vitals;

    @JsonProperty("lab_reports")
    private LabReportsDTO labReports;

    @JsonProperty("obstetric_history")
    private ObstetricHistoryDTO obstetricHistory;

    @JsonProperty("pregnancy_details")
    private PregnancyDetailsDTO pregnancyDetails;

    @JsonProperty("current_symptoms")
    private CurrentSymptomsDTO currentSymptoms;
}
