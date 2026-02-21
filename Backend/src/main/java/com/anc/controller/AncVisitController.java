package com.anc.controller;

import com.anc.dto.AncVisitRequestDTO;
import com.anc.dto.AncVisitResponseDTO;
import com.anc.entity.AncVisitEntity;
import com.anc.service.AncVisitService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/anc")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class AncVisitController {

    private final AncVisitService visitService;

    @PostMapping("/register-visit")
    public ResponseEntity<AncVisitResponseDTO> registerVisit(
            @Valid @RequestBody AncVisitRequestDTO request) {
        
        log.info("POST /api/anc/register-visit - patientId: {}", request.getPatientId());
        AncVisitResponseDTO response = visitService.registerVisit(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/visits/{visitId}")
    public ResponseEntity<AncVisitEntity> getVisit(@PathVariable String visitId) {
        log.info("GET /api/anc/visits/{}", visitId);
        AncVisitEntity visit = visitService.getVisitById(visitId);
        return ResponseEntity.ok(visit);
    }

    @GetMapping("/patients/{patientId}/visits")
    public ResponseEntity<List<AncVisitEntity>> getPatientVisits(
            @PathVariable String patientId) {
        
        log.info("GET /api/anc/patients/{}/visits", patientId);
        List<AncVisitEntity> visits = visitService.getVisitsByPatientId(patientId);
        return ResponseEntity.ok(visits);
    }

    @GetMapping("/visits/high-risk")
    public ResponseEntity<List<AncVisitEntity>> getHighRiskVisits() {
        log.info("GET /api/anc/visits/high-risk");
        List<AncVisitEntity> visits = visitService.getHighRiskVisits();
        return ResponseEntity.ok(visits);
    }

    @GetMapping("/visits/critical")
    public ResponseEntity<List<AncVisitEntity>> getCriticalVisits() {
        log.info("GET /api/anc/visits/critical");
        List<AncVisitEntity> visits = visitService.getCriticalVisits();
        return ResponseEntity.ok(visits);
    }

    @GetMapping("/visits/risk-level/{riskLevel}")
    public ResponseEntity<List<AncVisitEntity>> getVisitsByRiskLevel(
            @PathVariable String riskLevel) {
        
        log.info("GET /api/anc/visits/risk-level/{}", riskLevel);
        List<AncVisitEntity> visits = visitService.getVisitsByRiskLevel(riskLevel);
        return ResponseEntity.ok(visits);
    }
}
