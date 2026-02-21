package com.anc.controller;

import com.anc.dto.AuthResponseDTO;
import com.anc.dto.DoctorProfileResponseDTO;
import com.anc.dto.DoctorSignupRequestDTO;
import com.anc.dto.LoginRequestDTO;
import com.anc.entity.DoctorEntity;
import com.anc.service.DoctorAuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/auth/doctor")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
public class DoctorAuthController {

    private final DoctorAuthService doctorAuthService;

    @PostMapping("/signup")
    public ResponseEntity<AuthResponseDTO> signup(@Valid @RequestBody DoctorSignupRequestDTO request) {
        AuthResponseDTO response = doctorAuthService.signup(request);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/login")
    public ResponseEntity<AuthResponseDTO> login(@Valid @RequestBody LoginRequestDTO request) {
        AuthResponseDTO response = doctorAuthService.login(request);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/me")
    public ResponseEntity<DoctorProfileResponseDTO> getProfile(
            @AuthenticationPrincipal DoctorEntity doctor) {
        DoctorProfileResponseDTO response = doctorAuthService.getDoctorProfile(doctor);
        return ResponseEntity.ok(response);
    }

    @PutMapping("/availability")
    public ResponseEntity<Map<String, String>> updateAvailability(
            @AuthenticationPrincipal DoctorEntity doctor,
            @RequestBody Map<String, Boolean> request) {
        
        doctorAuthService.updateAvailability(doctor.getId(), request.get("isAvailable"));
        
        return ResponseEntity.ok(Map.of(
            "message", "Availability updated successfully",
            "isAvailable", request.get("isAvailable").toString()
        ));
    }
}
