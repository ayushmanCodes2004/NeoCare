package com.anc.service;

import com.anc.dto.AuthResponseDTO;
import com.anc.dto.DoctorProfileResponseDTO;
import com.anc.dto.DoctorSignupRequestDTO;
import com.anc.dto.LoginRequestDTO;
import com.anc.entity.DoctorEntity;
import com.anc.repository.DoctorRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
@RequiredArgsConstructor
public class DoctorAuthService {

    private final DoctorRepository doctorRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final AuthenticationManager authenticationManager;

    public AuthResponseDTO signup(DoctorSignupRequestDTO request) {
        // Check if email already exists
        if (doctorRepository.existsByEmail(request.getEmail())) {
            throw new RuntimeException("Email already registered");
        }

        // Check if phone already exists
        if (doctorRepository.existsByPhone(request.getPhone())) {
            throw new RuntimeException("Phone number already registered");
        }

        // Create doctor entity
        DoctorEntity doctor = DoctorEntity.builder()
                .fullName(request.getFullName())
                .email(request.getEmail())
                .phone(request.getPhone())
                .password(passwordEncoder.encode(request.getPassword()))
                .specialization(request.getSpecialization())
                .licenseNumber(request.getLicenseNumber())
                .hospital(request.getHospital())
                .district(request.getDistrict())
                .yearsOfExperience(request.getYearsOfExperience())
                .role("DOCTOR")
                .isAvailable(true)
                .build();

        doctorRepository.save(doctor);

        // Generate JWT token with doctor ID
        String token = jwtService.generateToken(doctor, doctor.getId());

        return AuthResponseDTO.builder()
                .token(token)
                .workerId(doctor.getId())
                .fullName(doctor.getFullName())
                .email(doctor.getEmail())
                .phone(doctor.getPhone())
                .healthCenter(doctor.getHospital())
                .district(doctor.getDistrict())
                .message("Doctor registered successfully")
                .build();
    }

    public AuthResponseDTO login(LoginRequestDTO request) {
        // Authenticate using email (stored in phone field for doctors)
        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        request.getPhone(),
                        request.getPassword()
                )
        );

        // Find doctor by email
        DoctorEntity doctor = doctorRepository.findByEmail(request.getPhone())
                .orElseThrow(() -> new RuntimeException("Doctor not found"));

        // Generate token
        String token = jwtService.generateToken(doctor, doctor.getId());

        return AuthResponseDTO.builder()
                .token(token)
                .workerId(doctor.getId())
                .fullName(doctor.getFullName())
                .email(doctor.getEmail())
                .phone(doctor.getPhone())
                .healthCenter(doctor.getHospital())
                .district(doctor.getDistrict())
                .message("Login successful")
                .build();
    }

    public DoctorProfileResponseDTO getDoctorProfile(DoctorEntity doctor) {
        return DoctorProfileResponseDTO.builder()
                .doctorId(doctor.getId())
                .fullName(doctor.getFullName())
                .email(doctor.getEmail())
                .phone(doctor.getPhone())
                .specialization(doctor.getSpecialization())
                .licenseNumber(doctor.getLicenseNumber())
                .hospital(doctor.getHospital())
                .district(doctor.getDistrict())
                .yearsOfExperience(doctor.getYearsOfExperience())
                .isAvailable(doctor.getIsAvailable())
                .role(doctor.getRole())
                .build();
    }

    public void updateAvailability(UUID doctorId, Boolean isAvailable) {
        DoctorEntity doctor = doctorRepository.findById(doctorId)
                .orElseThrow(() -> new RuntimeException("Doctor not found"));
        
        doctor.setIsAvailable(isAvailable);
        doctorRepository.save(doctor);
    }
}
