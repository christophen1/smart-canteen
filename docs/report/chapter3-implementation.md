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
| JDK | 17 | Java 运行环境（SpringBoot + PySpark 共用，MySQL JDBC 驱动 9.x 要求 17+） |
| Maven | 3.8+ | 后端构建管理 |
| SpringBoot | 3.x | 后端框架 |
| MyBatis Plus | 3.5+ | ORM 框架 |
| MySQL | 8.0 | 关系型数据库 |
| Redis | 7.x | 缓存 |
| Node.js | 18+ | 前端构建环境 |
| Vue | 3.x | 前端框架 |
| Element Plus | 2.x | UI 组件库 |
| Echarts | 5.x | 数据可视化图表 |
| Python | 3.8+（推荐 3.10-3.11） | PySpark 运行环境（3.12+ 有兼容风险） |
| PySpark | 3.4+ | 大数据分析引擎 |

### 3.1.3 Spark 安装与配置

1. 安装 JDK 17（MySQL Connector/J 9.x 要求 Java 17+）
2. 安装 Python 3.8+（推荐 3.10/3.11）
3. `pip install -r pyspark-analysis/requirements.txt` 安装依赖
4. MySQL JDBC 驱动已内置在 `pyspark-analysis/lib/mysql-connector-j-9.7.0.jar`，无需额外下载
5. 验证：`python -c "import pyspark; print(pyspark.__version__)"`

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

PySpark 分析模块位于 `pyspark-analysis/`，包含 5 个脚本，通过 `main.py` 统一调度执行。

**模块结构**：

```
pyspark-analysis/
├── config.py              // 数据库连接配置（从环境变量读取）
├── customer_flow.py       // 客流分析
├── peak_hour.py           // 高峰时段分析
├── dish_sales.py          // 菜品销量分析
├── meal_prediction.py     // 备餐预测
├── main.py                // 总入口（调度各分析任务）
└── requirements.txt       // Python 依赖
```

**执行流程**：
1. `SparkSession.builder` 初始化，master 设为 `local[*]` 本地模式
2. 通过 `spark.read.jdbc()` 从 MySQL 读取 orders 和 order_item 表为 DataFrame
3. 依次调用 4 个分析函数，每个函数接收 SparkSession，执行 SparkSQL 或 DataFrame 转换
4. 分析结果通过 `df.write.jdbc()` 写回 MySQL 对应的分析结果表
5. 所有任务完成后关闭 SparkSession

**各分析任务实现要点**：

- **客流分析**：`DATE(create_time)` 提取日期 → `groupBy("analysis_date").agg(count(), sum(), countDistinct())` → 写入 customer_flow_analysis 表
- **高峰时段分析**：`hour(col("create_time"))` 提取小时 → 跨所有日期按小时聚合 → 除以数据覆盖天数得日均值 → 按日均订单量降序写入 peak_hour_analysis 表
- **菜品销量分析**：orders JOIN order_item → 跨所有日期按 dish_id 聚合 → 除以天数得日均销量和日均销售额 → `row_number().over(Window.orderBy(...))` 取全局 TOP10 → 写入 dish_sales_analysis 表
- **备餐预测**：直接从 orders + order_item 原始数据按天聚合 → `lag()` 获取前 7 天销量 → 计算 7 日移动平均 → 取最近一天预测下一天 → 建议备餐量 = 预测值 × 1.2 → 覆盖写入 meal_prediction 表

**依赖**：PySpark 3.x、MySQL JDBC 驱动 (`mysql-connector-j`)，JDBC jar 需放入 Spark 的 jars 目录或通过 `--jars` 参数指定。

### 3.2.4 前端实现

前端基于 **Vue 3 + Vite 6** 构建，入口 `vue-frontend/`，共 19 个源文件，分为用户端和管理端两大部分。

**项目初始化与配置**：

- Vite 6 作为构建工具，开发服务器端口 5173
- `vite.config.js` 配置 proxy：`/api` 前缀请求转发到 `http://localhost:8080`，开发阶段无需 CORS
- 依赖：Vue 3.5、Vue Router 4.5、Element Plus 2.9、Echarts 5.6、Axios 1.7

**Axios 封装（`api/http.js`）**：

- `baseURL: '/api'`，统一请求前缀
- 请求拦截器：自动从 `localStorage.smart_token` 读取 token，添加 `Authorization: Bearer <token>` 头
- 响应拦截器：统一解包 `{ code, message, data }` 格式，code=200 返回 data，非 200 自动 `ElMessage.error` 提示
- 401 状态码：自动清除 token 并 `router.push('/login')` 跳转登录页
- 所有 API 方法集中在 `api` 对象中导出，共 24 个方法覆盖全部后端接口

**路由设计（`router/index.js`）**：

- history 模式（无 `#` 号），15 条路由
- 路由元信息 `meta.auth` 控制认证，`meta.admin` 控制管理员权限
- 全局前置守卫 `beforeEach`：检查 `localStorage.smart_token`，未认证访问受保护路由时跳转登录页

**用户端页面（5 个）**：

| 页面 | 组件 | 核心功能 |
|------|------|----------|
| 登录/注册 | LoginView.vue | tab 切换登录/注册表单，表单校验 |
| 首页 | HomeView.vue | 分类 tabs 切换、关键词搜索、菜品卡片网格、加入购物车 |
| 菜品详情 | DishDetailView.vue | 大图展示、描述、价格、数量选择、加购 |
| 购物车 | CartView.vue | reactive 状态管理 + localStorage 持久化、数量调整、总价计算、提交订单 |
| 我的订单 | OrdersView.vue | 分页列表、状态标签、订单明细展开、取消操作 |

**管理端页面（10 个文件）**：

| 页面 | 组件 | 核心功能 |
|------|------|----------|
| 管理员登录 | AdminLoginView.vue | 独立登录页 |
| 管理布局 | AdminLayout.vue | 侧边导航 + 顶栏 + `<router-view>` 插槽 |
| 工作台 | AdminDashboardView.vue | 用户数/订单数/菜品数/今日销售额 统计卡片 + 快捷入口 |
| 分类管理 | AdminCategoryView.vue | el-table + el-dialog 弹窗 CRUD，排序字段 |
| 菜品管理 | AdminDishView.vue | 表格 + 新增/编辑弹窗 + 上下架 toggle |
| 订单管理 | AdminOrderView.vue | 订单列表 + 状态下拉变更（待支付/已支付/已完成/已取消） |
| 用户管理 | AdminUserView.vue | 用户列表 + 启用/禁用 switch |
| 数据分析 | AdminAnalysisView.vue | **复用组件**，通过 `props.type` 切换 4 种分析类型，Echarts 渲染 + 数据表格 |

**数据可视化（AdminAnalysisView.vue）**：

- 统一组件，根据路由 `props.type` 参数渲染不同分析内容
- 4 种分析类型：`customer-flow`（客流折线图）、`peak-hour`（高峰柱状图）、`dish-sales`（销量 TOP10 柱状图）、`prediction`（备餐预测表格+图）
- 每种类型配置独立的：标题、说明文案、对应 PySpark 脚本名、结果表名、图表类型、表格列定义
- 调用 `/api/analysis/{type}` 获取数据，Echarts 绑定 `chartRef` 渲染

**全局样式（`assets/main.css`）**：

- CSS 自定义属性（颜色、圆角、阴影）
- 顶部导航栏（`.topbar`）、卡片网格、Hero 区域等通用布局样式

### 3.2.5 前后端联调

**开发环境联调方案**：

- 后端 SpringBoot 运行在 `http://localhost:8080`
- 前端 Vite dev server 运行在 `http://localhost:5173`
- Vite proxy 将 `/api` 前缀请求转发至后端，**无需配置 CORS 即可联调**

**认证流程**：

1. 用户在前端登录 → Axios POST `/api/user/login` → 后端验证并返回 JWT token
2. 前端将 token 存入 `localStorage.smart_token`，用户信息存入 `localStorage.smart_user`
3. 后续所有请求由 Axios 拦截器自动附加 `Authorization: Bearer <token>` 头
4. 后端 `JwtInterceptor` 解析 token，将 userId 注入 request attribute
5. 管理员接口额外经过 `AdminInterceptor` 校验 `role == 1`
6. token 过期或无效时后端返回 401 → Axios 响应拦截器自动清除本地 token 并跳转登录页

**数据流验证**：

- 用户下单 → SpringBoot 写入 orders/order_item 表 → PySpark 定时分析 → 结果写入分析结果表 → 前端 `/api/analysis/{type}` 查询 → Echarts 渲染
- 全链路验证方式：启动后端 → 启动前端 → 浏览器访问各页面 → 通过 Postman 或 `scripts/test_api.py` 辅助验证接口

---

## 3.3 演示截图
（本节在系统运行后填充，需至少 3 张核心功能截图。）

### 3.3.1 用户端截图

> 待系统运行后截图

### 3.3.2 管理端截图

> 待系统运行后截图

### 3.3.3 数据可视化截图

> 待系统运行后截图
