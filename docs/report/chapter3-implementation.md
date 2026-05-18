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

### 3.2.3 分析结果查询 API 实现

PySpark 将分析结果写入 MySQL 后，后端需要提供 REST API 供前端查询展示。B成员为 4 张分析结果表分别建立了完整的 Entity → Mapper → Service → Controller 四层。

**4 个分析结果实体类**：

| 实体类 | 对应表 | 核心字段 |
|--------|--------|----------|
| `CustomerFlowAnalysis` | customer_flow_analysis | analysisDate, dailyOrders, dailyAmount, avgOrderAmount, totalUsers |
| `PeakHourAnalysis` | peak_hour_analysis | analysisDate, hour, orderCount, totalAmount |
| `DishSalesAnalysis` | dish_sales_analysis | analysisDate, dishId, dishName, salesCount, salesAmount |
| `MealPrediction` | meal_prediction | predictDate, dishId, dishName, predictedSales, suggestedPrepare, confidence |

所有实体类使用 `@TableName` 映射表名、`@TableId(type = IdType.AUTO)` 标记自增主键，字段类型使用 `LocalDate` 映射日期、`BigDecimal` 映射金额。

**Mapper 层**：4 个 Mapper 接口均继承 `BaseMapper<T>`，利用 MyBatis Plus 自动生成 CRUD 方法，无需编写任何 SQL。

**Service 层**：`AnalysisService` 接口定义 4 个分页查询方法，`AnalysisServiceImpl` 实现类使用 `LambdaQueryWrapper` 构建类型安全的动态查询条件：
- 客流分析、高峰分析、菜品销量：支持 `startDate` / `endDate` 日期范围过滤
- 备餐预测：支持按 `predictDate` 精确查询
- 所有查询结果按业务需求排序（如客流按日期倒序、菜品销量按销量倒序）

**Controller 层**：`AnalysisController` 注册在 `/api/analysis` 路径下：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/analysis/customer-flow` | GET | 分页查询客流分析，可选日期范围过滤 |
| `/api/analysis/peak-hour` | GET | 分页查询高峰时段分析，可选日期范围过滤 |
| `/api/analysis/dish-sales` | GET | 分页查询菜品销量分析，可选日期范围过滤 |
| `/api/analysis/prediction` | GET | 分页查询备餐预测，可选预测日期过滤 |

所有端点均要求 JWT 认证（通过 JwtInterceptor 拦截），支持 `page`、`size` 分页参数，日期参数使用 `@DateTimeFormat(iso = DateTimeFormat.ISO.DATE)` 自动解析 `yyyy-MM-dd` 格式。

### 3.2.4 PySpark 分析模块实现

**整体流程**：`main.py` 作为总入口，依次初始化 SparkSession、执行 4 个分析任务、关闭 SparkSession。Windows 环境下通过 `os.environ['HADOOP_HOME'] = 'C:\\fake'` 规避 Hadoop 文件系统兼容问题。所有分析脚本均使用中文注释，方便课程报告展示。

**客流分析 (customer_flow.py)**：
1. 通过 JDBC 读取 orders 表为 DataFrame
2. `filter(col("is_deleted") == 0)` 过滤已删除订单
3. `groupBy(date_format("create_time", "yyyy-MM-dd"))` 按日期分组
4. `agg(count("id"), sum("total_amount"), countDistinct("user_id"))` 聚合统计
5. `withColumn("avg_order_amount", col("daily_amount") / col("daily_orders"))` 计算客单价
6. `write.jdbc(mode="overwrite")` 写入 customer_flow_analysis 表

**高峰时段分析 (peak_hour.py)**：
1. 读取 orders 表并过滤已删除订单
2. `groupBy(date_format("create_time"), hour("create_time"))` 按日期+小时双维度分组
3. 聚合订单数和销售额
4. 写入 peak_hour_analysis 表

**菜品销量分析 (dish_sales.py)**：
1. 读取 orders 和 order_item 两张表
2. 使用别名 JOIN（`oi.order_id == o.id`），选择 create_time、dish_id、dish_name、quantity、dish_price
3. 按日期+菜品分组聚合销量和销售额
4. 使用 `Window.partitionBy("analysis_date").orderBy(col("sales_count").desc())` + `row_number()` 取每日 TOP10
5. 写入 dish_sales_analysis 表

**备餐预测 (meal_prediction.py)**：
1. 读取 dish_sales_analysis 历史数据
2. `to_date(col("analysis_date"), "yyyy-MM-dd")` 将字符串转为日期类型
3. 为每个菜品添加 7 个 `lag("sales_count", n)` 滞后列，获取过去 1-7 天销量
4. 计算 7 日移动平均作为 `predicted_sales`
5. `suggested_prepare = predicted_sales * 1.2`（20% 安全冗余）
6. 使用 `when(col("predicted_sales").isNotNull(), ...).otherwise(0)` 处理历史数据不足的边界情况
7. 过滤最新日期数据，预测明天，写入 meal_prediction 表

### 3.2.5 测试脚本优化

`scripts/test_api.py` 新增 `test_analysis_apis()` 函数，对 4 个分析结果查询接口进行覆盖测试：
- 分别使用普通用户 token 和管理员 token 请求所有分析端点
- 验证分页参数 `page` 和 `size` 生效
- 验证未登录访问返回 401 被拦截

同时优化了管理员注册流程：通过 `subprocess` 调用 MySQL 命令行自动设置 `role = 1`，替代原来的手动 SQL 提示，实现全自动测试。

`scripts/generate_data.py` 修复了订单明细数量统计 bug：独立的 `order_item_count` 计数器替代了原来错误的 `order_id - 1` 取值。

### 3.2.6 前端实现

> 前端页面和前后端联调待 Vue 前端开发完成后补充。

---

## 3.3 演示截图
（本节在系统运行后填充，需至少 3 张核心功能截图。）

### 3.3.1 用户端截图

> 待系统运行后截图

### 3.3.2 管理端截图

> 待系统运行后截图

### 3.3.3 数据可视化截图

> 待系统运行后截图
