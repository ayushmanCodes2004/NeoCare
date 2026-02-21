package com.anc.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "consultations")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ConsultationEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false)
    private UUID patientId;

    @Column(nullable = false)
    private UUID workerId;

    @Column(nullable = false)
    private UUID doctorId;

    @Column(nullable = false)
    private String visitId; // Reference to ANC visit

    @Column(nullable = false)
    private String status; // REQUESTED, SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED

    @Column(nullable = false)
    private String riskLevel; // LOW, HIGH, CRITICAL

    private String roomId; // Video call room ID

    private LocalDateTime scheduledAt;

    private LocalDateTime startedAt;

    private LocalDateTime completedAt;

    @Column(length = 2000)
    private String doctorNotes;

    @Column(length = 2000)
    private String prescription;

    @Column(length = 1000)
    private String recommendations;

    @Column(updatable = false)
    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
