package com.anc.service;

import com.anc.dto.AuthResponseDTO;
import com.anc.dto.LoginRequestDTO;
import com.anc.dto.SignupRequestDTO;
import com.anc.dto.WorkerProfileResponseDTO;
import com.anc.entity.AncWorkerEntity;
import com.anc.repository.AncWorkerRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Service for handling worker authentication operations including signup and login.
 * Implements BCrypt password hashing, duplicate checking, and JWT token generation.
 * 
 * Requirements: 1.1-1.8, 2.1-2.5, 10.1-10.4, 19.1, 19.2
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class AuthService {

    private final AncWorkerRepository ancWorkerRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final AuthenticationManager authenticationManager;

    /**
     * Register a new ANC worker account.
     * Validates uniqueness of phone and email, hashes password with BCrypt strength 12,
     * and generates JWT token.
     * 
     * @param request signup request containing worker details
     * @return authentication response with token and worker profile
     * @throws IllegalArgumentException if phone or email already exists
     * 
     * Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 10.1, 10.2, 19.1
     */
    @Transactional
    public AuthResponseDTO signup(SignupRequestDTO request) {
        log.debug("Processing signup request for phone: {}", request.getPhone());

        // Check for duplicate phone number (Requirement 1.2)
        if (ancWorkerRepository.existsByPhone(request.getPhone())) {
            log.warn("Signup failed: Phone number already registered - {}", request.getPhone());
            throw new IllegalArgumentException("Phone number already registered");
        }

        // Check for duplicate email (Requirement 1.3)
        if (ancWorkerRepository.existsByEmail(request.getEmail())) {
            log.warn("Signup failed: Email address already registered - {}", request.getEmail());
            throw new IllegalArgumentException("Email address already registered");
        }

        // Hash password with BCrypt strength 12 (Requirement 1.1, 10.1)
        String hashedPassword = passwordEncoder.encode(request.getPassword());

        // Create worker account with is_active = true by default (Requirement 1.8)
        AncWorkerEntity worker = AncWorkerEntity.builder()
                .fullName(request.getFullName())
                .phone(request.getPhone())
                .email(request.getEmail())
                .passwordHash(hashedPassword)
                .healthCenter(request.getHealthCenter())
                .district(request.getDistrict())
                .isActive(true)
                .build();

        worker = ancWorkerRepository.save(worker);

        // Generate JWT token with 24-hour expiration (Requirement 1.4)
        String token = jwtService.generateToken(worker, worker.getId());

        // Log successful signup (Requirement 19.1)
        log.info("Worker signed up successfully - ID: {}, Phone: {}", worker.getId(), worker.getPhone());

        // Return token and worker profile (Requirement 1.5)
        return AuthResponseDTO.builder()
                .token(token)
                .workerId(worker.getId())
                .fullName(worker.getFullName())
                .phone(worker.getPhone())
                .email(worker.getEmail())
                .healthCenter(worker.getHealthCenter())
                .district(worker.getDistrict())
                .message("Worker registered successfully")
                .build();
    }

    /**
     * Authenticate worker and generate JWT token.
     * Validates credentials and generates token with phone as subject and workerId as claim.
     * 
     * @param request login request containing phone and password
     * @return authentication response with token and worker profile
     * @throws org.springframework.security.core.AuthenticationException if credentials are invalid
     * 
     * Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 10.3, 19.2
     */
    @Transactional(readOnly = true)
    public AuthResponseDTO login(LoginRequestDTO request) {
        log.debug("Processing login request for phone: {}", request.getPhone());

        // Authenticate credentials using AuthenticationManager (Requirement 2.1, 10.3)
        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        request.getPhone(),
                        request.getPassword()
                )
        );

        // Get authenticated worker
        AncWorkerEntity worker = (AncWorkerEntity) authentication.getPrincipal();

        // Generate JWT token with phone as subject and workerId as custom claim (Requirement 2.2)
        String token = jwtService.generateToken(worker, worker.getId());

        // Log successful login (Requirement 19.2)
        log.info("Worker logged in successfully - ID: {}, Phone: {}", worker.getId(), worker.getPhone());

        // Return token with worker profile information (Requirement 2.3)
        return AuthResponseDTO.builder()
                .token(token)
                .workerId(worker.getId())
                .fullName(worker.getFullName())
                .phone(worker.getPhone())
                .email(worker.getEmail())
                .healthCenter(worker.getHealthCenter())
                .district(worker.getDistrict())
                .message("Login successful")
                .build();
    }

    /**
     * Get worker profile information from authenticated worker entity.
     * 
     * @param worker the authenticated worker entity
     * @return worker profile response
     * 
     * Requirements: 5.1, 5.4
     */
    public WorkerProfileResponseDTO getWorkerProfile(AncWorkerEntity worker) {
        log.debug("Retrieving profile for worker ID: {}", worker.getId());

        return WorkerProfileResponseDTO.builder()
                .workerId(worker.getId())
                .fullName(worker.getFullName())
                .phone(worker.getPhone())
                .email(worker.getEmail())
                .healthCenter(worker.getHealthCenter())
                .district(worker.getDistrict())
                .message("Profile retrieved successfully")
                .build();
    }
}
