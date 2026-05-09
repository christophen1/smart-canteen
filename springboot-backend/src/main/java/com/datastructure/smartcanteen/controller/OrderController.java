package com.datastructure.smartcanteen.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.datastructure.smartcanteen.common.Result;
import com.datastructure.smartcanteen.dto.OrderSubmitDTO;
import com.datastructure.smartcanteen.service.OrderService;
import com.datastructure.smartcanteen.vo.OrderVO;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/order")
@RequiredArgsConstructor
public class OrderController {

    private final OrderService orderService;

    @PostMapping
    public Result<Void> submit(@Valid @RequestBody OrderSubmitDTO dto, HttpServletRequest request) {
        Long userId = (Long) request.getAttribute("userId");
        orderService.submit(userId, dto);
        return Result.success();
    }

    @GetMapping("/page")
    public Result<Page<OrderVO>> page(@RequestParam(defaultValue = "1") int page,
                                      @RequestParam(defaultValue = "10") int size,
                                      HttpServletRequest request) {
        Long userId = (Long) request.getAttribute("userId");
        return Result.success(orderService.pageByUser(userId, page, size));
    }

    @GetMapping("/{id}")
    public Result<OrderVO> getById(@PathVariable Long id) {
        return Result.success(orderService.getById(id));
    }

    @PutMapping("/{id}/cancel")
    public Result<Void> cancel(@PathVariable Long id, HttpServletRequest request) {
        Long userId = (Long) request.getAttribute("userId");
        orderService.cancel(id, userId);
        return Result.success();
    }
}
