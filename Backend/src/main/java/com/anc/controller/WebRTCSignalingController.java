package com.anc.controller;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.handler.annotation.DestinationVariable;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Controller;

import java.util.Map;

/**
 * WebRTC Signaling Controller
 * Handles WebSocket messages for video consultation signaling
 */
@Controller
@RequiredArgsConstructor
@Slf4j
public class WebRTCSignalingController {

    private final SimpMessagingTemplate messagingTemplate;

    /**
     * Handle signaling messages for a specific consultation
     * Messages are forwarded to all participants in the consultation room
     */
    @MessageMapping("/consultation/{consultationId}/signal")
    public void handleSignal(
            @DestinationVariable String consultationId,
            @Payload Map<String, Object> signal
    ) {
        log.debug("Received signal for consultation {}: {}", consultationId, signal.get("type"));
        
        // Broadcast signal to all participants in the consultation room
        messagingTemplate.convertAndSend(
                "/topic/consultation/" + consultationId,
                signal
        );
    }

    /**
     * Handle user joining a consultation
     */
    @MessageMapping("/consultation/{consultationId}/join")
    public void handleJoin(
            @DestinationVariable String consultationId,
            @Payload Map<String, Object> joinMessage
    ) {
        String role = (String) joinMessage.get("role");
        log.info("User joined consultation {} as {}", consultationId, role);
        
        // Notify other participants that a user joined
        Map<String, Object> notification = Map.of(
                "type", "user-joined",
                "role", role,
                "consultationId", consultationId
        );
        
        messagingTemplate.convertAndSend(
                "/topic/consultation/" + consultationId,
                notification
        );
    }

    /**
     * Handle user leaving a consultation
     */
    @MessageMapping("/consultation/{consultationId}/leave")
    public void handleLeave(
            @DestinationVariable String consultationId,
            @Payload Map<String, Object> leaveMessage
    ) {
        String role = (String) leaveMessage.get("role");
        log.info("User left consultation {} (role: {})", consultationId, role);
        
        // Notify other participants that a user left
        Map<String, Object> notification = Map.of(
                "type", "user-left",
                "role", role,
                "consultationId", consultationId
        );
        
        messagingTemplate.convertAndSend(
                "/topic/consultation/" + consultationId,
                notification
        );
    }
}
