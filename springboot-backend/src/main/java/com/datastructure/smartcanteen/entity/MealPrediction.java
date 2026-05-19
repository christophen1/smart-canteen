package com.datastructure.smartcanteen.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@TableName("meal_prediction")
public class MealPrediction {

    @TableId(type = IdType.AUTO)
    private Long id;

    private LocalDate predictDate;
    private Long dishId;
    private String dishName;
    private Integer predictedSales;
    private Integer suggestedPrepare;
    private BigDecimal confidence;
    private LocalDateTime createTime;
}
