package com.datastructure.smartcanteen.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.datastructure.smartcanteen.dto.OrderSubmitDTO;
import com.datastructure.smartcanteen.vo.OrderVO;

public interface OrderService {

    void submit(Long userId, OrderSubmitDTO dto);

    Page<OrderVO> pageByUser(Long userId, int page, int size);

    OrderVO getById(Long id);

    void cancel(Long id, Long userId);

    Page<OrderVO> pageAll(int page, int size);

    void updateStatus(Long id, Integer status);
}
