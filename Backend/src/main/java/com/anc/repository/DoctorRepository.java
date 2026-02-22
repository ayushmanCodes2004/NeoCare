package com.anc.repository;

import com.anc.entity.DoctorEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface DoctorRepository extends JpaRepository<DoctorEntity, String> {

    Optional<DoctorEntity> findByPhone(String phone);

    boolean existsByPhone(String phone);

    boolean existsByEmail(String email);

    /** Find available doctors in the same district for auto-assignment */
    List<DoctorEntity> findByDistrictAndIsAvailableTrueAndIsActiveTrue(String district);

    /** All available doctors (fallback if no district match) */
    List<DoctorEntity> findByIsAvailableTrueAndIsActiveTrue();
}
