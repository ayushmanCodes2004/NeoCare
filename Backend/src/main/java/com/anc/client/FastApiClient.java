package com.anc.client;

import com.anc.dto.FastApiRequestDTO;
import com.anc.dto.FastApiResponseDTO;
import com.anc.exception.FastApiException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

@Slf4j
@Component
public class FastApiClient {

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    @Value("${fastapi.base-url}")
    private String fastApiBaseUrl;

    @Value("${fastapi.api-key}")
    private String fastApiKey;

    public FastApiClient(RestTemplate restTemplate, ObjectMapper objectMapper) {
        this.restTemplate = restTemplate;
        this.objectMapper = objectMapper;
    }

    /**
     * Calls FastAPI RAG pipeline /assess-structured endpoint.
     * Sends clinical_summary + structured_data.
     * Returns isHighRisk, riskLevel, detectedRisks, explanation, confidence, recommendation.
     */
    public FastApiResponseDTO analyzeRisk(FastApiRequestDTO request) {
        String url = fastApiBaseUrl + "/assess-structured";

        log.info("Calling FastAPI at: {}", url);
        log.debug("FastAPI Request: {}", toJson(request));

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("X-API-KEY", fastApiKey);

        HttpEntity<FastApiRequestDTO> entity = new HttpEntity<>(request, headers);

        try {
            ResponseEntity<FastApiResponseDTO> response = restTemplate.exchange(
                    url,
                    HttpMethod.POST,
                    entity,
                    FastApiResponseDTO.class
            );

            log.info("FastAPI responded with HTTP status: {}", response.getStatusCode());
            return response.getBody();

        } catch (HttpClientErrorException e) {
            log.error("FastAPI client error {}: {}", e.getStatusCode(), e.getResponseBodyAsString());
            throw new FastApiException("FastAPI returned client error: " + e.getStatusCode(), e);

        } catch (HttpServerErrorException e) {
            log.error("FastAPI server error {}: {}", e.getStatusCode(), e.getResponseBodyAsString());
            throw new FastApiException("FastAPI internal server error: " + e.getStatusCode(), e);

        } catch (ResourceAccessException e) {
            log.error("FastAPI unreachable: {}", e.getMessage());
            throw new FastApiException("FastAPI service is unreachable. Please try again later.", e);
        }
    }

    private String toJson(Object obj) {
        try {
            return objectMapper.writeValueAsString(obj);
        } catch (Exception e) {
            return "[SERIALIZATION ERROR]";
        }
    }
}
