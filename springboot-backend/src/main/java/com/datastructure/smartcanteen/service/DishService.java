package com.datastructure.smartcanteen.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.datastructure.smartcanteen.entity.Dish;
import com.datastructure.smartcanteen.vo.DishVO;

public interface DishService {

    Page<DishVO> page(int page, int size, String keyword);

    Page<DishVO> pageForAdmin(int page, int size, String keyword);

    DishVO getById(Long id);

    void save(Dish dish);

    void update(Dish dish);

    void delete(Long id);

    void updateStatus(Long id, Integer status);
}
