package com.datastructure.smartcanteen.controller;

import com.datastructure.smartcanteen.common.Result;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/analysis")
@RequiredArgsConstructor
public class AnalysisController {

    private final JdbcTemplate jdbcTemplate;

    @GetMapping("/customer-flow")
    public Result<List<Map<String, Object>>> customerFlow() {
        String sql = """
                SELECT
                    DATE_FORMAT(analysis_date, '%Y-%m-%d') AS analysisDate,
                    daily_orders AS dailyOrders,
                    daily_amount AS dailyAmount,
                    avg_order_amount AS avgOrderAmount,
                    total_users AS totalUsers
                FROM customer_flow_analysis
                ORDER BY analysis_date DESC
                LIMIT 30
                """;
        List<Map<String, Object>> rows = jdbcTemplate.queryForList(sql);
        Collections.reverse(rows);
        return Result.success(rows);
    }

    @GetMapping("/peak-hour")
    public Result<List<Map<String, Object>>> peakHour() {
        String sql = """
                SELECT
                    DATE_FORMAT(analysis_date, '%Y-%m-%d') AS analysisDate,
                    CONCAT(LPAD(hour, 2, '0'), ':00') AS hour,
                    order_count AS orderCount,
                    total_amount AS totalAmount
                FROM peak_hour_analysis
                WHERE analysis_date = (SELECT MAX(analysis_date) FROM peak_hour_analysis)
                ORDER BY hour
                """;
        return Result.success(jdbcTemplate.queryForList(sql));
    }

    @GetMapping("/dish-sales")
    public Result<List<Map<String, Object>>> dishSales() {
        String sql = """
                SELECT
                    DATE_FORMAT(analysis_date, '%Y-%m-%d') AS analysisDate,
                    dish_id AS dishId,
                    dish_name AS dishName,
                    sales_count AS salesCount,
                    sales_amount AS salesAmount
                FROM dish_sales_analysis
                WHERE analysis_date = (SELECT MAX(analysis_date) FROM dish_sales_analysis)
                ORDER BY sales_count DESC
                LIMIT 10
                """;
        return Result.success(jdbcTemplate.queryForList(sql));
    }

    @GetMapping("/prediction")
    public Result<List<Map<String, Object>>> prediction() {
        String sql = """
                SELECT
                    DATE_FORMAT(predict_date, '%Y-%m-%d') AS predictDate,
                    dish_id AS dishId,
                    dish_name AS dishName,
                    predicted_sales AS predictedSales,
                    suggested_prepare AS suggestedPrepare,
                    confidence
                FROM meal_prediction
                WHERE predict_date = (SELECT MAX(predict_date) FROM meal_prediction)
                ORDER BY suggested_prepare DESC
                LIMIT 10
                """;
        return Result.success(jdbcTemplate.queryForList(sql));
    }

    @GetMapping("/summary")
    public Result<Map<String, Object>> summary() {
        Map<String, Object> summary = new HashMap<>();

        List<Map<String, Object>> orderRows = jdbcTemplate.queryForList("""
                SELECT
                    COUNT(*) AS orderCount,
                    COALESCE(SUM(total_amount), 0) AS salesAmount
                FROM orders
                WHERE DATE(create_time) = (SELECT DATE(MAX(create_time)) FROM orders)
                """);
        Map<String, Object> orderSummary = firstOrEmpty(orderRows);
        summary.put("orderCount", orderSummary.getOrDefault("orderCount", 0));
        summary.put("salesAmount", orderSummary.getOrDefault("salesAmount", 0));

        List<Map<String, Object>> peakRows = jdbcTemplate.queryForList("""
                SELECT CONCAT(LPAD(hour, 2, '0'), ':00') AS peakHour
                FROM peak_hour_analysis
                WHERE analysis_date = (SELECT MAX(analysis_date) FROM peak_hour_analysis)
                ORDER BY order_count DESC
                LIMIT 1
                """);
        summary.put("peakHour", firstOrEmpty(peakRows).getOrDefault("peakHour", "--"));

        summary.put("taskCount", 4);
        summary.put("predictions", prediction().getData());
        return Result.success(summary);
    }

    private Map<String, Object> firstOrEmpty(List<Map<String, Object>> rows) {
        return rows.isEmpty() ? Map.of() : rows.get(0);
    }
}
