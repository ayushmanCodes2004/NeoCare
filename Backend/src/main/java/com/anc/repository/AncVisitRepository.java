package com.anc.repository;

import com.anc.entity.AncVisitEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AncVisitRepository extends JpaRepository<AncVisitEntity, String> {

    List<AncVisitEntity> findByPatientIdOrderByCreatedAtDesc(String patientId);

    List<AncVisitEntity> findByWorkerIdOrderByCreatedAtDesc(String workerId);

    /** All visits where isHighRisk = true (covers CRITICAL + HIGH) */
    List<AncVisitEntity> findByIsHighRiskTrueOrderByCreatedAtDesc();

    /** Filter by specific riskLevel: CRITICAL / HIGH / MEDIUM / LOW */
    List<AncVisitEntity> findByRiskLevelOrderByCreatedAtDesc(String riskLevel);

    /** CRITICAL only — for urgent supervisor alert panel */
    @Query("SELECT v FROM AncVisitEntity v WHERE v.riskLevel = 'CRITICAL' ORDER BY v.createdAt DESC")
    List<AncVisitEntity> findAllCriticalVisits();

    /** Most recent visit for a patient */
    @Query("SELECT v FROM AncVisitEntity v WHERE v.patientId = :patientId ORDER BY v.createdAt DESC LIMIT 1")
    AncVisitEntity findLatestByPatientId(@Param("patientId") String patientId);

    /** Dashboard stat: total high risk count */
    @Query("SELECT COUNT(v) FROM AncVisitEntity v WHERE v.isHighRisk = true")
    long countHighRiskVisits();

    /** Dashboard stat: total critical count */
    @Query("SELECT COUNT(v) FROM AncVisitEntity v WHERE v.riskLevel = 'CRITICAL'")
    long countCriticalVisits();
}
