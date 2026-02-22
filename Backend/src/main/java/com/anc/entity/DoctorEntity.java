package com.anc.entity;

import com.anc.security.EncryptedStringConverter;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.time.LocalDateTime;
import java.util.Collection;
import java.util.List;

/**
 * Doctor account entity.
 *
 * Implements UserDetails — same pattern as AncWorkerEntity.
 * Login identifier: phone number (unique across ALL users — workers + doctors)
 * Role: "ROLE_DOCTOR" returned in getAuthorities()
 *
 * isAvailable: doctor can toggle ON/OFF to accept consultations.
 */
@Entity
@Table(name = "doctors")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DoctorEntity implements UserDetails {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id", updatable = false, nullable = false)
    private String id;

    @Convert(converter = EncryptedStringConverter.class)
    @Column(name = "full_name", nullable = false, length = 500)
    private String fullName;

    /** Phone = unique login identifier across the entire system - cannot be encrypted */
    @Column(name = "phone", nullable = false, unique = true, length = 15)
    private String phone;

    @Convert(converter = EncryptedStringConverter.class)
    @Column(name = "email", unique = true, length = 500)
    private String email;

    @Column(name = "password_hash", nullable = false)
    private String passwordHash;

    /** e.g. "Obstetrics & Gynaecology" */
    @Column(name = "specialization")
    private String specialization;

    @Column(name = "hospital")
    private String hospital;

    @Column(name = "district")
    private String district;

    /** Medical council registration number */
    @Column(name = "registration_no", length = 100)
    private String registrationNo;

    /** Account active flag — false blocks login */
    @Column(name = "is_active")
    @Builder.Default
    private Boolean isActive = true;

    /** Availability toggle — false means doctor won't receive new consultations */
    @Column(name = "is_available")
    @Builder.Default
    private Boolean isAvailable = true;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    // ─── UserDetails ──────────────────────────────────────────────────────────

    /** ROLE_DOCTOR — used by SecurityConfig to restrict doctor-only endpoints */
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return List.of(new SimpleGrantedAuthority("ROLE_DOCTOR"));
    }

    @Override
    public String getPassword() { return passwordHash; }

    @Override
    public String getUsername() { return phone; }

    @Override
    public boolean isAccountNonExpired() { return true; }

    @Override
    public boolean isAccountNonLocked() { return Boolean.TRUE.equals(isActive); }

    @Override
    public boolean isCredentialsNonExpired() { return true; }

    @Override
    public boolean isEnabled() { return Boolean.TRUE.equals(isActive); }
}
