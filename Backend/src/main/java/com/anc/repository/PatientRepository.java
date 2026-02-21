package com.anc.repository;

import com.anc.entity.PatientEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository interface for PatientEntity.
 * Provides data access methods for patient management with worker-based data isolation.
 * 
 * Requirements: 7.1, 7.2, 8.1
 */
@Repository
public interface PatientRepository extends JpaRepository<PatientEntity, UUID> {

    /**
     * Find all patients registered by a specific worker, ordered by creation date descending.
     * Ensures data isolation - workers can only see their own patients.
     * 
     * @param workerId the UUID of the worker
     * @return List of patients ordered by newest first
     */
    List<PatientEntity> findByWorkerIdOrderByCreatedAtDesc(UUID workerId);

    /**
     * Find a patient by ID and worker ID.
     * Ensures data isolation - verifies the patient belongs to the specified worker.
     * 
     * @param id the patient UUID
     * @param workerId the worker UUID
     * @return Optional containing the patient if found and belongs to worker, empty otherwise
     */
    Optional<PatientEntity> findByIdAndWorkerId(UUID id, UUID workerId);
}
