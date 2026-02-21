package com.anc.mapper;

import com.anc.dto.AncVisitRequestDTO;
import com.anc.dto.AncVisitResponseDTO;
import com.anc.dto.FastApiResponseDTO;
import com.anc.entity.AncVisitEntity;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.Map;

@Slf4j
@Component
@RequiredArgsConstructor
public class AncVisitMapper {

    private final ObjectMapper objectMapper;

    /**
     * DTO → Entity for first DB save (status = REGISTERED).
     * Converts StructuredDataDTO to Map<String, Object> for JSONB storage.
     */
    public AncVisitEntity toEntity(AncVisitRequestDTO request) {
        Map<String, Object> structuredDataMap = objectMapper.convertValue(
                request.getStructuredData(),
                new TypeReference<Map<String, Object>>() {}
        );

        return AncVisitEntity.builder()
                .patientId(request.getPatientId())
                .patientName(request.getPatientName())
                .workerId(request.getWorkerId())
                .phcId(request.getPhcId())
                .clinicalSummary(request.getClinicalSummary())
                .structuredData(structuredDataMap)
                .status("REGISTERED")
                .build();
    }

    /**
     * Enrich entity with actual FastAPI response fields.
     *
     * Maps every field from the real FastAPI output:
     *   isHighRisk, riskLevel, detectedRisks, explanation,
     *   confidence, recommendation, visitMetadata
     */
    public void enrichWithAiResponse(AncVisitEntity entity, FastApiResponseDTO ai) {
        if (ai == null) {
            entity.setStatus("AI_FAILED");
            entity.setAiErrorMessage("No response received from FastAPI");
            return;
        }

        entity.setIsHighRisk(ai.getIsHighRisk());
        entity.setRiskLevel(ai.getRiskLevel());
        entity.setDetectedRisks(ai.getDetectedRisks());
        entity.setExplanation(ai.getExplanation());
        entity.setConfidence(ai.getConfidence());
        entity.setRecommendation(ai.getRecommendation());
        entity.setVisitMetadata(ai.getVisitMetadata());
        entity.setStatus("AI_ANALYZED");

        log.info("Enriched — isHighRisk: {}, riskLevel: {}, detectedRisks count: {}, confidence: {}",
                ai.getIsHighRisk(),
                ai.getRiskLevel(),
                ai.getDetectedRisks() != null ? ai.getDetectedRisks().size() : 0,
                ai.getConfidence());
    }

    /**
     * Entity + FastAPI response → final DTO for React.
     */
    public AncVisitResponseDTO toResponseDTO(AncVisitEntity entity, FastApiResponseDTO aiResponse) {
        // Populate missing fields in aiResponse from entity/request
        if (aiResponse != null) {
            aiResponse.setPatientId(entity.getPatientId());
            aiResponse.setPatientName(entity.getPatientName());
            // Extract age and gestationalWeeks from structured_data if available
            if (entity.getStructuredData() != null) {
                Map<String, Object> patientInfo = (Map<String, Object>) entity.getStructuredData().get("patient_info");
                if (patientInfo != null) {
                    aiResponse.setAge((Integer) patientInfo.get("age"));
                    aiResponse.setGestationalWeeks((Integer) patientInfo.get("gestationalWeeks"));
                }
            }
        }
        
        return AncVisitResponseDTO.builder()
                .visitId(entity.getId())
                .patientId(entity.getPatientId())
                .patientName(entity.getPatientName())
                .status(entity.getStatus())
                .riskAssessment(aiResponse)
                .savedAt(entity.getCreatedAt())
                .message(buildMessage(entity))
                .build();
    }

    private String buildMessage(AncVisitEntity entity) {
        if ("AI_FAILED".equals(entity.getStatus())) {
            return "Visit registered but AI analysis failed. Please retry.";
        }
        if (Boolean.TRUE.equals(entity.getIsHighRisk())) {
            return "ALERT: High risk pregnancy detected — "
                    + entity.getRiskLevel() + ". Immediate action required.";
        }
        return "Visit registered successfully. Risk level: " + entity.getRiskLevel();
    }
}
