package com.anc.entity;

import com.anc.security.EncryptedStringConverter;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

/**
 * Consultation request — created automatically when a visit is high risk.
 *
 * Links: visit → patient → worker → doctor
 * Tracks: status lifecycle, video call URLs/tokens, doctor's notes.
 *
 * Priority queue: ORDER BY priority_score DESC, created_at ASC
 *   CRITICAL = 100 (shown first)
 *   HIGH     = 70
 *   MEDIUM   = 40
 */
@Entity
@Table(name = "consultations")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ConsultationEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id", updatable = false, nullable = false)
    private String id;

    // ─── Linked records ───────────────────────────────────────────────────────
    @Column(name = "visit_id", nullable = false)
    private String visitId;

    @Column(name = "patient_id", nullable = false)
    private String patientId;

    @Column(name = "worker_id", nullable = false)
    private String workerId;

    /** Null until a doctor accepts the consultation */
    @Column(name = "doctor_id")
    private String doctorId;

    // ─── Risk info (copied from visit) ────────────────────────────────────────
    @Column(name = "risk_level", nullable = false, length = 20)
    private String riskLevel;

    @Column(name = "is_high_risk")
    private Boolean isHighRisk;

    /**
     * Numeric priority for ORDER BY:
     *   CRITICAL = 100, HIGH = 70, MEDIUM = 40
     */
    @Column(name = "priority_score")
    private Integer priorityScore;

    // ─── Status lifecycle ─────────────────────────────────────────────────────
    /**
     * PENDING    → waiting for a doctor to accept
     * ACCEPTED   → doctor accepted, video call not yet started
     * IN_PROGRESS→ video call active
     * COMPLETED  → doctor submitted notes
     * CANCELLED  → worker or system cancelled
     */
    @Column(name = "status", nullable = false, length = 30)
    @Builder.Default
    private String status = "PENDING";

    // ─── Video call (Daily.co) ────────────────────────────────────────────────
    /** Daily.co room URL e.g. "https://anc.daily.co/consult-uuid" */
    @Column(name = "room_url", length = 500)
    private String roomUrl;

    /** Meeting token for doctor — passed to Daily.co JS SDK */
    @Column(name = "doctor_token", columnDefinition = "TEXT")
    private String doctorToken;

    /** Meeting token for ANC worker — passed via notification */
    @Column(name = "worker_token", columnDefinition = "TEXT")
    private String workerToken;

    // ─── Doctor's notes (filled on COMPLETED) ────────────────────────────────
    @Convert(converter = EncryptedStringConverter.class)
    @Column(name = "doctor_notes", columnDefinition = "TEXT")
    private String doctorNotes;

    @Convert(converter = EncryptedStringConverter.class)
    @Column(name = "diagnosis", columnDefinition = "TEXT")
    private String diagnosis;

    @Convert(converter = EncryptedStringConverter.class)
    @Column(name = "action_plan", columnDefinition = "TEXT")
    private String actionPlan;

    // ─── Timestamps ───────────────────────────────────────────────────────────
    @Column(name = "accepted_at")
    private LocalDateTime acceptedAt;

    @Column(name = "call_started_at")
    private LocalDateTime callStartedAt;

    @Column(name = "completed_at")
    private LocalDateTime completedAt;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
