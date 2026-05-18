package com.datastructure.smartcanteen.controller.admin;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.datastructure.smartcanteen.common.Result;
import com.datastructure.smartcanteen.service.UserService;
import com.datastructure.smartcanteen.vo.UserVO;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/admin/user")
@RequiredArgsConstructor
public class AdminUserController {

    private final UserService userService;

    @GetMapping("/page")
    public Result<Page<UserVO>> page(@RequestParam(defaultValue = "1") int page,
                                     @RequestParam(defaultValue = "10") int size,
                                     @RequestParam(required = false) String keyword) {
        return Result.success(userService.page(page, size, keyword));
    }

    @PutMapping("/status")
    public Result<Void> updateStatus(@RequestBody Map<String, Object> body) {
        Long id = Long.valueOf(body.get("id").toString());
        Integer status = (Integer) body.get("status");
        userService.updateStatus(id, status);
        return Result.success();
    }
}
