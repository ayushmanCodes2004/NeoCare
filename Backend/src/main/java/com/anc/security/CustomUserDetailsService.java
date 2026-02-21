package com.anc.security;

import com.anc.repository.AncWorkerRepository;
import com.anc.repository.DoctorRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

/**
 * Custom UserDetailsService implementation for loading user details.
 * Supports both ANC workers (by phone) and doctors (by email).
 * Used by Spring Security for authentication.
 * 
 * Requirements: 3.2, 19.6
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class CustomUserDetailsService implements UserDetailsService {

    private final AncWorkerRepository ancWorkerRepository;
    private final DoctorRepository doctorRepository;

    /**
     * Load user details by username (phone for workers, email for doctors).
     * First tries to find an ANC worker by phone, then tries to find a doctor by email.
     * 
     * @param username the phone number or email to search for
     * @return UserDetails object containing user information
     * @throws UsernameNotFoundException if user is not found
     * 
     * Requirements: 3.2, 19.6
     */
    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        log.debug("Loading user details for username: {}", username);
        
        // Try to find ANC worker by phone
        var worker = ancWorkerRepository.findByPhone(username);
        if (worker.isPresent()) {
            log.debug("Found ANC worker with phone: {}", username);
            return worker.get();
        }
        
        // Try to find doctor by email
        var doctor = doctorRepository.findByEmail(username);
        if (doctor.isPresent()) {
            log.debug("Found doctor with email: {}", username);
            return doctor.get();
        }
        
        log.warn("User not found with username: {}", username);
        throw new UsernameNotFoundException("User not found with username: " + username);
    }
}
