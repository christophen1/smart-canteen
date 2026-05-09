package com.datastructure.smartcanteen.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.datastructure.smartcanteen.common.BusinessException;
import com.datastructure.smartcanteen.common.ResultCode;
import com.datastructure.smartcanteen.dto.OrderItemDTO;
import com.datastructure.smartcanteen.dto.OrderSubmitDTO;
import com.datastructure.smartcanteen.entity.Dish;
import com.datastructure.smartcanteen.entity.OrderItem;
import com.datastructure.smartcanteen.entity.Orders;
import com.datastructure.smartcanteen.mapper.DishMapper;
import com.datastructure.smartcanteen.mapper.OrderItemMapper;
import com.datastructure.smartcanteen.mapper.OrdersMapper;
import com.datastructure.smartcanteen.service.OrderService;
import com.datastructure.smartcanteen.vo.OrderVO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class OrderServiceImpl implements OrderService {

    private final OrdersMapper ordersMapper;
    private final OrderItemMapper orderItemMapper;
    private final DishMapper dishMapper;

    @Override
    @Transactional
    public void submit(Long userId, OrderSubmitDTO dto) {
        Orders order = new Orders();
        order.setOrderNo(System.currentTimeMillis() + UUID.randomUUID().toString().substring(0, 8));
        order.setUserId(userId);
        order.setStatus(1);
        order.setRemark(dto.getRemark() != null ? dto.getRemark() : "");

        BigDecimal total = BigDecimal.ZERO;
        for (OrderItemDTO itemDTO : dto.getItems()) {
            Dish dish = dishMapper.selectById(itemDTO.getDishId());
            if (dish == null || dish.getStatus() == 0) {
                throw new BusinessException(ResultCode.BAD_REQUEST.getCode(),
                        "菜品不存在或已下架: " + itemDTO.getDishId());
            }
            total = total.add(dish.getPrice().multiply(BigDecimal.valueOf(itemDTO.getQuantity())));
        }
        order.setTotalAmount(total);
        ordersMapper.insert(order);

        for (OrderItemDTO itemDTO : dto.getItems()) {
            Dish dish = dishMapper.selectById(itemDTO.getDishId());
            OrderItem item = new OrderItem();
            item.setOrderId(order.getId());
            item.setDishId(dish.getId());
            item.setDishName(dish.getName());
            item.setDishPrice(dish.getPrice());
            item.setQuantity(itemDTO.getQuantity());
            orderItemMapper.insert(item);
        }
    }

    @Override
    public Page<OrderVO> pageByUser(Long userId, int page, int size) {
        LambdaQueryWrapper<Orders> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Orders::getUserId, userId).orderByDesc(Orders::getCreateTime);
        Page<Orders> result = ordersMapper.selectPage(new Page<>(page, size), wrapper);
        return convertPage(result);
    }

    @Override
    public OrderVO getById(Long id) {
        Orders order = ordersMapper.selectById(id);
        if (order == null) {
            throw new BusinessException(ResultCode.NOT_FOUND.getCode(), "订单不存在");
        }
        return toVO(order);
    }

    @Override
    public void cancel(Long id, Long userId) {
        Orders order = ordersMapper.selectById(id);
        if (order == null) {
            throw new BusinessException(ResultCode.NOT_FOUND.getCode(), "订单不存在");
        }
        if (!order.getUserId().equals(userId)) {
            throw new BusinessException(ResultCode.FORBIDDEN.getCode(), "无权取消他人订单");
        }
        if (order.getStatus() != 1) {
            throw new BusinessException(ResultCode.BAD_REQUEST.getCode(), "仅待支付订单可取消");
        }
        order.setStatus(0);
        ordersMapper.updateById(order);
    }

    @Override
    public Page<OrderVO> pageAll(int page, int size) {
        LambdaQueryWrapper<Orders> wrapper = new LambdaQueryWrapper<>();
        wrapper.orderByDesc(Orders::getCreateTime);
        Page<Orders> result = ordersMapper.selectPage(new Page<>(page, size), wrapper);
        return convertPage(result);
    }

    @Override
    public void updateStatus(Long id, Integer status) {
        Orders order = ordersMapper.selectById(id);
        if (order == null) {
            throw new BusinessException(ResultCode.NOT_FOUND.getCode(), "订单不存在");
        }
        order.setStatus(status);
        ordersMapper.updateById(order);
    }

    private OrderVO toVO(Orders order) {
        OrderVO vo = new OrderVO();
        vo.setId(order.getId());
        vo.setOrderNo(order.getOrderNo());
        vo.setUserId(order.getUserId());
        vo.setTotalAmount(order.getTotalAmount());
        vo.setStatus(order.getStatus());
        vo.setRemark(order.getRemark());
        vo.setCreateTime(order.getCreateTime());
        List<OrderItem> items = orderItemMapper.selectList(
                new LambdaQueryWrapper<OrderItem>().eq(OrderItem::getOrderId, order.getId()));
        vo.setItems(items);
        return vo;
    }

    private Page<OrderVO> convertPage(Page<Orders> result) {
        Page<OrderVO> voPage = new Page<>(result.getCurrent(), result.getSize(), result.getTotal());
        voPage.setRecords(result.getRecords().stream().map(this::toVO).toList());
        return voPage;
    }
}
