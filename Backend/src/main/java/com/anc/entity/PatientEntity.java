package com.anc.entity;

import com.anc.security.EncryptedStringConverter;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "patients", indexes = {
    @Index(name = "idx_patients_worker_id", columnList = "worker_id"),
    @Index(name = "idx_patients_phone", columnList = "phone"),
    @Index(name = "idx_patients_district", columnList = "district")
})
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PatientEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id", updatable = false, nullable = false)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "worker_id", nullable = false)
    private AncWorkerEntity worker;

    @Convert(converter = EncryptedStringConverter.class)
    @Column(name = "full_name", nullable = false, length = 500)
    private String fullName;

    // Phone is searchable - keep unencrypted for queries
    @Column(name = "phone", nullable = false, length = 15)
    private String phone;

    @Column(name = "age", nullable = false)
    private Integer age;

    @Convert(converter = EncryptedStringConverter.class)
    @Column(name = "address", nullable = false, length = 1000)
    private String address;

    @Column(name = "village", nullable = false)
    private String village;

    @Column(name = "district", nullable = false)
    private String district;

    @Column(name = "lmp_date", nullable = false)
    private LocalDate lmpDate;

    @Column(name = "edd_date", nullable = false)
    private LocalDate eddDate;

    @Column(name = "blood_group", length = 10)
    private String bloodGroup;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
