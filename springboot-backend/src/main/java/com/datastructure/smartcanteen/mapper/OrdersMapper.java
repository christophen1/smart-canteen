package com.datastructure.smartcanteen.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.datastructure.smartcanteen.entity.Orders;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface OrdersMapper extends BaseMapper<Orders> {
}
