package com.anc.service;

import com.anc.dto.ConsultationNotesRequestDTO;
import com.anc.dto.ConsultationResponseDTO;
import com.anc.entity.*;
import com.anc.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * Consultation Service — Doctor Module
 * 
 * Handles:
 * - Auto-creation of consultations from high-risk visits
 * - Priority queue management (CRITICAL → HIGH → MEDIUM)
 * - Doctor acceptance and video call initiation
 * - Consultation completion with notes
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ConsultationService {

    private final ConsultationRepository consultationRepository;
    private final DoctorRepository doctorRepository;
    private final PatientRepository patientRepository;
    private final AncWorkerRepository workerRepository;
    private final AncVisitRepository visitRepository;

    @Value("${doctor.auto-assign-district:true}")
    private boolean autoAssignDistrict;

    /**
     * Auto-create consultation from high-risk visit.
     * Called by AncVisitService after AI analysis.
     */
    @Transactional
    public ConsultationEntity createFromVisit(AncVisitEntity visit) {
        log.info("Creating consultation for high-risk visit: {}", visit.getId());

        // Check if consultation already exists for this visit
        List<String> activeStatuses = List.of("PENDING", "ACCEPTED", "IN_PROGRESS");
        if (consultationRepository.existsByVisitIdAndStatusIn(visit.getId(), activeStatuses)) {
            log.warn("Consultation already exists for visit: {}", visit.getId());
            throw new RuntimeException("Consultation already exists for this visit");
        }

        // Calculate priority score
        int priorityScore = calculatePriorityScore(visit.getRiskLevel());

        // Build consultation entity
        ConsultationEntity consultation = ConsultationEntity.builder()
                .visitId(visit.getId())
                .patientId(visit.getPatientId())
                .workerId(visit.getWorkerId())
                .doctorId(null)  // Unassigned initially
                .riskLevel(visit.getRiskLevel())
                .isHighRisk(visit.getIsHighRisk())
                .priorityScore(priorityScore)
                .status("PENDING")
                .build();

        consultation = consultationRepository.save(consultation);
        log.info("Consultation created: {} with priority {}", consultation.getId(), priorityScore);

        return consultation;
    }

    /**
     * Get priority queue for doctor.
     * CRITICAL (100) → HIGH (70) → MEDIUM (40), oldest first within same priority.
     */
    public List<ConsultationResponseDTO> getPriorityQueue(String doctorId) {
        log.info("Fetching priority queue for doctor: {}", doctorId);

        DoctorEntity doctor = doctorRepository.findById(doctorId)
                .orElseThrow(() -> new RuntimeException("Doctor not found"));

        List<ConsultationEntity> consultations;

        if (autoAssignDistrict && doctor.getDistrict() != null) {
            // Filter by doctor's district
            consultations = consultationRepository.findPriorityQueueByDistrict(doctor.getDistrict());
            log.debug("Found {} consultations in district: {}", consultations.size(), doctor.getDistrict());
        } else {
            // All pending consultations
            consultations = consultationRepository.findPriorityQueue();
            log.debug("Found {} consultations (all districts)", consultations.size());
        }

        return consultations.stream()
                .map(this::toResponseDTO)
                .collect(Collectors.toList());
    }

    /**
     * Get consultation by ID with full details.
     */
    public ConsultationResponseDTO getById(String consultationId) {
        ConsultationEntity consultation = consultationRepository.findById(consultationId)
                .orElseThrow(() -> new RuntimeException("Consultation not found: " + consultationId));

        return toResponseDTO(consultation);
    }

    /**
     * Doctor accepts a consultation.
     */
    @Transactional
    public ConsultationResponseDTO accept(String consultationId, String doctorId) {
        log.info("Doctor {} accepting consultation {}", doctorId, consultationId);

        ConsultationEntity consultation = consultationRepository.findById(consultationId)
                .orElseThrow(() -> new RuntimeException("Consultation not found"));

        if (!"PENDING".equals(consultation.getStatus())) {
            throw new RuntimeException("Consultation is not in PENDING status");
        }

        // Check if doctor already has an active consultation
        consultationRepository.findByDoctorIdAndStatus(doctorId, "IN_PROGRESS")
                .ifPresent(active -> {
                    throw new RuntimeException("Doctor already has an active consultation");
                });

        consultation.setDoctorId(doctorId);
        consultation.setStatus("ACCEPTED");
        consultation.setAcceptedAt(LocalDateTime.now());

        consultation = consultationRepository.save(consultation);
        log.info("Consultation {} accepted by doctor {}", consultationId, doctorId);

        return toResponseDTO(consultation);
    }

    /**
     * Start video call — using WebRTC peer-to-peer connection.
     * No external service needed, uses STOMP WebSocket signaling.
     */
    @Transactional
    public ConsultationResponseDTO startCall(String consultationId, String doctorId) {
        log.info("Starting WebRTC video call for consultation: {}", consultationId);

        ConsultationEntity consultation = consultationRepository.findById(consultationId)
                .orElseThrow(() -> new RuntimeException("Consultation not found"));

        if (!doctorId.equals(consultation.getDoctorId())) {
            throw new RuntimeException("Unauthorized: consultation not assigned to this doctor");
        }

        if (!"ACCEPTED".equals(consultation.getStatus())) {
            throw new RuntimeException("Consultation must be ACCEPTED before starting call");
        }

        // WebRTC uses peer-to-peer connection via STOMP WebSocket signaling
        // No room URL or tokens needed - signaling happens via /ws/consultation endpoint
        // Room identifier is the consultationId itself
        
        consultation.setRoomUrl("webrtc://" + consultationId);  // Marker for WebRTC mode
        consultation.setDoctorToken(null);  // Not needed for WebRTC
        consultation.setWorkerToken(null);  // Not needed for WebRTC
        consultation.setStatus("IN_PROGRESS");
        consultation.setCallStartedAt(LocalDateTime.now());

        consultation = consultationRepository.save(consultation);
        log.info("WebRTC video call started for consultation: {}", consultationId);

        return toResponseDTO(consultation);
    }

    /**
     * Complete consultation with doctor's notes.
     */
    @Transactional
    public ConsultationResponseDTO complete(String consultationId, String doctorId, ConsultationNotesRequestDTO notes) {
        log.info("Completing consultation: {}", consultationId);

        ConsultationEntity consultation = consultationRepository.findById(consultationId)
                .orElseThrow(() -> new RuntimeException("Consultation not found"));

        if (!doctorId.equals(consultation.getDoctorId())) {
            throw new RuntimeException("Unauthorized: consultation not assigned to this doctor");
        }

        if ("COMPLETED".equals(consultation.getStatus())) {
            throw new RuntimeException("Consultation already completed");
        }

        consultation.setDoctorNotes(notes.getDoctorNotes());
        consultation.setDiagnosis(notes.getDiagnosis());
        consultation.setActionPlan(notes.getActionPlan());
        consultation.setStatus("COMPLETED");
        consultation.setCompletedAt(LocalDateTime.now());

        consultation = consultationRepository.save(consultation);
        log.info("Consultation {} completed", consultationId);

        return toResponseDTO(consultation);
    }

    /**
     * Get doctor's consultation history.
     */
    public List<ConsultationResponseDTO> getDoctorHistory(String doctorId) {
        List<ConsultationEntity> consultations = consultationRepository.findByDoctorIdOrderByCreatedAtDesc(doctorId);
        
        return consultations.stream()
                .map(this::toResponseDTO)
                .collect(Collectors.toList());
    }

    /**
     * Get consultations for a patient (worker view).
     */
    public List<ConsultationResponseDTO> getPatientConsultations(String patientId) {
        List<ConsultationEntity> consultations = consultationRepository.findByPatientIdOrderByCreatedAtDesc(patientId);
        
        return consultations.stream()
                .map(this::toResponseDTO)
                .collect(Collectors.toList());
    }

    // ─── Helper Methods ───────────────────────────────────────────────────────

    private int calculatePriorityScore(String riskLevel) {
        return switch (riskLevel != null ? riskLevel.toUpperCase() : "MEDIUM") {
            case "CRITICAL" -> 100;
            case "HIGH" -> 70;
            case "MEDIUM" -> 40;
            default -> 40;
        };
    }

    /**
     * Build full ConsultationResponseDTO with enriched data.
     */
    private ConsultationResponseDTO toResponseDTO(ConsultationEntity consultation) {
        // Fetch related entities
        PatientEntity patient = patientRepository.findById(UUID.fromString(consultation.getPatientId())).orElse(null);
        AncWorkerEntity worker = workerRepository.findById(UUID.fromString(consultation.getWorkerId())).orElse(null);
        DoctorEntity doctor = consultation.getDoctorId() != null 
                ? doctorRepository.findById(consultation.getDoctorId()).orElse(null) 
                : null;
        AncVisitEntity visit = visitRepository.findById(consultation.getVisitId()).orElse(null);

        // Extract gestational weeks from visit structured data
        Integer gestationalWeeks = null;
        if (visit != null && visit.getStructuredData() != null) {
            Map<String, Object> patientInfo = (Map<String, Object>) visit.getStructuredData().get("patient_info");
            if (patientInfo != null && patientInfo.get("gestationalWeeks") != null) {
                gestationalWeeks = ((Number) patientInfo.get("gestationalWeeks")).intValue();
            }
        }

        return ConsultationResponseDTO.builder()
                .consultationId(consultation.getId())
                .status(consultation.getStatus())
                .riskLevel(consultation.getRiskLevel())
                .isHighRisk(consultation.getIsHighRisk())
                .priorityScore(consultation.getPriorityScore())
                // Patient
                .patientId(consultation.getPatientId())
                .patientName(patient != null ? patient.getFullName() : "Unknown")
                .patientAge(patient != null ? patient.getAge() : null)
                .patientPhone(patient != null ? patient.getPhone() : null)
                .village(patient != null ? patient.getVillage() : null)
                .district(patient != null ? patient.getDistrict() : null)
                .bloodGroup(patient != null ? patient.getBloodGroup() : null)
                // Visit + AI data
                .visitId(consultation.getVisitId())
                .gestationalWeeks(gestationalWeeks)
                .detectedRisks(visit != null ? visit.getDetectedRisks() : null)
                .explanation(visit != null ? visit.getExplanation() : null)
                .confidence(visit != null ? visit.getConfidence() : null)
                .recommendation(visit != null ? visit.getRecommendation() : null)
                // Worker
                .workerId(consultation.getWorkerId())
                .workerName(worker != null ? worker.getFullName() : "Unknown")
                .workerPhone(worker != null ? worker.getPhone() : null)
                .healthCenter(worker != null ? worker.getHealthCenter() : null)
                // Doctor
                .doctorId(consultation.getDoctorId())
                .doctorName(doctor != null ? doctor.getFullName() : null)
                // Video
                .roomUrl(consultation.getRoomUrl())
                .doctorToken(consultation.getDoctorToken())
                .workerToken(consultation.getWorkerToken())
                // Notes
                .doctorNotes(consultation.getDoctorNotes())
                .diagnosis(consultation.getDiagnosis())
                .actionPlan(consultation.getActionPlan())
                // Timestamps
                .acceptedAt(consultation.getAcceptedAt())
                .callStartedAt(consultation.getCallStartedAt())
                .completedAt(consultation.getCompletedAt())
                .createdAt(consultation.getCreatedAt())
                .build();
    }
}
