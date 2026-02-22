package com.anc.security;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.util.Base64;

/**
 * AES-256-GCM Encryption Service for sensitive patient data
 * 
 * Features:
 * - AES-256 encryption (industry standard)
 * - GCM mode (authenticated encryption)
 * - Random IV for each encryption (prevents pattern analysis)
 * - Base64 encoding for database storage
 */
@Service
public class EncryptionService {

    private static final String ALGORITHM = "AES/GCM/NoPadding";
    private static final int GCM_IV_LENGTH = 12; // 96 bits
    private static final int GCM_TAG_LENGTH = 128; // 128 bits

    @Value("${app.encryption.key:CHANGE_THIS_TO_32_BYTE_SECRET_KEY_IN_PRODUCTION!!}")
    private String encryptionKey;

    /**
     * Encrypt plaintext data
     * 
     * @param plaintext Data to encrypt
     * @return Base64-encoded encrypted data with IV prepended
     */
    public String encrypt(String plaintext) {
        if (plaintext == null || plaintext.isEmpty()) {
            return plaintext;
        }

        try {
            // Generate random IV for this encryption
            byte[] iv = new byte[GCM_IV_LENGTH];
            SecureRandom random = new SecureRandom();
            random.nextBytes(iv);

            // Create cipher
            Cipher cipher = Cipher.getInstance(ALGORITHM);
            SecretKeySpec keySpec = new SecretKeySpec(getKeyBytes(), "AES");
            GCMParameterSpec gcmSpec = new GCMParameterSpec(GCM_TAG_LENGTH, iv);
            cipher.init(Cipher.ENCRYPT_MODE, keySpec, gcmSpec);

            // Encrypt
            byte[] encrypted = cipher.doFinal(plaintext.getBytes(StandardCharsets.UTF_8));

            // Combine IV + encrypted data
            ByteBuffer byteBuffer = ByteBuffer.allocate(iv.length + encrypted.length);
            byteBuffer.put(iv);
            byteBuffer.put(encrypted);

            // Encode to Base64 for storage
            return Base64.getEncoder().encodeToString(byteBuffer.array());

        } catch (Exception e) {
            throw new RuntimeException("Encryption failed", e);
        }
    }

    /**
     * Decrypt encrypted data
     * 
     * @param ciphertext Base64-encoded encrypted data with IV
     * @return Decrypted plaintext
     */
    public String decrypt(String ciphertext) {
        if (ciphertext == null || ciphertext.isEmpty()) {
            return ciphertext;
        }

        try {
            // Decode from Base64
            byte[] decoded = Base64.getDecoder().decode(ciphertext);

            // Extract IV and encrypted data
            ByteBuffer byteBuffer = ByteBuffer.wrap(decoded);
            byte[] iv = new byte[GCM_IV_LENGTH];
            byteBuffer.get(iv);
            byte[] encrypted = new byte[byteBuffer.remaining()];
            byteBuffer.get(encrypted);

            // Create cipher
            Cipher cipher = Cipher.getInstance(ALGORITHM);
            SecretKeySpec keySpec = new SecretKeySpec(getKeyBytes(), "AES");
            GCMParameterSpec gcmSpec = new GCMParameterSpec(GCM_TAG_LENGTH, iv);
            cipher.init(Cipher.DECRYPT_MODE, keySpec, gcmSpec);

            // Decrypt
            byte[] decrypted = cipher.doFinal(encrypted);
            return new String(decrypted, StandardCharsets.UTF_8);

        } catch (Exception e) {
            throw new RuntimeException("Decryption failed", e);
        }
    }

    /**
     * Get encryption key as bytes
     * Ensures key is exactly 32 bytes for AES-256
     */
    private byte[] getKeyBytes() {
        byte[] key = encryptionKey.getBytes(StandardCharsets.UTF_8);
        if (key.length != 32) {
            // Pad or truncate to 32 bytes
            byte[] paddedKey = new byte[32];
            System.arraycopy(key, 0, paddedKey, 0, Math.min(key.length, 32));
            return paddedKey;
        }
        return key;
    }
}
