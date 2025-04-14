package com.voiceorder.controller;

import com.voiceorder.client.OrderClient;
import com.voiceorder.orderservice.AudioOrderResponse;
import com.voiceorder.orderservice.Product;
import com.voiceorder.orderservice.ProductError;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

@Controller
public class OrderController {

    @Autowired
    private OrderClient orderClient;

    @GetMapping("/")
    public String index(Model model) {
        model.addAttribute("message", "Click the button below to start recording");
        return "index";
    }

    @PostMapping("/process")
    public String processOrder(@RequestParam("audio") MultipartFile audioFile, Model model) {
        try {
            if (audioFile == null || audioFile.isEmpty()) {
                throw new IllegalArgumentException("No audio file provided");
            }

            AudioOrderResponse response = orderClient.processOrder(audioFile);
            
            Map<String, Object> result = new HashMap<>();
            result.put("status", response.getStatus());
            result.put("message", response.getMessage());
            
            // Convert gRPC products to map
            result.put("products", response.getProductsList().stream()
                    .map(this::convertProductToMap)
                    .collect(Collectors.toList()));
            
            // Convert gRPC error products to map
            result.put("productsError", response.getProductsErrorList().stream()
                    .map(this::convertProductErrorToMap)
                    .collect(Collectors.toList()));
            
            model.addAttribute("result", result);
            return "result";
            
        } catch (Exception e) {
            model.addAttribute("error", "Error processing order: " + e.getMessage());
            return "error";
        }
    }

    private Map<String, Object> convertProductToMap(Product product) {
        Map<String, Object> map = new HashMap<>();
        map.put("name", product.getName());
        map.put("quantity", product.getQuantity());
        map.put("sapCode", product.getSapCode());
        return map;
    }

    private Map<String, Object> convertProductErrorToMap(ProductError productError) {
        Map<String, Object> map = new HashMap<>();
        map.put("name", productError.getName());
        map.put("quantity", productError.getQuantity());
        return map;
    }
} 