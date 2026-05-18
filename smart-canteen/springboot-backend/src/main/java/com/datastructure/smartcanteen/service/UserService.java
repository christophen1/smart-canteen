package com.datastructure.smartcanteen.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.datastructure.smartcanteen.dto.LoginDTO;
import com.datastructure.smartcanteen.dto.RegisterDTO;
import com.datastructure.smartcanteen.entity.User;
import com.datastructure.smartcanteen.vo.LoginVO;
import com.datastructure.smartcanteen.vo.UserVO;

public interface UserService {

    LoginVO login(LoginDTO dto);

    void register(RegisterDTO dto);

    UserVO getById(Long id);

    void updateInfo(Long id, User user);

    Page<UserVO> page(int page, int size, String keyword);

    void updateStatus(Long id, Integer status);
}
