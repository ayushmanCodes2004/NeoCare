package com.anc.security;

import jakarta.persistence.AttributeConverter;
import jakarta.persistence.Converter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

/**
 * JPA AttributeConverter for automatic field-level encryption/decryption
 * 
 * Usage: Add @Convert(converter = EncryptedStringConverter.class) to entity fields
 * 
 * Automatically:
 * - Encrypts data before saving to database
 * - Decrypts data when reading from database
 */
@Converter
@Component
public class EncryptedStringConverter implements AttributeConverter<String, String> {

    private static EncryptionService encryptionService;

    @Autowired
    public void setEncryptionService(EncryptionService service) {
        EncryptedStringConverter.encryptionService = service;
    }

    @Override
    public String convertToDatabaseColumn(String attribute) {
        if (attribute == null) {
            return null;
        }
        return encryptionService.encrypt(attribute);
    }

    @Override
    public String convertToEntityAttribute(String dbData) {
        if (dbData == null) {
            return null;
        }
        return encryptionService.decrypt(dbData);
    }
}
