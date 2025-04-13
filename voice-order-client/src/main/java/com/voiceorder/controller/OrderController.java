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

@Controller
public class OrderController {

    private final OrderClient orderClient;

    @Autowired
    public OrderController(OrderClient orderClient) {
        this.orderClient = orderClient;
    }

    @GetMapping("/")
    public String index(Model model) {
        model.addAttribute("message", "Please upload an audio file");
        return "index";
    }

    @PostMapping("/process")
    public String processAudio(@RequestParam("audio") MultipartFile file, Model model) {
        try {
            byte[] audioData = file.getBytes();
            AudioOrderResponse response = orderClient.processAudioOrder(audioData, "wav");

            model.addAttribute("status", response.getStatus());
            model.addAttribute("message", response.getMessage());
            model.addAttribute("products", response.getProductsList());
            model.addAttribute("errors", response.getProductsErrorList());

        } catch (IOException e) {
            model.addAttribute("error", "Error processing audio file: " + e.getMessage());
        }

        return "result";
    }
} 