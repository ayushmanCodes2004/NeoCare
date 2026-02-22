package com.anc.controller;

import com.anc.dto.DoctorAuthResponseDTO;
import com.anc.dto.DoctorLoginRequestDTO;
import com.anc.dto.DoctorSignupRequestDTO;
import com.anc.entity.DoctorEntity;
import com.anc.service.DoctorAuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/api/doctor/auth")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class DoctorAuthController {

    private final DoctorAuthService doctorAuthService;

    /**
     * POST /api/doctor/auth/signup
     *
     * Body: { fullName, phone, email, password, specialization, hospital, district, registrationNo }
     * Response: { token, role="DOCTOR", doctorId, fullName, specialization, hospital, ... }
     */
    @PostMapping("/signup")
    public ResponseEntity<DoctorAuthResponseDTO> signup(
            @Valid @RequestBody DoctorSignupRequestDTO request) {

        log.info("Doctor signup for phone: {}", request.getPhone());
        return ResponseEntity.status(HttpStatus.CREATED).body(doctorAuthService.signup(request));
    }

    /**
     * POST /api/doctor/auth/login
     *
     * Body: { phone, password }
     * Response: { token, role="DOCTOR", doctorId, fullName, ... }
     */
    @PostMapping("/login")
    public ResponseEntity<DoctorAuthResponseDTO> login(
            @Valid @RequestBody DoctorLoginRequestDTO request) {

        log.info("Doctor login for phone: {}", request.getPhone());
        return ResponseEntity.ok(doctorAuthService.login(request));
    }

    /**
     * GET /api/doctor/auth/me
     * Header: Authorization: Bearer <token>
     */
    @GetMapping("/me")
    public ResponseEntity<DoctorAuthResponseDTO> getMe(
            @AuthenticationPrincipal DoctorEntity doctor) {

        DoctorAuthResponseDTO response = DoctorAuthResponseDTO.builder()
                .doctorId(doctor.getId())
                .role("DOCTOR")
                .fullName(doctor.getFullName())
                .phone(doctor.getPhone())
                .email(doctor.getEmail())
                .specialization(doctor.getSpecialization())
                .hospital(doctor.getHospital())
                .district(doctor.getDistrict())
                .registrationNo(doctor.getRegistrationNo())
                .isAvailable(doctor.getIsAvailable())
                .message("Profile fetched")
                .build();

        return ResponseEntity.ok(response);
    }
}
