package com.datastructure.smartcanteen.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.datastructure.smartcanteen.entity.OrderItem;
import com.datastructure.smartcanteen.mapper.OrderItemMapper;
import com.datastructure.smartcanteen.service.OrderItemService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class OrderItemServiceImpl implements OrderItemService {

    private final OrderItemMapper orderItemMapper;

    @Override
    public List<OrderItem> listByOrderId(Long orderId) {
        return orderItemMapper.selectList(
                new LambdaQueryWrapper<OrderItem>().eq(OrderItem::getOrderId, orderId));
    }
}
