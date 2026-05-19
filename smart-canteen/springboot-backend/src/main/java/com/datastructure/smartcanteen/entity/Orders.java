package com.datastructure.smartcanteen.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.math.BigDecimal;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("orders")
public class Orders extends BaseEntity {

    private String orderNo;
    private Long userId;
    private BigDecimal totalAmount;
    private Integer status;
    private String remark;
}
