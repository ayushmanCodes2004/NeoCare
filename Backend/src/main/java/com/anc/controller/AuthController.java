package com.anc.controller;

import com.anc.dto.AuthResponseDTO;
import com.anc.dto.LoginRequestDTO;
import com.anc.dto.SignupRequestDTO;
import com.anc.dto.WorkerProfileResponseDTO;
import com.anc.entity.AncWorkerEntity;
import com.anc.service.AuthService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.ExampleObject;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
@Tag(name = "Worker Authentication", description = "Authentication endpoints for ANC Workers")
public class AuthController {

    private final AuthService authService;

    @PostMapping("/signup")
    @Operation(
            summary = "Register new ANC worker",
            description = "Creates a new ANC worker account with the provided details. Password is hashed before storage."
    )
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "200",
                    description = "Worker registered successfully",
                    content = @Content(
                            mediaType = "application/json",
                            schema = @Schema(implementation = AuthResponseDTO.class),
                            examples = @ExampleObject(value = """
                                    {
                                      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                                      "workerId": "550e8400-e29b-41d4-a716-446655440000",
                                      "fullName": "Priya Sharma",
                                      "phone": "9876543210",
                                      "email": "priya@health.gov.in",
                                      "healthCenter": "Primary Health Center Bangalore",
                                      "district": "Bangalore Urban",
                                      "message": "Signup successful"
                                    }
                                    """)
                    )
            ),
            @ApiResponse(responseCode = "400", description = "Invalid input data"),
            @ApiResponse(responseCode = "409", description = "Phone number already registered")
    })
    public ResponseEntity<AuthResponseDTO> signup(
            @io.swagger.v3.oas.annotations.parameters.RequestBody(
                    description = "Worker signup details",
                    required = true,
                    content = @Content(
                            schema = @Schema(implementation = SignupRequestDTO.class),
                            examples = @ExampleObject(value = """
                                    {
                                      "fullName": "Priya Sharma",
                                      "phone": "9876543210",
                                      "email": "priya@health.gov.in",
                                      "password": "SecurePass123",
                                      "healthCenter": "Primary Health Center Bangalore",
                                      "district": "Bangalore Urban"
                                    }
                                    """)
                    )
            )
            @Valid @RequestBody SignupRequestDTO request) {
        AuthResponseDTO response = authService.signup(request);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/login")
    @Operation(
            summary = "Worker login",
            description = "Authenticates an ANC worker and returns a JWT token for subsequent API calls"
    )
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "200",
                    description = "Login successful",
                    content = @Content(
                            mediaType = "application/json",
                            schema = @Schema(implementation = AuthResponseDTO.class),
                            examples = @ExampleObject(value = """
                                    {
                                      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                                      "workerId": "550e8400-e29b-41d4-a716-446655440000",
                                      "fullName": "Priya Sharma",
                                      "phone": "9876543210",
                                      "email": "priya@health.gov.in",
                                      "healthCenter": "Primary Health Center Bangalore",
                                      "district": "Bangalore Urban",
                                      "message": "Login successful"
                                    }
                                    """)
                    )
            ),
            @ApiResponse(responseCode = "401", description = "Invalid credentials")
    })
    public ResponseEntity<AuthResponseDTO> login(
            @io.swagger.v3.oas.annotations.parameters.RequestBody(
                    description = "Worker login credentials",
                    required = true,
                    content = @Content(
                            schema = @Schema(implementation = LoginRequestDTO.class),
                            examples = @ExampleObject(value = """
                                    {
                                      "phone": "9876543210",
                                      "password": "SecurePass123"
                                    }
                                    """)
                    )
            )
            @Valid @RequestBody LoginRequestDTO request) {
        AuthResponseDTO response = authService.login(request);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/me")
    @Operation(
            summary = "Get worker profile",
            description = "Returns the profile information of the authenticated worker",
            security = @SecurityRequirement(name = "Bearer Authentication")
    )
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "200",
                    description = "Profile retrieved successfully",
                    content = @Content(
                            mediaType = "application/json",
                            schema = @Schema(implementation = WorkerProfileResponseDTO.class)
                    )
            ),
            @ApiResponse(responseCode = "401", description = "Unauthorized - Invalid or missing token")
    })
    public ResponseEntity<WorkerProfileResponseDTO> getProfile(
            @AuthenticationPrincipal AncWorkerEntity worker) {
        WorkerProfileResponseDTO response = authService.getWorkerProfile(worker);
        return ResponseEntity.ok(response);
    }
}
