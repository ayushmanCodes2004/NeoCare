package com.anc.repository;

import com.anc.entity.AncWorkerEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

/**
 * Repository interface for AncWorkerEntity.
 * Provides data access methods for ANC worker authentication and management.
 * 
 * Requirements: 1.2, 1.3
 */
@Repository
public interface AncWorkerRepository extends JpaRepository<AncWorkerEntity, UUID> {

    /**
     * Find an ANC worker by phone number.
     * Used for authentication and user lookup.
     * 
     * @param phone the phone number to search for
     * @return Optional containing the worker if found, empty otherwise
     */
    Optional<AncWorkerEntity> findByPhone(String phone);

    /**
     * Check if a phone number is already registered.
     * Used during signup to prevent duplicate phone numbers.
     * 
     * @param phone the phone number to check
     * @return true if phone exists, false otherwise
     */
    boolean existsByPhone(String phone);

    /**
     * Check if an email address is already registered.
     * Used during signup to prevent duplicate email addresses.
     * 
     * @param email the email address to check
     * @return true if email exists, false otherwise
     */
    boolean existsByEmail(String email);
}
