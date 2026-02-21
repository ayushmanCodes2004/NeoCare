package com.anc.controller;

import com.anc.dto.ConsultationRequestDTO;
import com.anc.dto.ConsultationResponseDTO;
import com.anc.entity.AncWorkerEntity;
import com.anc.entity.DoctorEntity;
import com.anc.service.ConsultationService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/consultations")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
public class ConsultationController {

    private final ConsultationService consultationService;

    @PostMapping("/request")
    public ResponseEntity<ConsultationResponseDTO> requestConsultation(
            @Valid @RequestBody ConsultationRequestDTO request,
            @AuthenticationPrincipal AncWorkerEntity worker) {
        
        ConsultationResponseDTO response = consultationService.requestConsultation(request, worker.getId());
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/pending")
    public ResponseEntity<List<ConsultationResponseDTO>> getPendingRequests(
            @AuthenticationPrincipal DoctorEntity doctor) {
        
        List<ConsultationResponseDTO> consultations = consultationService.getPendingRequests(doctor.getId());
        return ResponseEntity.ok(consultations);
    }

    @GetMapping("/my-consultations")
    public ResponseEntity<List<ConsultationResponseDTO>> getMyConsultations(
            @AuthenticationPrincipal DoctorEntity doctor) {
        
        List<ConsultationResponseDTO> consultations = consultationService.getDoctorConsultations(doctor.getId());
        return ResponseEntity.ok(consultations);
    }

    @GetMapping("/{id}")
    public ResponseEntity<ConsultationResponseDTO> getConsultationById(@PathVariable UUID id) {
        ConsultationResponseDTO consultation = consultationService.getConsultationById(id);
        return ResponseEntity.ok(consultation);
    }

    @PutMapping("/{id}/accept")
    public ResponseEntity<ConsultationResponseDTO> acceptConsultation(
            @PathVariable UUID id,
            @AuthenticationPrincipal DoctorEntity doctor) {
        
        ConsultationResponseDTO response = consultationService.acceptConsultation(id, doctor.getId());
        return ResponseEntity.ok(response);
    }

    @PutMapping("/{id}/start")
    public ResponseEntity<ConsultationResponseDTO> startConsultation(
            @PathVariable UUID id,
            @AuthenticationPrincipal DoctorEntity doctor,
            @RequestBody Map<String, String> request) {
        
        String roomId = request.get("roomId");
        ConsultationResponseDTO response = consultationService.startConsultation(id, doctor.getId(), roomId);
        return ResponseEntity.ok(response);
    }

    @PutMapping("/{id}/complete")
    public ResponseEntity<ConsultationResponseDTO> completeConsultation(
            @PathVariable UUID id,
            @AuthenticationPrincipal DoctorEntity doctor,
            @RequestBody Map<String, String> request) {
        
        ConsultationResponseDTO response = consultationService.completeConsultation(
            id,
            doctor.getId(),
            request.get("doctorNotes"),
            request.get("prescription"),
            request.get("recommendations")
        );
        return ResponseEntity.ok(response);
    }

    @PutMapping("/{id}/cancel")
    public ResponseEntity<Map<String, String>> cancelConsultation(
            @PathVariable UUID id,
            @AuthenticationPrincipal DoctorEntity doctor) {
        
        consultationService.cancelConsultation(id, doctor.getId());
        return ResponseEntity.ok(Map.of("message", "Consultation cancelled successfully"));
    }

    @GetMapping("/high-risk")
    public ResponseEntity<List<ConsultationResponseDTO>> getHighRiskConsultations() {
        List<ConsultationResponseDTO> consultations = consultationService.getHighRiskConsultations();
        return ResponseEntity.ok(consultations);
    }
}
