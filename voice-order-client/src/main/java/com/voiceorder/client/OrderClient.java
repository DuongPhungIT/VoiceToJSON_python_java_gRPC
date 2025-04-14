package com.voiceorder.client;

import com.voiceorder.orderservice.VoiceRequest;
import com.voiceorder.orderservice.VoiceResponse;
import com.voiceorder.orderservice.VoiceServiceGrpc;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;
import java.util.HashMap;
import java.util.Map;

@Component
public class OrderClient {
    private static final Logger logger = LoggerFactory.getLogger(OrderClient.class);
    private ManagedChannel channel;
    private VoiceServiceGrpc.VoiceServiceBlockingStub blockingStub;

    @PostConstruct
    public void init() {
        logger.info("Initializing gRPC client...");
        channel = ManagedChannelBuilder.forAddress("localhost", 50051)
                .usePlaintext()
                .build();
        blockingStub = VoiceServiceGrpc.newBlockingStub(channel);
        logger.info("gRPC client initialized and connected to server at localhost:50051");
    }

    public Map<String, Object> processOrder(MultipartFile audioFile) {
        try {
            logger.info("Processing order with audio file: {}", audioFile.getOriginalFilename());
            
            // Get audio bytes directly
            byte[] audioBytes = audioFile.getBytes();
            logger.info("Audio file size: {} bytes", audioBytes.length);

            // Create gRPC request
            VoiceRequest request = VoiceRequest.newBuilder()
                    .setAudioData(com.google.protobuf.ByteString.copyFrom(audioBytes))
                    .build();
            logger.info("Created gRPC request");

            // Call gRPC service
            logger.info("Sending request to server...");
            VoiceResponse response = blockingStub.processVoice(request);
            logger.info("Received response from server: {}", response);

            // Convert response to map
            Map<String, Object> result = new HashMap<>();
            result.put("status", response.getStatus());
            result.put("message", response.getMessage());
            result.put("transcript", response.getTranscript());
            
            // Convert products to map
            result.put("products", response.getProductsList().stream()
                    .map(product -> {
                        Map<String, Object> productMap = new HashMap<>();
                        productMap.put("name", product.getName());
                        productMap.put("sapCode", product.getSapCode());
                        productMap.put("quantity", product.getQuantity());
                        return productMap;
                    })
                    .collect(java.util.stream.Collectors.toList()));
            
            // Convert error products to map
            result.put("productsError", response.getProductsErrorList().stream()
                    .map(productError -> {
                        Map<String, Object> errorMap = new HashMap<>();
                        errorMap.put("name", productError.getName());
                        errorMap.put("quantity", productError.getQuantity());
                        return errorMap;
                    })
                    .collect(java.util.stream.Collectors.toList()));

            logger.info("Processed order successfully: {}", result);
            return result;
        } catch (Exception e) {
            logger.error("Error processing order: {}", e.getMessage(), e);
            Map<String, Object> error = new HashMap<>();
            error.put("status", "error");
            error.put("message", e.getMessage());
            return error;
        }
    }

    @PreDestroy
    public void shutdown() {
        if (channel != null) {
            logger.info("Shutting down gRPC client...");
            channel.shutdown();
            logger.info("gRPC client shutdown completed");
        }
    }
} 