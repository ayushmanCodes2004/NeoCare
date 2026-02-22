package com.anc.service;

import com.anc.dto.DoctorAuthResponseDTO;
import com.anc.dto.DoctorLoginRequestDTO;
import com.anc.dto.DoctorSignupRequestDTO;
import com.anc.entity.DoctorEntity;
import com.anc.repository.DoctorRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class DoctorAuthService {

    private final DoctorRepository doctorRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final AuthenticationManager authenticationManager;

    public DoctorAuthResponseDTO signup(DoctorSignupRequestDTO request) {
        log.info("Doctor signup for phone: {}", request.getPhone());

        if (doctorRepository.existsByPhone(request.getPhone())) {
            throw new RuntimeException("Phone number already registered");
        }
        if (request.getEmail() != null && doctorRepository.existsByEmail(request.getEmail())) {
            throw new RuntimeException("Email already registered");
        }

        DoctorEntity doctor = DoctorEntity.builder()
                .fullName(request.getFullName())
                .phone(request.getPhone())
                .email(request.getEmail())
                .passwordHash(passwordEncoder.encode(request.getPassword()))
                .specialization(
                    request.getSpecialization() != null
                        ? request.getSpecialization()
                        : "Obstetrics & Gynaecology"
                )
                .hospital(request.getHospital())
                .district(request.getDistrict())
                .registrationNo(request.getRegistrationNo())
                .isActive(true)
                .isAvailable(true)
                .build();

        doctor = doctorRepository.save(doctor);
        log.info("Doctor created — ID: {}", doctor.getId());

        // Pass role="DOCTOR" so JwtService embeds it in the token
        String token = jwtService.generateToken(doctor.getPhone(), doctor.getId(), "DOCTOR");
        return buildResponse(doctor, token, "Account created successfully");
    }

    public DoctorAuthResponseDTO login(DoctorLoginRequestDTO request) {
        log.info("Doctor login for phone: {}", request.getPhone());

        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.getPhone(), request.getPassword())
        );

        DoctorEntity doctor = doctorRepository.findByPhone(request.getPhone())
                .orElseThrow(() -> new RuntimeException("Doctor not found"));

        String token = jwtService.generateToken(doctor.getPhone(), doctor.getId(), "DOCTOR");
        return buildResponse(doctor, token, "Login successful");
    }

    private DoctorAuthResponseDTO buildResponse(DoctorEntity doctor, String token, String message) {
        return DoctorAuthResponseDTO.builder()
                .token(token)
                .role("DOCTOR")
                .doctorId(doctor.getId())
                .fullName(doctor.getFullName())
                .phone(doctor.getPhone())
                .email(doctor.getEmail())
                .specialization(doctor.getSpecialization())
                .hospital(doctor.getHospital())
                .district(doctor.getDistrict())
                .registrationNo(doctor.getRegistrationNo())
                .isAvailable(doctor.getIsAvailable())
                .message(message)
                .build();
    }
}
