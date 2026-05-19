package com.datastructure.smartcanteen.controller.admin;

import com.datastructure.smartcanteen.common.Result;
import com.datastructure.smartcanteen.entity.Dish;
import com.datastructure.smartcanteen.service.DishService;
import com.datastructure.smartcanteen.vo.DishVO;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/admin/dish")
@RequiredArgsConstructor
public class AdminDishController {

    private final DishService dishService;

    @GetMapping("/page")
    public Result<Page<DishVO>> page(@RequestParam(defaultValue = "1") int page,
                                     @RequestParam(defaultValue = "10") int size,
                                     @RequestParam(required = false) String keyword) {
        return Result.success(dishService.pageForAdmin(page, size, keyword));
    }

    @PostMapping
    public Result<Void> save(@RequestBody Dish dish) {
        dishService.save(dish);
        return Result.success();
    }

    @PutMapping
    public Result<Void> update(@RequestBody Dish dish) {
        dishService.update(dish);
        return Result.success();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        dishService.delete(id);
        return Result.success();
    }

    @PutMapping("/status")
    public Result<Void> updateStatus(@RequestBody Map<String, Object> body) {
        Long id = Long.valueOf(body.get("id").toString());
        Integer status = (Integer) body.get("status");
        dishService.updateStatus(id, status);
        return Result.success();
    }
}
