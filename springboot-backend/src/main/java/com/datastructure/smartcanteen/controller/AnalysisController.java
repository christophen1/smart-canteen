package com.datastructure.smartcanteen.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.datastructure.smartcanteen.common.Result;
import com.datastructure.smartcanteen.entity.CustomerFlowAnalysis;
import com.datastructure.smartcanteen.entity.DishSalesAnalysis;
import com.datastructure.smartcanteen.entity.MealPrediction;
import com.datastructure.smartcanteen.entity.PeakHourAnalysis;
import com.datastructure.smartcanteen.service.AnalysisService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;

@RestController
@RequestMapping("/api/analysis")
@RequiredArgsConstructor
public class AnalysisController {

    private final AnalysisService analysisService;

    @GetMapping("/customer-flow")
    public Result<Page<CustomerFlowAnalysis>> customerFlow(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        return Result.success(analysisService.pageCustomerFlow(page, size, startDate, endDate));
    }

    @GetMapping("/peak-hour")
    public Result<Page<PeakHourAnalysis>> peakHour(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        return Result.success(analysisService.pagePeakHour(page, size, startDate, endDate));
    }

    @GetMapping("/dish-sales")
    public Result<Page<DishSalesAnalysis>> dishSales(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        return Result.success(analysisService.pageDishSales(page, size, startDate, endDate));
    }

    @GetMapping("/prediction")
    public Result<Page<MealPrediction>> prediction(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate predictDate) {
        return Result.success(analysisService.pagePrediction(page, size, predictDate));
    }
}
