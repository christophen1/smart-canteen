package com.datastructure.smartcanteen.controller;

import com.datastructure.smartcanteen.common.Result;
import com.datastructure.smartcanteen.dto.LoginDTO;
import com.datastructure.smartcanteen.dto.RegisterDTO;
import com.datastructure.smartcanteen.entity.User;
import com.datastructure.smartcanteen.service.UserService;
import com.datastructure.smartcanteen.vo.LoginVO;
import com.datastructure.smartcanteen.vo.UserVO;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/user")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @PostMapping("/register")
    public Result<Void> register(@Valid @RequestBody RegisterDTO dto) {
        userService.register(dto);
        return Result.success();
    }

    @PostMapping("/login")
    public Result<LoginVO> login(@Valid @RequestBody LoginDTO dto) {
        return Result.success(userService.login(dto));
    }

    @GetMapping("/info")
    public Result<UserVO> info(HttpServletRequest request) {
        Long userId = (Long) request.getAttribute("userId");
        return Result.success(userService.getById(userId));
    }

    @PutMapping("/info")
    public Result<Void> updateInfo(@RequestBody User user, HttpServletRequest request) {
        Long userId = (Long) request.getAttribute("userId");
        userService.updateInfo(userId, user);
        return Result.success();
    }
}
