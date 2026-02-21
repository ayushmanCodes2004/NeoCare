package com.anc.repository;

import com.anc.entity.DoctorEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface DoctorRepository extends JpaRepository<DoctorEntity, UUID> {
    
    Optional<DoctorEntity> findByEmail(String email);
    
    Optional<DoctorEntity> findByPhone(String phone);
    
    boolean existsByEmail(String email);
    
    boolean existsByPhone(String phone);
    
    List<DoctorEntity> findByIsAvailable(Boolean isAvailable);
    
    List<DoctorEntity> findByDistrict(String district);
    
    List<DoctorEntity> findBySpecialization(String specialization);
}
