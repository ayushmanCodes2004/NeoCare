package com.anc.service;

import com.anc.dto.ConsultationRequestDTO;
import com.anc.dto.ConsultationResponseDTO;
import com.anc.entity.AncWorkerEntity;
import com.anc.entity.ConsultationEntity;
import com.anc.entity.DoctorEntity;
import com.anc.entity.PatientEntity;
import com.anc.repository.AncWorkerRepository;
import com.anc.repository.ConsultationRepository;
import com.anc.repository.DoctorRepository;
import com.anc.repository.PatientRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ConsultationService {

    private final ConsultationRepository consultationRepository;
    private final DoctorRepository doctorRepository;
    private final PatientRepository patientRepository;
    private final AncWorkerRepository workerRepository;

    public ConsultationResponseDTO requestConsultation(ConsultationRequestDTO request, UUID workerId) {
        // Validate doctor exists
        DoctorEntity doctor = doctorRepository.findById(request.getDoctorId())
                .orElseThrow(() -> new RuntimeException("Doctor not found"));

        // Validate patient exists
        PatientEntity patient = patientRepository.findById(request.getPatientId())
                .orElseThrow(() -> new RuntimeException("Patient not found"));

        // Create consultation
        ConsultationEntity consultation = ConsultationEntity.builder()
                .patientId(request.getPatientId())
                .workerId(workerId)
                .doctorId(request.getDoctorId())
                .visitId(request.getVisitId())
                .status("REQUESTED")
                .riskLevel(request.getRiskLevel())
                .scheduledAt(request.getScheduledAt())
                .build();

        consultationRepository.save(consultation);

        return buildConsultationResponse(consultation);
    }

    public List<ConsultationResponseDTO> getPendingRequests(UUID doctorId) {
        List<ConsultationEntity> consultations = consultationRepository
                .findPendingRequestsByDoctor(doctorId);
        
        return consultations.stream()
                .map(this::buildConsultationResponse)
                .collect(Collectors.toList());
    }

    public List<ConsultationResponseDTO> getDoctorConsultations(UUID doctorId) {
        List<ConsultationEntity> consultations = consultationRepository
                .findRecentConsultationsByDoctor(doctorId);
        
        return consultations.stream()
                .map(this::buildConsultationResponse)
                .collect(Collectors.toList());
    }

    public ConsultationResponseDTO getConsultationById(UUID consultationId) {
        ConsultationEntity consultation = consultationRepository.findById(consultationId)
                .orElseThrow(() -> new RuntimeException("Consultation not found"));
        
        return buildConsultationResponse(consultation);
    }

    public ConsultationResponseDTO acceptConsultation(UUID consultationId, UUID doctorId) {
        ConsultationEntity consultation = consultationRepository.findById(consultationId)
                .orElseThrow(() -> new RuntimeException("Consultation not found"));

        if (!consultation.getDoctorId().equals(doctorId)) {
            throw new RuntimeException("Unauthorized access");
        }

        consultation.setStatus("SCHEDULED");
        consultationRepository.save(consultation);

        return buildConsultationResponse(consultation);
    }

    public ConsultationResponseDTO startConsultation(UUID consultationId, UUID doctorId, String roomId) {
        ConsultationEntity consultation = consultationRepository.findById(consultationId)
                .orElseThrow(() -> new RuntimeException("Consultation not found"));

        if (!consultation.getDoctorId().equals(doctorId)) {
            throw new RuntimeException("Unauthorized access");
        }

        consultation.setStatus("IN_PROGRESS");
        consultation.setRoomId(roomId);
        consultation.setStartedAt(LocalDateTime.now());
        consultationRepository.save(consultation);

        return buildConsultationResponse(consultation);
    }

    public ConsultationResponseDTO completeConsultation(
            UUID consultationId, 
            UUID doctorId,
            String doctorNotes,
            String prescription,
            String recommendations) {
        
        ConsultationEntity consultation = consultationRepository.findById(consultationId)
                .orElseThrow(() -> new RuntimeException("Consultation not found"));

        if (!consultation.getDoctorId().equals(doctorId)) {
            throw new RuntimeException("Unauthorized access");
        }

        consultation.setStatus("COMPLETED");
        consultation.setCompletedAt(LocalDateTime.now());
        consultation.setDoctorNotes(doctorNotes);
        consultation.setPrescription(prescription);
        consultation.setRecommendations(recommendations);
        consultationRepository.save(consultation);

        return buildConsultationResponse(consultation);
    }

    public void cancelConsultation(UUID consultationId, UUID doctorId) {
        ConsultationEntity consultation = consultationRepository.findById(consultationId)
                .orElseThrow(() -> new RuntimeException("Consultation not found"));

        if (!consultation.getDoctorId().equals(doctorId)) {
            throw new RuntimeException("Unauthorized access");
        }

        consultation.setStatus("CANCELLED");
        consultationRepository.save(consultation);
    }

    public List<ConsultationResponseDTO> getHighRiskConsultations() {
        List<ConsultationEntity> consultations = consultationRepository
                .findHighRiskPendingConsultations();
        
        return consultations.stream()
                .map(this::buildConsultationResponse)
                .collect(Collectors.toList());
    }

    private ConsultationResponseDTO buildConsultationResponse(ConsultationEntity consultation) {
        // Fetch related entities
        PatientEntity patient = patientRepository.findById(consultation.getPatientId())
                .orElse(null);
        
        DoctorEntity doctor = doctorRepository.findById(consultation.getDoctorId())
                .orElse(null);
        
        AncWorkerEntity worker = workerRepository.findById(consultation.getWorkerId())
                .orElse(null);

        return ConsultationResponseDTO.builder()
                .consultationId(consultation.getId())
                .patientId(consultation.getPatientId())
                .patientName(patient != null ? patient.getFullName() : "Unknown")
                .workerId(consultation.getWorkerId())
                .workerName(worker != null ? worker.getFullName() : "Unknown")
                .doctorId(consultation.getDoctorId())
                .doctorName(doctor != null ? doctor.getFullName() : "Unknown")
                .visitId(consultation.getVisitId())
                .status(consultation.getStatus())
                .riskLevel(consultation.getRiskLevel())
                .roomId(consultation.getRoomId())
                .scheduledAt(consultation.getScheduledAt())
                .startedAt(consultation.getStartedAt())
                .completedAt(consultation.getCompletedAt())
                .doctorNotes(consultation.getDoctorNotes())
                .prescription(consultation.getPrescription())
                .recommendations(consultation.getRecommendations())
                .createdAt(consultation.getCreatedAt())
                .build();
    }
}
