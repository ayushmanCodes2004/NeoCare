package com.anc.controller;

import com.anc.dto.ConsultationNotesRequestDTO;
import com.anc.dto.ConsultationResponseDTO;
import com.anc.entity.DoctorEntity;
import com.anc.service.ConsultationService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * Consultation Controller — Doctor Module
 * 
 * Endpoints:
 * - GET  /api/consultations/queue              → Priority queue (DOCTOR)
 * - GET  /api/consultations/{id}               → Full consultation details (DOCTOR)
 * - POST /api/consultations/{id}/accept        → Accept consultation (DOCTOR)
 * - POST /api/consultations/{id}/start-call    → Start video call (DOCTOR)
 * - POST /api/consultations/{id}/complete      → Submit notes (DOCTOR)
 * - GET  /api/consultations/my-history         → Doctor's history (DOCTOR)
 * - GET  /api/consultations/patient/{patientId}→ Patient consultations (WORKER)
 */
@Slf4j
@RestController
@RequestMapping("/api/consultations")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
public class ConsultationController {

    private final ConsultationService consultationService;

    /**
     * GET /api/consultations/queue
     * 
     * Doctor's priority queue: CRITICAL → HIGH → MEDIUM, oldest first.
     * Shows PENDING and ACCEPTED consultations.
     */
    @GetMapping("/queue")
    public ResponseEntity<List<ConsultationResponseDTO>> getPriorityQueue(
            @AuthenticationPrincipal DoctorEntity doctor) {
        
        log.info("Doctor {} fetching priority queue", doctor.getId());
        List<ConsultationResponseDTO> queue = consultationService.getPriorityQueue(doctor.getId());
        
        return ResponseEntity.ok(queue);
    }

    /**
     * GET /api/consultations/{id}
     * 
     * Get full consultation details including patient, visit, AI analysis.
     */
    @GetMapping("/{id}")
    public ResponseEntity<ConsultationResponseDTO> getConsultationById(@PathVariable String id) {
        log.info("Fetching consultation: {}", id);
        ConsultationResponseDTO consultation = consultationService.getById(id);
        
        return ResponseEntity.ok(consultation);
    }

    /**
     * POST /api/consultations/{id}/accept
     * 
     * Doctor accepts a consultation.
     * Status: PENDING → ACCEPTED
     */
    @PostMapping("/{id}/accept")
    public ResponseEntity<ConsultationResponseDTO> acceptConsultation(
            @PathVariable String id,
            @AuthenticationPrincipal DoctorEntity doctor) {
        
        log.info("Doctor {} accepting consultation {}", doctor.getId(), id);
        ConsultationResponseDTO response = consultationService.accept(id, doctor.getId());
        
        return ResponseEntity.ok(response);
    }

    /**
     * POST /api/consultations/{id}/start-call
     * 
     * Start video call — generates Daily.co room and tokens.
     * Status: ACCEPTED → IN_PROGRESS
     */
    @PostMapping("/{id}/start-call")
    public ResponseEntity<ConsultationResponseDTO> startCall(
            @PathVariable String id,
            @AuthenticationPrincipal DoctorEntity doctor) {
        
        log.info("Doctor {} starting call for consultation {}", doctor.getId(), id);
        ConsultationResponseDTO response = consultationService.startCall(id, doctor.getId());
        
        return ResponseEntity.ok(response);
    }

    /**
     * POST /api/consultations/{id}/complete
     * 
     * Complete consultation with doctor's notes.
     * Status: IN_PROGRESS → COMPLETED
     * 
     * Body: { "doctorNotes": "...", "diagnosis": "...", "actionPlan": "..." }
     */
    @PostMapping("/{id}/complete")
    public ResponseEntity<ConsultationResponseDTO> completeConsultation(
            @PathVariable String id,
            @AuthenticationPrincipal DoctorEntity doctor,
            @Valid @RequestBody ConsultationNotesRequestDTO notes) {
        
        log.info("Doctor {} completing consultation {}", doctor.getId(), id);
        ConsultationResponseDTO response = consultationService.complete(id, doctor.getId(), notes);
        
        return ResponseEntity.ok(response);
    }

    /**
     * GET /api/consultations/my-history
     * 
     * Doctor's consultation history (all statuses).
     */
    @GetMapping("/my-history")
    public ResponseEntity<List<ConsultationResponseDTO>> getDoctorHistory(
            @AuthenticationPrincipal DoctorEntity doctor) {
        
        log.info("Doctor {} fetching consultation history", doctor.getId());
        List<ConsultationResponseDTO> history = consultationService.getDoctorHistory(doctor.getId());
        
        return ResponseEntity.ok(history);
    }

    /**
     * GET /api/consultations/patient/{patientId}
     * 
     * Get all consultations for a patient.
     * Used by ANC workers to see doctor consultations for their patients.
     */
    @GetMapping("/patient/{patientId}")
    public ResponseEntity<List<ConsultationResponseDTO>> getPatientConsultations(
            @PathVariable String patientId) {
        
        log.info("Fetching consultations for patient: {}", patientId);
        List<ConsultationResponseDTO> consultations = consultationService.getPatientConsultations(patientId);
        
        return ResponseEntity.ok(consultations);
    }

    /**
     * GET /api/consultations/stats
     * 
     * Dashboard statistics (optional — for future enhancement).
     */
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getStats() {
        // TODO: Implement dashboard stats
        return ResponseEntity.ok(Map.of(
                "message", "Stats endpoint not yet implemented"
        ));
    }
}
