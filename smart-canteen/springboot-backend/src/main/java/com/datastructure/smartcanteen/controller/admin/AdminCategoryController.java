package com.datastructure.smartcanteen.controller.admin;

import com.datastructure.smartcanteen.common.Result;
import com.datastructure.smartcanteen.entity.Category;
import com.datastructure.smartcanteen.service.CategoryService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/admin/category")
@RequiredArgsConstructor
public class AdminCategoryController {

    private final CategoryService categoryService;

    @PostMapping
    public Result<Void> save(@RequestBody Category category) {
        categoryService.save(category);
        return Result.success();
    }

    @PutMapping
    public Result<Void> update(@RequestBody Category category) {
        categoryService.update(category);
        return Result.success();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        categoryService.delete(id);
        return Result.success();
    }
}
