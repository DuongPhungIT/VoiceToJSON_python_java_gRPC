package com.voiceorder.controller;

import com.voiceorder.OrderClient;
import com.voiceorder.orderservice.OrderServiceOuterClass.AudioOrderResponse;
import com.voiceorder.orderservice.OrderServiceOuterClass.Product;
import com.voiceorder.orderservice.OrderServiceOuterClass.ProductError;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Base64;

@Controller
public class OrderController {

    private final OrderClient orderClient;

    @Autowired
    public OrderController(OrderClient orderClient) {
        this.orderClient = orderClient;
    }

    @GetMapping("/")
    public String index(Model model) {
        model.addAttribute("message", "Click the button below to start recording");
        return "record";
    }

    @PostMapping("/process")
    public String processAudio(@RequestParam("audio") String base64Audio, Model model) {
        try {
            // Decode base64 audio data
            byte[] audioData = Base64.getDecoder().decode(base64Audio);
            
            // Process with webm format
            AudioOrderResponse response = orderClient.processAudioOrder(audioData, "webm");

            model.addAttribute("status", response.getStatus());
            model.addAttribute("message", response.getMessage());
            model.addAttribute("products", response.getProductsList());
            model.addAttribute("errors", response.getProductsErrorList());

        } catch (Exception e) {
            model.addAttribute("status", "ERROR");
            model.addAttribute("message", "Error processing audio: " + e.getMessage());
            model.addAttribute("products", null);
            model.addAttribute("errors", null);
        }

        return "result";
    }
} 