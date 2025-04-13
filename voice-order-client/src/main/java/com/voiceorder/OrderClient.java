package com.voiceorder;

import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import com.voiceorder.orderservice.OrderServiceGrpc;
import com.voiceorder.orderservice.OrderServiceOuterClass.AudioOrderRequest;
import com.voiceorder.orderservice.OrderServiceOuterClass.AudioOrderResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.util.concurrent.TimeUnit;

@Component
public class OrderClient {
    private final ManagedChannel channel;
    private final OrderServiceGrpc.OrderServiceBlockingStub blockingStub;

    public OrderClient(@Value("${grpc.server.host:localhost}") String host,
                      @Value("${grpc.server.port:50051}") int port) {
        this.channel = ManagedChannelBuilder.forAddress(host, port)
                .usePlaintext()
                .build();
        this.blockingStub = OrderServiceGrpc.newBlockingStub(channel);
    }

    public AudioOrderResponse processAudioOrder(byte[] audioData, String audioFormat) {
        AudioOrderRequest request = AudioOrderRequest.newBuilder()
                .setAudioData(com.google.protobuf.ByteString.copyFrom(audioData))
                .setAudioFormat(audioFormat)
                .build();

        return blockingStub.processAudioOrder(request);
    }

    public void shutdown() throws InterruptedException {
        channel.shutdown().awaitTermination(5, TimeUnit.SECONDS);
    }
} 