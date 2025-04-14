package com.voiceorder.controller;

import com.voiceorder.client.OrderClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;
import java.util.HashMap;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*", allowedHeaders = "*", methods = {RequestMethod.GET, RequestMethod.POST, RequestMethod.OPTIONS})
public class OrderApiController {
    private static final Logger logger = LoggerFactory.getLogger(OrderApiController.class);

    @Autowired
    private OrderClient orderClient;

    @PostMapping("/process")
    public Map<String, Object> processOrder(@RequestParam("audio") MultipartFile audioFile) {
        logger.info("Received audio file: {}", audioFile.getOriginalFilename());
        try {
            if (audioFile == null || audioFile.isEmpty()) {
                logger.error("No audio file provided");
                Map<String, Object> error = new HashMap<>();
                error.put("status", "error");
                error.put("message", "No audio file provided");
                return error;
            }

            Map<String, Object> result = orderClient.processOrder(audioFile);
            logger.info("Processed order successfully: {}", result);
            return result;
        } catch (Exception e) {
            logger.error("Error processing order: {}", e.getMessage(), e);
            Map<String, Object> error = new HashMap<>();
            error.put("status", "error");
            error.put("message", "Error processing order: " + e.getMessage());
            return error;
        }
    }
} 