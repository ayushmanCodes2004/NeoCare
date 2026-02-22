package com.anc.repository;

import com.anc.entity.ConsultationEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ConsultationRepository extends JpaRepository<ConsultationEntity, String> {

    /**
     * Doctor's priority queue:
     * PENDING + ACCEPTED cases, CRITICAL first, oldest first within same priority.
     * Doctor sees this on their dashboard.
     */
    @Query("""
        SELECT c FROM ConsultationEntity c
        WHERE c.status IN ('PENDING', 'ACCEPTED')
        ORDER BY c.priorityScore DESC, c.createdAt ASC
        """)
    List<ConsultationEntity> findPriorityQueue();

    /**
     * Queue filtered by doctor's district (preferred).
     * Used when auto-assign-district = true.
     */
    @Query("""
        SELECT c FROM ConsultationEntity c
        JOIN PatientEntity p ON CAST(c.patientId AS string) = CAST(p.id AS string)
        WHERE c.status IN ('PENDING', 'ACCEPTED')
          AND p.district = :district
        ORDER BY c.priorityScore DESC, c.createdAt ASC
        """)
    List<ConsultationEntity> findPriorityQueueByDistrict(@Param("district") String district);

    /** All consultations assigned to a specific doctor */
    List<ConsultationEntity> findByDoctorIdOrderByCreatedAtDesc(String doctorId);

    /** Active consultation (IN_PROGRESS) for a doctor — at most one at a time */
    Optional<ConsultationEntity> findByDoctorIdAndStatus(String doctorId, String status);

    /** All consultations for a patient — worker uses this to see history */
    List<ConsultationEntity> findByPatientIdOrderByCreatedAtDesc(String patientId);

    /** Check if a pending consultation already exists for this visit */
    boolean existsByVisitIdAndStatusIn(String visitId, List<String> statuses);

    /** CRITICAL count for dashboard */
    @Query("SELECT COUNT(c) FROM ConsultationEntity c WHERE c.riskLevel = 'CRITICAL' AND c.status = 'PENDING'")
    long countPendingCritical();
}
