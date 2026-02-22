package com.anc.util;

import com.anc.entity.AncWorkerEntity;
import com.anc.entity.DoctorEntity;
import com.anc.entity.PatientEntity;
import com.anc.repository.AncWorkerRepository;
import com.anc.repository.DoctorRepository;
import com.anc.repository.PatientRepository;
import com.anc.security.EncryptionService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

/**
 * One-time migration tool to encrypt existing unencrypted data.
 * 
 * HOW TO USE:
 * 1. Uncomment @Component annotation below
 * 2. Start the application - it will run automatically
 * 3. Check logs for migration results
 * 4. Comment out @Component again to prevent re-running
 * 
 * DETECTION:
 * - Encrypted data is Base64 encoded (typically 40+ characters)
 * - Unencrypted data is shorter (e.g., "John Doe" = 8 chars)
 * - This tool checks length to detect unencrypted fields
 * 
 * SAFETY:
 * - Only encrypts fields that appear unencrypted
 * - Skips already encrypted data
 * - Logs all operations
 */
@Slf4j
@RequiredArgsConstructor
// @Component  // UNCOMMENT THIS TO RUN MIGRATION
public class MigrateExistingDataToEncrypted implements CommandLineRunner {

    private final AncWorkerRepository workerRepository;
    private final PatientRepository patientRepository;
    private final DoctorRepository doctorRepository;
    private final EncryptionService encryptionService;

    private static final int MIN_ENCRYPTED_LENGTH = 40; // Base64 encrypted strings are longer

    @Override
    public void run(String... args) {
        log.info("========================================");
        log.info("STARTING DATA ENCRYPTION MIGRATION");
        log.info("========================================");

        migrateWorkers();
        migratePatients();
        migrateDoctors();

        log.info("========================================");
        log.info("MIGRATION COMPLETE");
        log.info("========================================");
    }

    private void migrateWorkers() {
        log.info("Migrating ANC Workers...");
        
        var workers = workerRepository.findAll();
        int encrypted = 0;
        int skipped = 0;

        for (AncWorkerEntity worker : workers) {
            boolean needsUpdate = false;

            // Check and encrypt full_name
            if (worker.getFullName() != null && worker.getFullName().length() < MIN_ENCRYPTED_LENGTH) {
                log.info("Encrypting worker {} full_name: {}", worker.getId(), worker.getFullName());
                worker.setFullName(encryptionService.encrypt(worker.getFullName()));
                needsUpdate = true;
            }

            // Check and encrypt email
            if (worker.getEmail() != null && worker.getEmail().length() < MIN_ENCRYPTED_LENGTH) {
                log.info("Encrypting worker {} email: {}", worker.getId(), worker.getEmail());
                worker.setEmail(encryptionService.encrypt(worker.getEmail()));
                needsUpdate = true;
            }

            // Note: phone is NOT encrypted (used for login)

            if (needsUpdate) {
                workerRepository.save(worker);
                encrypted++;
                log.info("✅ Worker {} encrypted", worker.getId());
            } else {
                skipped++;
            }
        }

        log.info("Workers: {} encrypted, {} already encrypted", encrypted, skipped);
    }

    private void migratePatients() {
        log.info("Migrating Patients...");
        
        var patients = patientRepository.findAll();
        int encrypted = 0;
        int skipped = 0;

        for (PatientEntity patient : patients) {
            boolean needsUpdate = false;

            // Check and encrypt full_name
            if (patient.getFullName() != null && patient.getFullName().length() < MIN_ENCRYPTED_LENGTH) {
                log.info("Encrypting patient {} full_name: {}", patient.getId(), patient.getFullName());
                patient.setFullName(encryptionService.encrypt(patient.getFullName()));
                needsUpdate = true;
            }

            // Check and encrypt address
            if (patient.getAddress() != null && patient.getAddress().length() < MIN_ENCRYPTED_LENGTH) {
                log.info("Encrypting patient {} address: {}", patient.getId(), patient.getAddress());
                patient.setAddress(encryptionService.encrypt(patient.getAddress()));
                needsUpdate = true;
            }

            // Note: phone is NOT encrypted (used for search)

            if (needsUpdate) {
                patientRepository.save(patient);
                encrypted++;
                log.info("✅ Patient {} encrypted", patient.getId());
            } else {
                skipped++;
            }
        }

        log.info("Patients: {} encrypted, {} already encrypted", encrypted, skipped);
    }

    private void migrateDoctors() {
        log.info("Migrating Doctors...");
        
        var doctors = doctorRepository.findAll();
        int encrypted = 0;
        int skipped = 0;

        for (DoctorEntity doctor : doctors) {
            boolean needsUpdate = false;

            // Check and encrypt full_name
            if (doctor.getFullName() != null && doctor.getFullName().length() < MIN_ENCRYPTED_LENGTH) {
                log.info("Encrypting doctor {} full_name: {}", doctor.getId(), doctor.getFullName());
                doctor.setFullName(encryptionService.encrypt(doctor.getFullName()));
                needsUpdate = true;
            }

            // Check and encrypt email
            if (doctor.getEmail() != null && doctor.getEmail().length() < MIN_ENCRYPTED_LENGTH) {
                log.info("Encrypting doctor {} email: {}", doctor.getId(), doctor.getEmail());
                doctor.setEmail(encryptionService.encrypt(doctor.getEmail()));
                needsUpdate = true;
            }

            // Note: phone is NOT encrypted (used for login)

            if (needsUpdate) {
                doctorRepository.save(doctor);
                encrypted++;
                log.info("✅ Doctor {} encrypted", doctor.getId());
            } else {
                skipped++;
            }
        }

        log.info("Doctors: {} encrypted, {} already encrypted", encrypted, skipped);
    }
}
