# How to Implement Data Encryption - Step by Step

## 🎯 Goal
Encrypt sensitive patient data in the database using AES-256 encryption.

---

## 📦 Step 1: Add Encryption Dependency

Add to `pom.xml`:

```xml
<!-- AES Encryption -->
<dependency>
    <groupId>org.jasypt</groupId>
    <artifactId>jasypt-spring-boot-starter</artifactId>
    <version>3.0.5</version>
</dependency>
```

---

## 🔑 Step 2: Create Encryption Utility

Create `Backend/src/main/java/com/anc/util/EncryptionUtil.java`:

```java
package com.anc.util;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.util.Base64;

public class EncryptionUtil {
    
    private static final String ALGORITHM = "AES/GCM/NoPadding";
    private static final int TAG_LENGTH_BIT = 128;
    private static final int IV_LENGTH_BYTE = 12;
    private static final int AES_KEY_BIT = 256;
    
    // Get encryption key from environment variable
    private static final String ENCRYPTION_KEY = System.getenv("DB_ENCRYPTION_KEY");
    
    /**
     * Encrypt a string using AES-256-GCM
     */
    public static String encrypt(String plainText) {
        if (plainText == null || plainText.isEmpty()) {
            return plainText;
        }
        
        try {
            // Generate IV
            byte[] iv = new byte[IV_LENGTH_BYTE];
            SecureRandom random = new SecureRandom();
            random.nextBytes(iv);
            
            // Get cipher instance
            Cipher cipher = Cipher.getInstance(ALGORITHM);
            
            // Get secret key
            SecretKey secretKey = getSecretKey();
            
            // Initialize cipher
            GCMParameterSpec parameterSpec = new GCMParameterSpec(TAG_LENGTH_BIT, iv);
            cipher.init(Cipher.ENCRYPT_MODE, secretKey, parameterSpec);
            
            // Encrypt
            byte[] encryptedBytes = cipher.doFinal(plainText.getBytes(StandardCharsets.UTF_8));
            
            // Combine IV and encrypted data
            ByteBuffer byteBuffer = ByteBuffer.allocate(iv.length + encryptedBytes.length);
            byteBuffer.put(iv);
            byteBuffer.put(encryptedBytes);
            
            // Encode to Base64
            return Base64.getEncoder().encodeToString(byteBuffer.array());
            
        } catch (Exception e) {
            throw new RuntimeException("Error encrypting data", e);
        }
    }
    
    /**
     * Decrypt a string using AES-256-GCM
     */
    public static String decrypt(String encryptedText) {
        if (encryptedText == null || encryptedText.isEmpty()) {
            return encryptedText;
        }
        
        try {
            // Decode from Base64
            byte[] decodedBytes = Base64.getDecoder().decode(encryptedText);
            
            // Extract IV and encrypted data
            ByteBuffer byteBuffer = ByteBuffer.wrap(decodedBytes);
            byte[] iv = new byte[IV_LENGTH_BYTE];
            byteBuffer.get(iv);
            byte[] encryptedBytes = new byte[byteBuffer.remaining()];
            byteBuffer.get(encryptedBytes);
            
            // Get cipher instance
            Cipher cipher = Cipher.getInstance(ALGORITHM);
            
            // Get secret key
            SecretKey secretKey = getSecretKey();
            
            // Initialize cipher
            GCMParameterSpec parameterSpec = new GCMParameterSpec(TAG_LENGTH_BIT, iv);
            cipher.init(Cipher.DECRYPT_MODE, secretKey, parameterSpec);
            
            // Decrypt
            byte[] decryptedBytes = cipher.doFinal(encryptedBytes);
            
            return new String(decryptedBytes, StandardCharsets.UTF_8);
            
        } catch (Exception e) {
            throw new RuntimeException("Error decrypting data", e);
        }
    }
    
    /**
     * Get secret key from environment variable
     */
    private static SecretKey getSecretKey() {
        if (ENCRYPTION_KEY == null || ENCRYPTION_KEY.isEmpty()) {
            throw new IllegalStateException("DB_ENCRYPTION_KEY environment variable not set");
        }
        
        // Use first 32 bytes of key (256 bits)
        byte[] keyBytes = ENCRYPTION_KEY.getBytes(StandardCharsets.UTF_8);
        byte[] key = new byte[32];
        System.arraycopy(keyBytes, 0, key, 0, Math.min(keyBytes.length, 32));
        
        return new SecretKeySpec(key, "AES");
    }
    
    /**
     * Generate a new encryption key (run once, save to environment)
     */
    public static String generateKey() throws Exception {
        KeyGenerator keyGenerator = KeyGenerator.getInstance("AES");
        keyGenerator.init(AES_KEY_BIT);
        SecretKey secretKey = keyGenerator.generateKey();
        return Base64.getEncoder().encodeToString(secretKey.getEncoded());
    }
}
```

---

## 🔧 Step 3: Create JPA Converter

Create `Backend/src/main/java/com/anc/converter/StringEncryptionConverter.java`:

```java
package com.anc.converter;

import com.anc.util.EncryptionUtil;
import jakarta.persistence.AttributeConverter;
import jakarta.persistence.Converter;

@Converter
public class StringEncryptionConverter implements AttributeConverter<String, String> {
    
    @Override
    public String convertToDatabaseColumn(String attribute) {
        // Encrypt before storing in database
        return EncryptionUtil.encrypt(attribute);
    }
    
    @Override
    public String convertToEntityAttribute(String dbData) {
        // Decrypt when reading from database
        return EncryptionUtil.decrypt(dbData);
    }
}
```

---

## 📝 Step 4: Apply Encryption to Entities

### Update PatientEntity.java

```java
package com.anc.entity;

import com.anc.converter.StringEncryptionConverter;
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

    // ✅ ENCRYPTED FIELDS
    @Convert(converter = StringEncryptionConverter.class)
    @Column(name = "full_name", nullable = false, length = 500)
    private String fullName;

    @Convert(converter = StringEncryptionConverter.class)
    @Column(name = "phone", nullable = false, length = 500)
    private String phone;

    @Convert(converter = StringEncryptionConverter.class)
    @Column(name = "address", nullable = false, length = 1000)
    private String address;

    @Convert(converter = StringEncryptionConverter.class)
    @Column(name = "village", nullable = false, length = 500)
    private String village;

    // ❌ NOT ENCRYPTED (can be used for filtering)
    @Column(name = "age", nullable = false)
    private Integer age;

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
```

### Update AncWorkerEntity.java

```java
// Add encryption to sensitive fields
@Convert(converter = StringEncryptionConverter.class)
@Column(name = "full_name", nullable = false, length = 500)
private String fullName;

@Convert(converter = StringEncryptionConverter.class)
@Column(name = "email", unique = true, nullable = false, length = 500)
private String email;

// Phone should NOT be encrypted (used for login/lookup)
@Column(name = "phone", unique = true, nullable = false, length = 10)
private String phone;
```

---

## 🔑 Step 5: Generate and Set Encryption Key

### Generate Key

Create a temporary main class:

```java
public class KeyGenerator {
    public static void main(String[] args) throws Exception {
        String key = EncryptionUtil.generateKey();
        System.out.println("Generated Encryption Key:");
        System.out.println(key);
        System.out.println("\nSet this as environment variable:");
        System.out.println("export DB_ENCRYPTION_KEY=\"" + key + "\"");
    }
}
```

Run it once to generate a key.

### Set Environment Variable

**Windows**:
```cmd
setx DB_ENCRYPTION_KEY "your-generated-key-here"
```

**Linux/Mac**:
```bash
export DB_ENCRYPTION_KEY="your-generated-key-here"
```

**For permanent storage**, add to:
- Windows: System Environment Variables
- Linux/Mac: `~/.bashrc` or `~/.zshrc`

---

## 🗄️ Step 6: Migrate Existing Data

Create a migration script to encrypt existing data:

```java
@Service
public class DataMigrationService {
    
    @Autowired
    private PatientRepository patientRepository;
    
    @Transactional
    public void encryptExistingData() {
        List<PatientEntity> patients = patientRepository.findAll();
        
        for (PatientEntity patient : patients) {
            // Re-save will trigger encryption
            patientRepository.save(patient);
        }
        
        System.out.println("Encrypted " + patients.size() + " patient records");
    }
}
```

Run once after deployment:
```java
@PostConstruct
public void init() {
    if (needsMigration()) {
        dataMigrationService.encryptExistingData();
    }
}
```

---

## ⚠️ Important Notes

### What to Encrypt:
✅ Patient names
✅ Phone numbers (except if used for lookup)
✅ Addresses
✅ Email addresses
✅ Any PII (Personally Identifiable Information)

### What NOT to Encrypt:
❌ IDs (UUIDs)
❌ Foreign keys
❌ Timestamps
❌ Fields used for filtering/searching (district, age)
❌ Passwords (already hashed with BCrypt)

### Performance Impact:
- Encryption adds ~1-2ms per field
- Minimal impact for typical use cases
- Cannot search encrypted fields directly

### Column Size:
- Encrypted data is larger (Base64 encoded)
- Increase column length: `length = 500` or `length = 1000`

---

## 🧪 Testing

### Test Encryption

```java
@Test
public void testEncryption() {
    String original = "John Doe";
    String encrypted = EncryptionUtil.encrypt(original);
    String decrypted = EncryptionUtil.decrypt(encrypted);
    
    assertNotEquals(original, encrypted);
    assertEquals(original, decrypted);
}
```

### Test Entity

```java
@Test
public void testPatientEncryption() {
    PatientEntity patient = PatientEntity.builder()
        .fullName("Jane Smith")
        .phone("9876543210")
        .address("123 Main St")
        .build();
    
    patientRepository.save(patient);
    
    // Verify data is encrypted in database
    String encryptedName = jdbcTemplate.queryForObject(
        "SELECT full_name FROM patients WHERE id = ?",
        String.class,
        patient.getId()
    );
    
    assertNotEquals("Jane Smith", encryptedName);
    
    // Verify data is decrypted when retrieved
    PatientEntity retrieved = patientRepository.findById(patient.getId()).get();
    assertEquals("Jane Smith", retrieved.getFullName());
}
```

---

## 📋 Deployment Checklist

- [ ] Add Jasypt dependency to pom.xml
- [ ] Create EncryptionUtil class
- [ ] Create StringEncryptionConverter
- [ ] Generate encryption key
- [ ] Set DB_ENCRYPTION_KEY environment variable
- [ ] Update PatientEntity with @Convert annotations
- [ ] Update AncWorkerEntity with @Convert annotations
- [ ] Increase column lengths in database
- [ ] Test encryption/decryption
- [ ] Migrate existing data
- [ ] Deploy to production
- [ ] Verify encrypted data in database

---

## 🔐 Security Best Practices

1. **Never commit encryption key to Git**
2. **Use different keys for dev/staging/production**
3. **Rotate keys periodically (every 6-12 months)**
4. **Backup encryption key securely**
5. **Use environment variables, not config files**
6. **Monitor for encryption failures**
7. **Test decryption before deploying**

---

## 💾 Backup Strategy

Before implementing encryption:
1. Backup entire database
2. Test encryption on copy first
3. Verify decryption works
4. Then apply to production

---

## 🆘 Troubleshooting

### Error: "DB_ENCRYPTION_KEY environment variable not set"
**Solution**: Set the environment variable and restart application

### Error: "Error decrypting data"
**Solution**: Encryption key changed or data corrupted. Restore from backup.

### Error: "Data too long for column"
**Solution**: Increase column length to accommodate encrypted data

### Performance Issues
**Solution**: Add database indexes on non-encrypted fields used for filtering

---

## 📊 Encryption Status After Implementation

### Before:
- ❌ Patient names: Plain text
- ❌ Phone numbers: Plain text
- ❌ Addresses: Plain text
- ✅ Passwords: BCrypt hashed

### After:
- ✅ Patient names: AES-256 encrypted
- ✅ Phone numbers: AES-256 encrypted
- ✅ Addresses: AES-256 encrypted
- ✅ Passwords: BCrypt hashed

**Security Score**: 4/10 → 8/10

---

## 🎯 Next Steps

After implementing database encryption:
1. Move other secrets to environment variables
2. Enable HTTPS
3. Enable database SSL
4. Restrict CORS
5. Add audit logging

See `SECURITY_AUDIT.md` for complete security roadmap.
