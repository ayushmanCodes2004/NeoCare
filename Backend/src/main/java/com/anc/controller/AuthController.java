package com.anc.controller;

import com.anc.dto.AuthResponseDTO;
import com.anc.dto.LoginRequestDTO;
import com.anc.dto.SignupRequestDTO;
import com.anc.dto.WorkerProfileResponseDTO;
import com.anc.entity.AncWorkerEntity;
import com.anc.service.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/signup")
    public ResponseEntity<AuthResponseDTO> signup(@Valid @RequestBody SignupRequestDTO request) {
        AuthResponseDTO response = authService.signup(request);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/login")
    public ResponseEntity<AuthResponseDTO> login(@Valid @RequestBody LoginRequestDTO request) {
        AuthResponseDTO response = authService.login(request);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/me")
    public ResponseEntity<WorkerProfileResponseDTO> getProfile(
            @AuthenticationPrincipal AncWorkerEntity worker) {
        WorkerProfileResponseDTO response = authService.getWorkerProfile(worker);
        return ResponseEntity.ok(response);
    }
}
