package com.anc.service;

import com.anc.client.FastApiClient;
import com.anc.dto.*;
import com.anc.entity.AncVisitEntity;
import com.anc.mapper.AncVisitMapper;
import com.anc.repository.AncVisitRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class AncVisitService {

    private final AncVisitRepository visitRepository;
    private final AncVisitMapper visitMapper;
    private final ClinicalSummaryBuilder summaryBuilder;
    private final FastApiClient fastApiClient;

    @Transactional
    public AncVisitResponseDTO registerVisit(AncVisitRequestDTO request) {
        log.info("Registering ANC visit for patient: {}", request.getPatientId());

        // 1. Auto-generate clinical summary if not provided
        if (request.getClinicalSummary() == null || request.getClinicalSummary().isBlank()) {
            String generatedSummary = summaryBuilder.build(request.getStructuredData());
            request.setClinicalSummary(generatedSummary);
            log.debug("Auto-generated clinical summary: {}", generatedSummary);
        }

        // 2. Convert DTO to Entity
        AncVisitEntity entity = visitMapper.toEntity(request);

        // 3. Save to DB (status = REGISTERED)
        entity = visitRepository.save(entity);
        log.info("Visit saved with ID: {}", entity.getId());

        // 4. Call FastAPI for AI risk analysis
        FastApiResponseDTO aiResponse = null;
        try {
            FastApiRequestDTO fastApiRequest = FastApiRequestDTO.builder()
                    .clinicalSummary(entity.getClinicalSummary())
                    .structuredData(request.getStructuredData())
                    .build();

            aiResponse = fastApiClient.analyzeRisk(fastApiRequest);
            log.info("AI analysis completed: isHighRisk={}, riskLevel={}, confidence={}", 
                    aiResponse.getIsHighRisk(), aiResponse.getRiskLevel(), aiResponse.getConfidence());

        } catch (Exception e) {
            log.error("FastAPI call failed: {}", e.getMessage(), e);
            aiResponse = new FastApiResponseDTO();
            entity.setAiErrorMessage("AI service unavailable: " + e.getMessage());
        }

        // 5. Enrich entity with AI response
        visitMapper.enrichWithAiResponse(entity, aiResponse);

        // 6. Update DB (status = AI_ANALYZED or AI_FAILED)
        entity = visitRepository.save(entity);

        // 7. Build response DTO
        return visitMapper.toResponseDTO(entity, aiResponse);
    }

    public AncVisitEntity getVisitById(String visitId) {
        return visitRepository.findById(visitId)
                .orElseThrow(() -> new RuntimeException("Visit not found: " + visitId));
    }

    public List<AncVisitEntity> getVisitsByPatientId(String patientId) {
        return visitRepository.findByPatientIdOrderByCreatedAtDesc(patientId);
    }

    public List<AncVisitEntity> getHighRiskVisits() {
        return visitRepository.findByIsHighRiskTrueOrderByCreatedAtDesc();
    }

    public List<AncVisitEntity> getCriticalVisits() {
        return visitRepository.findAllCriticalVisits();
    }

    public List<AncVisitEntity> getVisitsByRiskLevel(String riskLevel) {
        return visitRepository.findByRiskLevelOrderByCreatedAtDesc(riskLevel);
    }
}
