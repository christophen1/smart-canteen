package com.datastructure.smartcanteen.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.datastructure.smartcanteen.common.Result;
import com.datastructure.smartcanteen.service.DishService;
import com.datastructure.smartcanteen.vo.DishVO;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/dish")
@RequiredArgsConstructor
public class DishController {

    private final DishService dishService;

    @GetMapping("/page")
    public Result<Page<DishVO>> page(@RequestParam(defaultValue = "1") int page,
                                     @RequestParam(defaultValue = "10") int size,
                                     @RequestParam(required = false) String keyword) {
        return Result.success(dishService.page(page, size, keyword));
    }

    @GetMapping("/{id}")
    public Result<DishVO> getById(@PathVariable Long id) {
        return Result.success(dishService.getById(id));
    }
}
