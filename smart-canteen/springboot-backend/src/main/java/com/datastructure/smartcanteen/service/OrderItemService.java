package com.datastructure.smartcanteen.service;

import com.datastructure.smartcanteen.entity.OrderItem;

import java.util.List;

public interface OrderItemService {

    List<OrderItem> listByOrderId(Long orderId);
}
