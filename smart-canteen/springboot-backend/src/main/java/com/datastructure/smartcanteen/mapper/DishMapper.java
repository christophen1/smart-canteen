package com.datastructure.smartcanteen.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.datastructure.smartcanteen.entity.Dish;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface DishMapper extends BaseMapper<Dish> {
}
