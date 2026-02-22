package com.anc.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

/**
 * Manages Daily.co video rooms for teleconsultation.
 *
 * HOW DAILY.CO WORKS:
 *   1. Create a room via Daily.co REST API → get room URL
 *   2. Generate meeting tokens for doctor + worker (with different permissions)
 *   3. React embeds Daily.co using their JS SDK (@daily-co/daily-js)
 *      or iframe with the room URL + token
 *
 * FREE TIER: daily.co free plan supports up to 200 participants/month.
 *
 * Get API key at: https://dashboard.daily.co/
 */
@Slf4j
@Service
public class VideoSessionService {

    @Value("${daily.api-key:}")
    private String dailyApiKey;

    @Value("${daily.base-url:https://api.daily.co/v1}")
    private String dailyBaseUrl;

    @Value("${daily.domain:anc-portal}")
    private String dailyDomain;

    private final RestTemplate restTemplate;

    public VideoSessionService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    /**
     * Create a Daily.co room for a consultation.
     * Room name = "consult-{consultationId}" (first 8 chars of UUID)
     *
     * @return room URL e.g. "https://anc-portal.daily.co/consult-abc12345"
     */
    public String createRoom(String consultationId) {
        String roomName = "consult-" + consultationId.substring(0, 8);
        String url      = dailyBaseUrl + "/rooms";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("Authorization", "Bearer " + dailyApiKey);

        Map<String, Object> properties = new HashMap<>();
        properties.put("exp", (System.currentTimeMillis() / 1000) + 7200); // 2 hour expiry
        properties.put("enable_chat", true);
        properties.put("enable_screenshare", false);
        properties.put("max_participants", 2);  // doctor + worker only

        Map<String, Object> body = new HashMap<>();
        body.put("name", roomName);
        body.put("privacy", "private");
        body.put("properties", properties);

        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(body, headers);

        try {
            ResponseEntity<Map> response = restTemplate.exchange(url, HttpMethod.POST, entity, Map.class);
            String roomUrl = (String) response.getBody().get("url");
            log.info("Daily.co room created: {}", roomUrl);
            return roomUrl;
        } catch (Exception e) {
            log.error("Failed to create Daily.co room: {}", e.getMessage());
            // Fallback: return a placeholder URL (for dev/testing without Daily.co key)
            return "https://" + dailyDomain + ".daily.co/" + roomName;
        }
    }

    /**
     * Generate a meeting token for a participant.
     *
     * @param roomName   the Daily.co room name
     * @param userName   display name in the call
     * @param isOwner    true for doctor (owner = can end call, mute others)
     * @return token string to pass to Daily.co JS SDK
     */
    public String generateToken(String roomName, String userName, boolean isOwner) {
        String url = dailyBaseUrl + "/meeting-tokens";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("Authorization", "Bearer " + dailyApiKey);

        Map<String, Object> properties = new HashMap<>();
        properties.put("room_name", roomName);
        properties.put("user_name", userName);
        properties.put("is_owner", isOwner);
        properties.put("exp", (System.currentTimeMillis() / 1000) + 7200);
        properties.put("enable_recording", false);

        Map<String, Object> body = new HashMap<>();
        body.put("properties", properties);

        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(body, headers);

        try {
            ResponseEntity<Map> response = restTemplate.exchange(url, HttpMethod.POST, entity, Map.class);
            return (String) response.getBody().get("token");
        } catch (Exception e) {
            log.error("Failed to generate Daily.co token: {}", e.getMessage());
            return "dev-token-" + userName.replaceAll("\\s", "-");
        }
    }
}
