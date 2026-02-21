package com.anc.repository;

import com.anc.entity.ConsultationEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Repository
public interface ConsultationRepository extends JpaRepository<ConsultationEntity, UUID> {
    
    List<ConsultationEntity> findByDoctorId(UUID doctorId);
    
    List<ConsultationEntity> findByWorkerId(UUID workerId);
    
    List<ConsultationEntity> findByPatientId(UUID patientId);
    
    List<ConsultationEntity> findByStatus(String status);
    
    List<ConsultationEntity> findByRiskLevel(String riskLevel);
    
    List<ConsultationEntity> findByDoctorIdAndStatus(UUID doctorId, String status);
    
    @Query("SELECT c FROM ConsultationEntity c WHERE c.doctorId = :doctorId AND c.status = 'REQUESTED' ORDER BY c.createdAt DESC")
    List<ConsultationEntity> findPendingRequestsByDoctor(UUID doctorId);
    
    @Query("SELECT c FROM ConsultationEntity c WHERE c.doctorId = :doctorId AND c.scheduledAt BETWEEN :start AND :end ORDER BY c.scheduledAt ASC")
    List<ConsultationEntity> findScheduledConsultations(UUID doctorId, LocalDateTime start, LocalDateTime end);
    
    @Query("SELECT c FROM ConsultationEntity c WHERE c.riskLevel IN ('HIGH', 'CRITICAL') AND c.status = 'REQUESTED' ORDER BY c.riskLevel DESC, c.createdAt DESC")
    List<ConsultationEntity> findHighRiskPendingConsultations();
    
    @Query("SELECT c FROM ConsultationEntity c WHERE c.doctorId = :doctorId ORDER BY c.createdAt DESC")
    List<ConsultationEntity> findRecentConsultationsByDoctor(UUID doctorId);
}
