package com.datastructure.smartcanteen.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.datastructure.smartcanteen.entity.CustomerFlowAnalysis;
import com.datastructure.smartcanteen.entity.DishSalesAnalysis;
import com.datastructure.smartcanteen.entity.MealPrediction;
import com.datastructure.smartcanteen.entity.PeakHourAnalysis;

import java.time.LocalDate;

public interface AnalysisService {

    Page<CustomerFlowAnalysis> pageCustomerFlow(int page, int size, LocalDate startDate, LocalDate endDate);

    Page<PeakHourAnalysis> pagePeakHour(int page, int size, LocalDate startDate, LocalDate endDate);

    Page<DishSalesAnalysis> pageDishSales(int page, int size, LocalDate startDate, LocalDate endDate);

    Page<MealPrediction> pagePrediction(int page, int size, LocalDate predictDate);
}
