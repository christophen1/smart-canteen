package com.datastructure.smartcanteen.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@TableName("customer_flow_analysis")
public class CustomerFlowAnalysis {

    @TableId(type = IdType.AUTO)
    private Long id;

    private LocalDate analysisDate;
    private Integer dailyOrders;
    private BigDecimal dailyAmount;
    private BigDecimal avgOrderAmount;
    private Integer totalUsers;
    private LocalDateTime createTime;
}
