package com.datastructure.smartcanteen.dto;

import jakarta.validation.constraints.NotEmpty;
import lombok.Data;

import java.util.List;

@Data
public class OrderSubmitDTO {

    @NotEmpty(message = "订单项不能为空")
    private List<OrderItemDTO> items;

    private String remark;
}
