package com.anc.service;

import com.anc.dto.PatientRequestDTO;
import com.anc.dto.PatientResponseDTO;
import com.anc.entity.AncWorkerEntity;
import com.anc.entity.PatientEntity;
import com.anc.repository.AncWorkerRepository;
import com.anc.repository.PatientRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * Service for managing patient records with worker-based data isolation.
 * Ensures workers can only access their own patients.
 * 
 * Requirements: 6.1-6.6, 7.1-7.3, 8.1-8.4, 18.1-18.6, 19.4
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class PatientService {

    private final PatientRepository patientRepository;
    private final AncWorkerRepository ancWorkerRepository;

    /**
     * Create a new patient record for the authenticated worker.
     * Worker ID is taken from the authenticated context, not from request body.
     * 
     * @param request patient details
     * @param workerId authenticated worker's UUID from security context
     * @return patient response with created patient details
     * @throws IllegalArgumentException if worker not found
     * 
     * Requirements: 6.1, 6.2, 6.3, 6.5, 6.6, 18.2, 18.3
     */
    @Transactional
    public PatientResponseDTO createPatient(PatientRequestDTO request, UUID workerId) {
        log.debug("Creating patient for worker ID: {}", workerId);

        // Load worker entity (Requirement 18.3)
        AncWorkerEntity worker = ancWorkerRepository.findById(workerId)
                .orElseThrow(() -> new IllegalArgumentException("Worker not found"));

        // Create patient entity with worker ID from authenticated context (Requirement 6.1, 18.2)
        PatientEntity patient = PatientEntity.builder()
                .worker(worker)
                .fullName(request.getFullName())
                .phone(request.getPhone())
                .age(request.getAge())
                .address(request.getAddress())
                .village(request.getVillage())
                .district(request.getDistrict())
                .lmpDate(request.getLmpDate())
                .eddDate(request.getEddDate())
                .bloodGroup(request.getBloodGroup())
                .build();

        patient = patientRepository.save(patient);

        log.info("Patient created successfully - ID: {}, Worker ID: {}", patient.getId(), workerId);

        // Return patient details (Requirement 6.3)
        return mapToResponseDTO(patient);
    }

    /**
     * Get all patients registered by the authenticated worker.
     * Returns patients ordered by creation date descending (newest first).
     * 
     * @param workerId authenticated worker's UUID from security context
     * @return list of patient responses
     * 
     * Requirements: 7.1, 7.2, 7.3, 18.1, 18.5
     */
    @Transactional(readOnly = true)
    public List<PatientResponseDTO> getPatientsByWorker(UUID workerId) {
        log.debug("Retrieving patients for worker ID: {}", workerId);

        // Query patients filtered by worker ID, ordered by creation date desc (Requirement 7.1, 7.2, 18.1)
        List<PatientEntity> patients = patientRepository.findByWorkerIdOrderByCreatedAtDesc(workerId);

        log.debug("Found {} patients for worker ID: {}", patients.size(), workerId);

        return patients.stream()
                .map(this::mapToResponseDTO)
                .collect(Collectors.toList());
    }

    /**
     * Get a specific patient by ID with worker ownership validation.
     * Ensures the patient belongs to the authenticated worker.
     * 
     * @param patientId patient UUID
     * @param workerId authenticated worker's UUID from security context
     * @return patient response
     * @throws IllegalArgumentException if patient not found or access denied
     * 
     * Requirements: 8.1, 8.2, 8.3, 8.4, 18.1, 18.4, 18.6, 19.4
     */
    @Transactional(readOnly = true)
    public PatientResponseDTO getPatientById(UUID patientId, UUID workerId) {
        log.debug("Retrieving patient ID: {} for worker ID: {}", patientId, workerId);

        // Verify patient exists and belongs to the authenticated worker (Requirement 8.1, 18.4)
        PatientEntity patient = patientRepository.findByIdAndWorkerId(patientId, workerId)
                .orElseGet(() -> {
                    // Check if patient exists but belongs to another worker
                    if (patientRepository.existsById(patientId)) {
                        // Log unauthorized access attempt (Requirement 19.4)
                        log.warn("Access denied: Worker ID {} attempted to access patient ID {} belonging to another worker",
                                workerId, patientId);
                        throw new IllegalArgumentException("Access denied: this patient is not registered under your account");
                    } else {
                        // Patient doesn't exist at all (Requirement 8.4)
                        log.debug("Patient not found with ID: {}", patientId);
                        throw new IllegalArgumentException("Patient not found");
                    }
                });

        log.debug("Patient retrieved successfully - ID: {}", patientId);

        // Return complete patient details (Requirement 8.2)
        return mapToResponseDTO(patient);
    }

    /**
     * Map PatientEntity to PatientResponseDTO.
     * 
     * @param patient patient entity
     * @return patient response DTO
     */
    private PatientResponseDTO mapToResponseDTO(PatientEntity patient) {
        return PatientResponseDTO.builder()
                .patientId(patient.getId())
                .workerId(patient.getWorker().getId())
                .fullName(patient.getFullName())
                .phone(patient.getPhone())
                .age(patient.getAge())
                .address(patient.getAddress())
                .village(patient.getVillage())
                .district(patient.getDistrict())
                .lmpDate(patient.getLmpDate())
                .eddDate(patient.getEddDate())
                .bloodGroup(patient.getBloodGroup())
                .createdAt(patient.getCreatedAt())
                .build();
    }
}
