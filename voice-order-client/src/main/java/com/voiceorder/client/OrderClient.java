package com.voiceorder.client;

import com.voiceorder.orderservice.AudioOrderRequest;
import com.voiceorder.orderservice.AudioOrderResponse;
import com.voiceorder.orderservice.OrderServiceGrpc;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;
import java.io.IOException;

@Component
public class OrderClient {
    private ManagedChannel channel;
    private OrderServiceGrpc.OrderServiceBlockingStub blockingStub;

    @PostConstruct
    public void init() {
        channel = ManagedChannelBuilder.forAddress("localhost", 5002)
                .usePlaintext()
                .build();
        blockingStub = OrderServiceGrpc.newBlockingStub(channel);
    }

    public AudioOrderResponse processOrder(MultipartFile audioFile) throws IOException {
        AudioOrderRequest request = AudioOrderRequest.newBuilder()
                .setAudioData(com.google.protobuf.ByteString.copyFrom(audioFile.getBytes()))
                .setAudioFormat("webm")
                .build();

        return blockingStub.processAudioOrder(request);
    }

    @PreDestroy
    public void shutdown() {
        if (channel != null) {
            channel.shutdown();
        }
    }
} 