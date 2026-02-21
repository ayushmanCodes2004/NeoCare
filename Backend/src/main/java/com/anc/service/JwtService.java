package com.anc.service;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Service;

import java.security.Key;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Function;

/**
 * Service for JWT token generation, validation, and parsing.
 * Implements HMAC-SHA256 signing with 24-hour token expiration.
 * 
 * Requirements: 2.2, 2.6, 2.7, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6
 */
@Service
public class JwtService {

    @Value("${jwt.secret}")
    private String secretKey;

    @Value("${jwt.expiration}")
    private long jwtExpiration;

    /**
     * Generate JWT token with phone as subject and workerId as custom claim.
     * Token expires after 24 hours (86400000 ms).
     * 
     * @param userDetails the user details containing phone number
     * @param workerId the worker's UUID to include as custom claim
     * @return signed JWT token string
     * 
     * Requirements: 2.2, 11.1, 11.2, 11.3, 11.4, 11.5
     */
    public String generateToken(UserDetails userDetails, UUID workerId) {
        Map<String, Object> claims = new HashMap<>();
        claims.put("workerId", workerId.toString());
        
        return Jwts.builder()
                .setClaims(claims)
                .setSubject(userDetails.getUsername()) // phone number as subject
                .setIssuedAt(new Date(System.currentTimeMillis()))
                .setExpiration(new Date(System.currentTimeMillis() + jwtExpiration))
                .signWith(getSigningKey(), SignatureAlgorithm.HS256)
                .compact();
    }

    /**
     * Extract phone number from token subject claim.
     * 
     * @param token the JWT token
     * @return phone number string
     * 
     * Requirements: 11.1, 11.6
     */
    public String extractPhone(String token) {
        return extractClaim(token, Claims::getSubject);
    }

    /**
     * Extract worker ID from custom workerId claim.
     * 
     * @param token the JWT token
     * @return worker UUID
     * 
     * Requirements: 11.2, 11.6
     */
    public UUID extractWorkerId(String token) {
        Claims claims = extractAllClaims(token);
        String workerIdStr = claims.get("workerId", String.class);
        return UUID.fromString(workerIdStr);
    }

    /**
     * Validate token signature and expiration against user details.
     * 
     * @param token the JWT token
     * @param userDetails the user details to validate against
     * @return true if token is valid and not expired, false otherwise
     * 
     * Requirements: 2.6, 11.5
     */
    public boolean isTokenValid(String token, UserDetails userDetails) {
        final String phone = extractPhone(token);
        return (phone.equals(userDetails.getUsername()) && !isTokenExpired(token));
    }

    /**
     * Check if token is expired.
     * 
     * @param token the JWT token
     * @return true if token is expired, false otherwise
     * 
     * Requirements: 2.6, 11.4
     */
    public boolean isTokenExpired(String token) {
        return extractExpiration(token).before(new Date());
    }

    /**
     * Extract expiration date from token.
     * 
     * @param token the JWT token
     * @return expiration date
     */
    private Date extractExpiration(String token) {
        return extractClaim(token, Claims::getExpiration);
    }

    /**
     * Extract a specific claim from token using a claims resolver function.
     * 
     * @param token the JWT token
     * @param claimsResolver function to extract specific claim
     * @param <T> the type of the claim
     * @return the extracted claim value
     */
    private <T> T extractClaim(String token, Function<Claims, T> claimsResolver) {
        final Claims claims = extractAllClaims(token);
        return claimsResolver.apply(claims);
    }

    /**
     * Extract all claims from token.
     * 
     * @param token the JWT token
     * @return all claims
     */
    private Claims extractAllClaims(String token) {
        return Jwts.parser()
                .verifyWith(getSigningKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    /**
     * Get the signing key for HMAC-SHA256 algorithm.
     * Use the secret key directly as UTF-8 bytes (not base64 decoded).
     * 
     * @return signing key
     * 
     * Requirements: 2.7, 11.5
     */
    private javax.crypto.SecretKey getSigningKey() {
        byte[] keyBytes = secretKey.getBytes(java.nio.charset.StandardCharsets.UTF_8);
        return Keys.hmacShaKeyFor(keyBytes);
    }
}
