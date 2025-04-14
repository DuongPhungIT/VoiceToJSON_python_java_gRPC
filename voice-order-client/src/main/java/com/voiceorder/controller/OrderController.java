package com.voiceorder.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Controller
public class OrderController {
    private static final Logger logger = LoggerFactory.getLogger(OrderController.class);

    @GetMapping("/")
    public String index(Model model) {
        model.addAttribute("message", "Click the button below to start recording");
        return "index";
    }

    @GetMapping("/result")
    public String showResult(Model model) {
        return "result";
    }

    @GetMapping("/error")
    public String showError(Model model) {
        return "error";
    }
} 