package com.datastructure.smartcanteen.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@TableName("dish_sales_analysis")
public class DishSalesAnalysis {

    @TableId(type = IdType.AUTO)
    private Long id;

    private LocalDate analysisDate;
    private Long dishId;
    private String dishName;
    private Integer salesCount;
    private BigDecimal salesAmount;
    private LocalDateTime createTime;
}
