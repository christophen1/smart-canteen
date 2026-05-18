# 第3章 项目实现

## 3.1 实现环境
### 3.1.1 硬件环境

| 项目 | 配置 |
|------|------|
| CPU | Intel Core i5 / AMD Ryzen 5 及以上 |
| 内存 | 16 GB |
| 硬盘 | 256 GB SSD |
| 操作系统 | Windows 11 / Linux |

### 3.1.2 软件环境

| 软件 | 版本 | 用途 |
|------|------|------|
| JDK | 17 | Java 运行环境 |
| Maven | 3.8+ | 后端构建管理 |
| SpringBoot | 3.x | 后端框架 |
| MyBatis Plus | 3.5+ | ORM 框架 |
| MySQL | 8.0 | 关系型数据库 |
| Redis | 7.x | 缓存 |
| Node.js | 18+ | 前端构建环境 |
| Vue | 3.x | 前端框架 |
| Element Plus | 2.x | UI 组件库 |
| Echarts | 5.x | 数据可视化图表 |
| Python | 3.10+ | PySpark 运行环境 |
| PySpark | 3.x | 大数据分析引擎 |
| Java (Spark) | JDK 8/11 | Spark 运行时（需与 PySpark 匹配） |

### 3.1.3 Spark 安装与配置

1. 安装 Python 3.10+
2. `pip install pyspark` 安装 PySpark
3. 下载 MySQL JDBC 驱动 `mysql-connector-j-8.x.x.jar`
4. 将 JDBC jar 放入 Spark 的 jars 目录或使用 `--jars` 参数指定
5. 验证：`pyspark --version`

### 3.1.4 开发工具

| 工具 | 用途 |
|------|------|
| IntelliJ IDEA | 后端 Java 开发 |
| VS Code | 前端 Vue 开发 + PySpark 开发 |
| Navicat / DBeaver | 数据库管理 |
| Postman | API 测试 |

---

## 3.2 主要实现过程

### 3.2.1 后端基础框架搭建

**项目结构**：采用 Maven 多模块聚合项目，根 POM 定义 Spring Boot 3.2.0 父依赖和公共版本属性，`springboot-backend` 子模块包含所有业务代码。

**依赖选型**：

| 依赖 | 版本 | 用途 |
|------|------|------|
| spring-boot-starter-web | 3.2.0 | REST API |
| mybatis-plus-spring-boot3-starter | 3.5.5 | ORM + 分页 |
| mysql-connector-j | - | MySQL 驱动 |
| jjwt (api/impl/jackson) | 0.12.3 | JWT 令牌 |
| spring-security-crypto | - | BCrypt 密码加密 |
| spring-boot-starter-validation | - | 参数校验 |
| lombok | - | 减少样板代码 |

**统一响应封装**：`Result<T>` 泛型类，包含 `code`、`message`、`data` 三个字段，提供 `success()` / `error()` 静态工厂方法。`ResultCode` 枚举定义 6 种标准状态码（200/400/401/403/404/500）。

**全局异常处理**：`@RestControllerAdvice` + `@ExceptionHandler`，`BusinessException` 返回业务状态码，未捕获异常统一返回 500。

**JWT 认证**：`JwtUtils` 基于 jjwt 0.12.x API，使用 HMAC-SHA 算法签发和验证 token，有效期 2 小时。`JwtInterceptor` 从 `Authorization: Bearer <token>` 头提取 token，验证通过后将 `userId` 存入 request attribute，白名单放行登录/注册/菜品浏览等公开接口。

**管理员鉴权**：`AdminInterceptor` 独立拦截 `/api/admin/**` 路径，查询数据库验证 `role == 1`，与 JWT 拦截器职责分离。

**CORS**：`CorsFilter` 允许所有来源和方法，支持凭证携带，满足前后端分离开发需求。

**MyBatis Plus 配置**：
- 分页插件 `PaginationInnerInterceptor`
- 自动填充：`MetaObjectHandler` 自动设置 `createTime` / `updateTime`
- 逻辑删除：`@TableLogic` 注解，删除操作自动转为 `is_deleted = 1`
- `@MapperScan("com.datastructure.smartcanteen.mapper")` 自动注册 Mapper

**关键代码示例 — JWT 拦截器**：

```java
@Component
@RequiredArgsConstructor
public class JwtInterceptor implements HandlerInterceptor {
    private final JwtUtils jwtUtils;

    @Override
    public boolean preHandle(HttpServletRequest request, 
                            HttpServletResponse response, Object handler) {
        String token = request.getHeader("Authorization");
        if (token != null && token.startsWith("Bearer ")) {
            token = token.substring(7);
        }
        if (token == null || token.isEmpty()) {
            response.getWriter().write("{\"code\":401,\"message\":\"未登录\"}");
            return false;
        }
        Long userId = jwtUtils.getUserId(token);
        request.setAttribute("userId", userId);
        return true;
    }
}
```

**配置管理**：敏感信息（数据库密码、JWT Secret）通过 `${ENV_VAR:default}` 占位符引用环境变量，提供 `.env.example` 模板，`.env` 已加入 `.gitignore`。

### 3.2.2 业务模块实现

**用户模块**：
- 注册：校验用户名唯一性，BCrypt 加密存储密码
- 登录：验密后签发 JWT token，返回 `LoginVO(token + UserVO)`
- 个人信息：查询/修改（不含密码字段的 UserVO）

**分类模块**：标准 CRUD，管理员操作；用户端 `GET /list` 公开访问

**菜品模块**：
- 用户端：分页查询（仅上架菜品）、关键词搜索、关联分类名查询
- 管理员端：CRUD + 上下架状态切换
- 菜品详情 VO 包含分类名（JOIN category 表）

**订单模块**：
- 下单：生成时间戳+UUID 订单号，查 Dish 表取实时价格，快照 dishName/dishPrice 写入 OrderItem，事务保证一致性
- 查询：我的订单（按用户ID）、全部订单（管理员），每条含订单明细列表
- 取消：校验归属权 + 仅待支付状态可取消
- 管理员改状态：支持 已取消/待支付/已支付/已完成 四个状态流转

### 3.2.3 PySpark 分析模块实现

- 客流分析脚本实现
- 高峰时段分析脚本实现
- 菜品销量分析脚本实现
- 备餐预测脚本实现

### 3.2.4 前端实现

- 用户端页面
- 管理端页面
- 数据可视化页面

### 3.2.5 前后端联调

- API 对接测试
- 数据流验证

---

## 3.3 演示截图
（本节在系统运行后填充，需至少 3 张核心功能截图。）

### 3.3.1 用户端截图

> 待系统运行后截图

### 3.3.2 管理端截图

> 待系统运行后截图

### 3.3.3 数据可视化截图

> 待系统运行后截图
