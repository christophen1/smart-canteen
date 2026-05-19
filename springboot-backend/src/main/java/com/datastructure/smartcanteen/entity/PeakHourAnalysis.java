package com.datastructure.smartcanteen.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@TableName("peak_hour_analysis")
public class PeakHourAnalysis {

    @TableId(type = IdType.AUTO)
    private Long id;

    private LocalDate analysisDate;
    private Integer hour;
    private Integer orderCount;
    private BigDecimal totalAmount;
    private LocalDateTime createTime;
}
