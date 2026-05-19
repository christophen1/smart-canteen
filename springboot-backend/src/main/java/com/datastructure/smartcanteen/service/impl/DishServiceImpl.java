package com.datastructure.smartcanteen.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.datastructure.smartcanteen.common.BusinessException;
import com.datastructure.smartcanteen.common.ResultCode;
import com.datastructure.smartcanteen.entity.Category;
import com.datastructure.smartcanteen.entity.Dish;
import com.datastructure.smartcanteen.mapper.CategoryMapper;
import com.datastructure.smartcanteen.mapper.DishMapper;
import com.datastructure.smartcanteen.service.DishService;
import com.datastructure.smartcanteen.vo.DishVO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class DishServiceImpl implements DishService {

    private final DishMapper dishMapper;
    private final CategoryMapper categoryMapper;

    @Override
    public Page<DishVO> page(int page, int size, String keyword) {
        LambdaQueryWrapper<Dish> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Dish::getStatus, 1);
        if (keyword != null && !keyword.isEmpty()) {
            wrapper.like(Dish::getName, keyword);
        }
        wrapper.orderByDesc(Dish::getCreateTime);
        Page<Dish> result = dishMapper.selectPage(new Page<>(page, size), wrapper);
        Page<DishVO> voPage = new Page<>(result.getCurrent(), result.getSize(), result.getTotal());
        voPage.setRecords(result.getRecords().stream().map(this::toVO).toList());
        return voPage;
    }

    @Override
    public Page<DishVO> pageForAdmin(int page, int size, String keyword) {
        LambdaQueryWrapper<Dish> wrapper = new LambdaQueryWrapper<>();
        if (keyword != null && !keyword.isEmpty()) {
            wrapper.like(Dish::getName, keyword);
        }
        wrapper.orderByDesc(Dish::getCreateTime);
        Page<Dish> result = dishMapper.selectPage(new Page<>(page, size), wrapper);
        Page<DishVO> voPage = new Page<>(result.getCurrent(), result.getSize(), result.getTotal());
        voPage.setRecords(result.getRecords().stream().map(this::toVO).toList());
        return voPage;
    }

    @Override
    public DishVO getById(Long id) {
        Dish dish = dishMapper.selectById(id);
        if (dish == null) {
            throw new BusinessException(ResultCode.NOT_FOUND.getCode(), "菜品不存在");
        }
        return toVO(dish);
    }

    @Override
    public void save(Dish dish) {
        dishMapper.insert(dish);
    }

    @Override
    public void update(Dish dish) {
        Dish exist = dishMapper.selectById(dish.getId());
        if (exist == null) {
            throw new BusinessException(ResultCode.NOT_FOUND.getCode(), "菜品不存在");
        }
        dishMapper.updateById(dish);
    }

    @Override
    public void delete(Long id) {
        dishMapper.deleteById(id);
    }

    @Override
    public void updateStatus(Long id, Integer status) {
        Dish dish = dishMapper.selectById(id);
        if (dish == null) {
            throw new BusinessException(ResultCode.NOT_FOUND.getCode(), "菜品不存在");
        }
        dish.setStatus(status);
        dishMapper.updateById(dish);
    }

    private DishVO toVO(Dish dish) {
        DishVO vo = new DishVO();
        vo.setId(dish.getId());
        vo.setCategoryId(dish.getCategoryId());
        vo.setName(dish.getName());
        vo.setPrice(dish.getPrice());
        vo.setImage(dish.getImage());
        vo.setDescription(dish.getDescription());
        vo.setStatus(dish.getStatus());
        vo.setCreateTime(dish.getCreateTime());
        if (dish.getCategoryId() != null) {
            Category category = categoryMapper.selectById(dish.getCategoryId());
            if (category != null) {
                vo.setCategoryName(category.getName());
            }
        }
        return vo;
    }
}
