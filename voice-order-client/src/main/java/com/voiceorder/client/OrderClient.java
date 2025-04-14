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
import javax.sound.sampled.*;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
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

    private byte[] convertToWav(MultipartFile audioFile) throws IOException {
        logger.info("Converting audio to WAV format using ffmpeg...");
        
        // Create temporary files
        java.io.File tempInputFile = java.io.File.createTempFile("input_", ".webm");
        java.io.File tempOutputFile = java.io.File.createTempFile("output_", ".wav");
        
        try {
            // Save input file
            audioFile.transferTo(tempInputFile);
            logger.info("Saved input audio to: {}", tempInputFile.getAbsolutePath());
            
            // Build ffmpeg command
            ProcessBuilder processBuilder = new ProcessBuilder(
                "ffmpeg",
                "-i", tempInputFile.getAbsolutePath(),
                "-acodec", "pcm_s16le",  // 16-bit PCM
                "-ar", "16000",          // 16kHz sample rate
                "-ac", "1",              // Mono
                "-y",                    // Overwrite output file
                tempOutputFile.getAbsolutePath()
            );
            
            // Start ffmpeg process
            Process process = processBuilder.start();
            int exitCode = process.waitFor();
            
            if (exitCode != 0) {
                String error = new String(process.getErrorStream().readAllBytes());
                logger.error("FFmpeg conversion failed: {}", error);
                throw new IOException("Failed to convert audio to WAV format: " + error);
            }
            
            // Read the converted WAV file
            byte[] wavBytes = java.nio.file.Files.readAllBytes(tempOutputFile.toPath());
            logger.info("Audio converted to WAV format, size: {} bytes", wavBytes.length);
            
            return wavBytes;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IOException("Audio conversion interrupted", e);
        } finally {
            // Clean up temporary files
            if (tempInputFile.exists()) {
                tempInputFile.delete();
            }
            if (tempOutputFile.exists()) {
                tempOutputFile.delete();
            }
            logger.info("Cleaned up temporary files");
        }
    }

    public Map<String, Object> processOrder(MultipartFile audioFile) {
        try {
            logger.info("Processing order with audio file: {}", audioFile.getOriginalFilename());
            
            // Convert audio to WAV format
            byte[] wavBytes = convertToWav(audioFile);
            logger.info("Audio converted to WAV format, size: {} bytes", wavBytes.length);

            // Create gRPC request with WAV data
            VoiceRequest request = VoiceRequest.newBuilder()
                    .setAudioData(com.google.protobuf.ByteString.copyFrom(wavBytes))
                    .build();
            logger.info("Created gRPC request with WAV data");

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