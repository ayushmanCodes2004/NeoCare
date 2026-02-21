package com.anc.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.time.LocalDateTime;
import java.util.Collection;
import java.util.Collections;
import java.util.UUID;

@Entity
@Table(name = "anc_workers", indexes = {
    @Index(name = "idx_anc_workers_phone", columnList = "phone", unique = true),
    @Index(name = "idx_anc_workers_district", columnList = "district")
})
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AncWorkerEntity implements UserDetails {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id", updatable = false, nullable = false)
    private UUID id;

    @Column(name = "full_name", nullable = false)
    private String fullName;

    @Column(name = "phone", unique = true, nullable = false, length = 10)
    private String phone;

    @Column(name = "email", unique = true, nullable = false)
    private String email;

    @Column(name = "password_hash", nullable = false)
    private String passwordHash;

    @Column(name = "health_center", nullable = false)
    private String healthCenter;

    @Column(name = "district", nullable = false)
    private String district;

    @Column(name = "is_active", nullable = false)
    @Builder.Default
    private Boolean isActive = true;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    // ── UserDetails Interface Implementation ──────────────────────────────

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        // Return empty list as per requirement 16.4
        return Collections.emptyList();
    }

    @Override
    public String getPassword() {
        // Return password_hash as per requirement 16.3
        return passwordHash;
    }

    @Override
    public String getUsername() {
        // Return phone number as per requirement 16.2
        return phone;
    }

    @Override
    public boolean isAccountNonExpired() {
        // Always return true as per requirement 16.6
        return true;
    }

    @Override
    public boolean isAccountNonLocked() {
        // Return false when is_active is false as per requirement 16.5
        return isActive;
    }

    @Override
    public boolean isCredentialsNonExpired() {
        // Always return true as per requirement 16.7
        return true;
    }

    @Override
    public boolean isEnabled() {
        // Return the value of is_active as per requirement 16.8
        return isActive;
    }
}
