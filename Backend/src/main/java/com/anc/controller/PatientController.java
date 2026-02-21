package com.anc.controller;

import com.anc.dto.PatientRequestDTO;
import com.anc.dto.PatientResponseDTO;
import com.anc.entity.AncWorkerEntity;
import com.anc.service.PatientService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/patients")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
public class PatientController {

    private final PatientService patientService;

    @PostMapping
    public ResponseEntity<PatientResponseDTO> createPatient(
            @Valid @RequestBody PatientRequestDTO request,
            @AuthenticationPrincipal AncWorkerEntity worker) {
        PatientResponseDTO response = patientService.createPatient(request, worker.getId());
        return ResponseEntity.ok(response);
    }

    @GetMapping
    public ResponseEntity<List<PatientResponseDTO>> getPatients(
            @AuthenticationPrincipal AncWorkerEntity worker) {
        List<PatientResponseDTO> patients = patientService.getPatientsByWorker(worker.getId());
        return ResponseEntity.ok(patients);
    }

    @GetMapping("/{id}")
    public ResponseEntity<PatientResponseDTO> getPatientById(
            @PathVariable UUID id,
            @AuthenticationPrincipal AncWorkerEntity worker) {
        PatientResponseDTO patient = patientService.getPatientById(id, worker.getId());
        return ResponseEntity.ok(patient);
    }
}
