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
 * Updated to check BOTH anc_workers and doctors tables by phone number.
 * 
 * Spring Security calls loadUserByUsername(phone) for every authenticated request.
 * We try the worker table first, then the doctor table.
 * If neither has this phone: throw UsernameNotFoundException → 401.
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
     * Load user details by phone number.
     * Checks both ANC workers and doctors tables.
     * 
     * @param phone the phone number to search for
     * @return UserDetails object containing user information
     * @throws UsernameNotFoundException if user is not found
     * 
     * Requirements: 3.2, 19.6
     */
    @Override
    public UserDetails loadUserByUsername(String phone) throws UsernameNotFoundException {
        log.debug("Loading user by phone: {}", phone);
        
        // Check ANC workers first
        var worker = ancWorkerRepository.findByPhone(phone);
        if (worker.isPresent()) {
            log.debug("Found ANC worker for phone: {}", phone);
            return worker.get();
        }
        
        // Then check doctors
        var doctor = doctorRepository.findByPhone(phone);
        if (doctor.isPresent()) {
            log.debug("Found doctor for phone: {}", phone);
            return doctor.get();
        }
        
        log.warn("No user found for phone: {}", phone);
        throw new UsernameNotFoundException("No user registered with phone: " + phone);
    }
}
