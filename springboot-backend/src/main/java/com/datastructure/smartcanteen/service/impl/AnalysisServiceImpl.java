package com.datastructure.smartcanteen.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.datastructure.smartcanteen.entity.CustomerFlowAnalysis;
import com.datastructure.smartcanteen.entity.DishSalesAnalysis;
import com.datastructure.smartcanteen.entity.MealPrediction;
import com.datastructure.smartcanteen.entity.PeakHourAnalysis;
import com.datastructure.smartcanteen.mapper.CustomerFlowAnalysisMapper;
import com.datastructure.smartcanteen.mapper.DishSalesAnalysisMapper;
import com.datastructure.smartcanteen.mapper.MealPredictionMapper;
import com.datastructure.smartcanteen.mapper.PeakHourAnalysisMapper;
import com.datastructure.smartcanteen.service.AnalysisService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;

@Service
@RequiredArgsConstructor
public class AnalysisServiceImpl implements AnalysisService {

    private final CustomerFlowAnalysisMapper customerFlowAnalysisMapper;
    private final PeakHourAnalysisMapper peakHourAnalysisMapper;
    private final DishSalesAnalysisMapper dishSalesAnalysisMapper;
    private final MealPredictionMapper mealPredictionMapper;

    @Override
    public Page<CustomerFlowAnalysis> pageCustomerFlow(int page, int size, LocalDate startDate, LocalDate endDate) {
        LambdaQueryWrapper<CustomerFlowAnalysis> wrapper = new LambdaQueryWrapper<>();
        if (startDate != null) {
            wrapper.ge(CustomerFlowAnalysis::getAnalysisDate, startDate);
        }
        if (endDate != null) {
            wrapper.le(CustomerFlowAnalysis::getAnalysisDate, endDate);
        }
        wrapper.orderByDesc(CustomerFlowAnalysis::getAnalysisDate);
        return customerFlowAnalysisMapper.selectPage(new Page<>(page, size), wrapper);
    }

    @Override
    public Page<PeakHourAnalysis> pagePeakHour(int page, int size, LocalDate startDate, LocalDate endDate) {
        LambdaQueryWrapper<PeakHourAnalysis> wrapper = new LambdaQueryWrapper<>();
        if (startDate != null) {
            wrapper.ge(PeakHourAnalysis::getAnalysisDate, startDate);
        }
        if (endDate != null) {
            wrapper.le(PeakHourAnalysis::getAnalysisDate, endDate);
        }
        wrapper.orderByDesc(PeakHourAnalysis::getAnalysisDate).orderByAsc(PeakHourAnalysis::getHour);
        return peakHourAnalysisMapper.selectPage(new Page<>(page, size), wrapper);
    }

    @Override
    public Page<DishSalesAnalysis> pageDishSales(int page, int size, LocalDate startDate, LocalDate endDate) {
        LambdaQueryWrapper<DishSalesAnalysis> wrapper = new LambdaQueryWrapper<>();
        if (startDate != null) {
            wrapper.ge(DishSalesAnalysis::getAnalysisDate, startDate);
        }
        if (endDate != null) {
            wrapper.le(DishSalesAnalysis::getAnalysisDate, endDate);
        }
        wrapper.orderByDesc(DishSalesAnalysis::getSalesCount);
        return dishSalesAnalysisMapper.selectPage(new Page<>(page, size), wrapper);
    }

    @Override
    public Page<MealPrediction> pagePrediction(int page, int size, LocalDate predictDate) {
        LambdaQueryWrapper<MealPrediction> wrapper = new LambdaQueryWrapper<>();
        if (predictDate != null) {
            wrapper.eq(MealPrediction::getPredictDate, predictDate);
        }
        wrapper.orderByDesc(MealPrediction::getPredictedSales);
        return mealPredictionMapper.selectPage(new Page<>(page, size), wrapper);
    }
}
