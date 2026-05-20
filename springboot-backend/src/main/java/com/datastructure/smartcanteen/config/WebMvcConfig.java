package com.datastructure.smartcanteen.config;

import com.datastructure.smartcanteen.interceptor.AdminInterceptor;
import com.datastructure.smartcanteen.interceptor.JwtInterceptor;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
@RequiredArgsConstructor
public class WebMvcConfig implements WebMvcConfigurer {

    private final JwtInterceptor jwtInterceptor;
    private final AdminInterceptor adminInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        // JWT 认证拦截器 — 除白名单外全部拦截
        registry.addInterceptor(jwtInterceptor)
                .addPathPatterns("/**")
                .excludePathPatterns(
                        "/api/user/login",
                        "/api/user/register",
                        "/api/category/list",
                        "/api/dish/page",
                        "/api/dish/*"
                );

        // 管理员鉴权拦截器 — 仅拦截 /api/admin/**
        registry.addInterceptor(adminInterceptor)
                .addPathPatterns(
                        "/api/admin/**",
                        "/api/analysis/**");
    }
}
