package com.anc.service;

import com.anc.dto.*;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

@Component
public class ClinicalSummaryBuilder {

    public String build(StructuredDataDTO data) {
        if (data == null) return "ANC visit - no structured data available";

        List<String> parts = new ArrayList<>();

        // Patient demographics
        if (data.getPatientInfo() != null) {
            PatientInfoDTO p = data.getPatientInfo();
            parts.add(p.getAge() + "-year-old at " + p.getGestationalWeeks() + " weeks gestation");
        }

        // Vitals flags
        if (data.getVitals() != null) {
            VitalsDTO v = data.getVitals();
            if (v.getBpSystolic() != null && v.getBpSystolic() >= 160) {
                parts.add("severe hypertension (" + v.getBpSystolic() + "/" + v.getBpDiastolic() + " mmHg)");
            } else if (v.getBpSystolic() != null && v.getBpSystolic() >= 140) {
                parts.add("hypertension (" + v.getBpSystolic() + "/" + v.getBpDiastolic() + " mmHg)");
            }
            if (v.getBmi() != null && v.getBmi() >= 30) {
                parts.add("obese (BMI " + v.getBmi() + ")");
            }
            if (v.getHeightCm() != null && v.getHeightCm() < 140) {
                parts.add("short stature (" + v.getHeightCm() + " cm)");
            }
        }

        // Lab flags
        if (data.getLabReports() != null) {
            LabReportsDTO l = data.getLabReports();
            if (l.getHemoglobin() != null) {
                if (l.getHemoglobin() < 7) {
                    parts.add("severe anemia (Hb " + l.getHemoglobin() + " g/dL)");
                } else if (l.getHemoglobin() < 11) {
                    parts.add("anemia (Hb " + l.getHemoglobin() + " g/dL)");
                }
            }
            if (Boolean.TRUE.equals(l.getUrineProtein())) parts.add("proteinuria");
            if (Boolean.TRUE.equals(l.getRhNegative())) parts.add("Rh-negative");
            if (Boolean.TRUE.equals(l.getHivPositive())) parts.add("HIV positive");
            if (Boolean.TRUE.equals(l.getSyphilisPositive())) parts.add("syphilis positive");
        }

        // Obstetric history flags
        if (data.getObstetricHistory() != null) {
            ObstetricHistoryDTO o = data.getObstetricHistory();
            if (o.getBirthOrder() != null && o.getBirthOrder() >= 5) {
                parts.add("grand multipara (G" + o.getBirthOrder() + ")");
            }
            if (o.getInterPregnancyInterval() != null && o.getInterPregnancyInterval() < 18) {
                parts.add("short inter-pregnancy interval (" + o.getInterPregnancyInterval() + " months)");
            }
        }

        // Pregnancy-specific flags
        if (data.getPregnancyDetails() != null) {
            PregnancyDetailsDTO pr = data.getPregnancyDetails();
            if (Boolean.TRUE.equals(pr.getTwinPregnancy())) parts.add("twin pregnancy");
            if (Boolean.TRUE.equals(pr.getPlacentaPrevia())) parts.add("placenta previa");
            if (Boolean.TRUE.equals(pr.getMalpresentation())) parts.add("malpresentation");
            if (Boolean.TRUE.equals(pr.getUmbilicalDopplerAbnormal())) parts.add("abnormal umbilical Doppler");
            if (Boolean.TRUE.equals(pr.getReducedFetalMovement())) parts.add("reduced fetal movements");
        }

        // Medical history flags
        if (data.getMedicalHistory() != null) {
            MedicalHistoryDTO m = data.getMedicalHistory();
            if (Boolean.TRUE.equals(m.getPreviousStillbirth())) parts.add("previous stillbirth");
            if (Boolean.TRUE.equals(m.getPreviousLscs())) parts.add("previous LSCS");
            if (Boolean.TRUE.equals(m.getBadObstetricHistory())) parts.add("bad obstetric history");
            if (Boolean.TRUE.equals(m.getChronicHypertension())) parts.add("chronic hypertension");
            if (Boolean.TRUE.equals(m.getDiabetes())) parts.add("diabetes");
            if (Boolean.TRUE.equals(m.getThyroidDisorder())) parts.add("thyroid disorder");
            if (Boolean.TRUE.equals(m.getSmoking())) parts.add("smoker");
            if (Boolean.TRUE.equals(m.getTobaccoUse())) parts.add("tobacco use");
            if (Boolean.TRUE.equals(m.getAlcoholUse())) parts.add("alcohol use");
            if (m.getSystemicIllness() != null
                    && !m.getSystemicIllness().isBlank()
                    && !m.getSystemicIllness().equalsIgnoreCase("None")) {
                parts.add("systemic illness: " + m.getSystemicIllness());
            }
        }

        // Current symptoms
        if (data.getCurrentSymptoms() != null) {
            CurrentSymptomsDTO s = data.getCurrentSymptoms();
            if (Boolean.TRUE.equals(s.getConvulsions())) parts.add("convulsions");
            if (Boolean.TRUE.equals(s.getHeadache())) parts.add("headache");
            if (Boolean.TRUE.equals(s.getVisualDisturbance())) parts.add("visual disturbances");
            if (Boolean.TRUE.equals(s.getEpigastricPain())) parts.add("epigastric pain");
            if (Boolean.TRUE.equals(s.getDecreasedUrineOutput())) parts.add("decreased urine output");
            if (Boolean.TRUE.equals(s.getBleedingPerVagina())) parts.add("bleeding per vagina");
        }

        if (parts.isEmpty()) return "ANC visit with no significant findings";

        String base = parts.get(0);
        if (parts.size() == 1) return base;

        String complications = String.join(", ", parts.subList(1, parts.size()));
        return base + " with " + complications;
    }
}
