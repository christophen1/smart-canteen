package com.datastructure.smartcanteen.vo;

import com.datastructure.smartcanteen.entity.OrderItem;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Data
public class OrderVO {

    private Long id;
    private String orderNo;
    private Long userId;
    private BigDecimal totalAmount;
    private Integer status;
    private String remark;
    private List<OrderItem> items;
    private LocalDateTime createTime;
}
