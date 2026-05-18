package com.datastructure.smartcanteen.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.datastructure.smartcanteen.entity.User;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface UserMapper extends BaseMapper<User> {
}
