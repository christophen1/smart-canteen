# 校园食堂客流与备餐预测系统 — 产品需求文档 (PRD)

## 1. 项目概述

### 1.1 项目名称

基于 PySpark 的校园食堂客流与备餐预测系统

### 1.2 项目定位

SpringBoot + Vue + PySpark 的完整前后端大数据课程设计项目。

### 1.3 核心目标

通过校园食堂订单数据，实现：

- 在线点餐与后台管理（SpringBoot + Vue）
- 客流统计分析（PySpark 离线分析）
- 热门菜品分析（PySpark 离线分析）
- 高峰时段分析（PySpark 离线分析）
- 备餐预测（PySpark 离线分析，项目亮点）

### 1.4 当前阶段

| 阶段 | 状态 |
|------|------|
| 架构设计 | 已完成 |
| 数据库设计 | 已完成 |
| 后端开发 | 进行中 |
| PySpark 分析 | 待开始 |
| 前端开发 | 待开始 |
| 联调部署 | 待开始 |

---

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────┐     ┌──────────────────┐     ┌─────────┐
│  Vue 前端    │────▶│  SpringBoot 后端  │────▶│  MySQL  │
│  (用户端+管理端)│    │  (RESTful API)   │     │  (主库)  │
└─────────────┘     └────────┬─────────┘     └─────────┘
                             │
                             │ 读数据 / 写结果
                             ▼
                    ┌──────────────────┐
                    │  PySpark 分析模块  │
                    │  (离线定时执行)    │
                    └──────────────────┘
```

- **Vue 前端**：用户点餐 + 管理后台 + 数据可视化（Echarts）
- **SpringBoot 后端**：在线业务 API，连接 MySQL，对接 PySpark 分析结果
- **PySpark 分析模块**：定时从 MySQL 读取订单数据，完成分析后将结果写回 MySQL
- **MySQL**：存储所有业务数据和分析结果

### 2.2 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 后端框架 | SpringBoot | 3.x |
| ORM | MyBatis Plus | 3.5+ |
| 数据库 | MySQL | 8.0 |
| 缓存 | Redis | 7.x |
| 构建工具 | Maven | 3.8+ |
| Java | JDK | 17 |
| 前端框架 | Vue | 3.x |
| UI 组件库 | Element Plus | 2.x |
| HTTP 客户端 | Axios | 1.x |
| 图表库 | Echarts | 5.x |
| 大数据分析 | PySpark | 3.x |
| Python | CPython | 3.10+ |

### 2.3 项目包结构

```
com.datastructure.smartcanteen
├── config          // 配置类（Redis、CORS、MyBatis Plus）
├── controller      // 控制器
│   ├── user        // 用户端接口
│   └── admin       // 管理员端接口
├── service         // 业务接口
│   └── impl        // 业务实现
├── mapper          // MyBatis Plus Mapper
├── entity          // 实体类
├── dto             // 数据传输对象
├── vo              // 视图对象
├── common          // 公共类（统一返回、异常处理、常量）
│   ├── result      // 统一响应封装
│   └── exception   // 全局异常处理
└── utils           // 工具类
```

---

## 3. 功能需求

### 3.1 用户端功能

| 编号 | 功能 | 描述 |
|------|------|------|
| U-01 | 用户注册 | 用户名 + 密码注册，用户名唯一 |
| U-02 | 用户登录 | 登录后返回 token，后续请求携带 token |
| U-03 | 浏览菜品 | 按分类浏览菜品列表，支持搜索菜品名 |
| U-04 | 查看菜品详情 | 查看菜品图片、描述、价格 |
| U-05 | 提交订单 | 选择菜品和数量，生成订单 |
| U-06 | 查看我的订单 | 分页查看历史订单及详情 |

### 3.2 管理员端功能

| 编号 | 功能 | 描述 |
|------|------|------|
| A-01 | 分类管理 | 菜品分类的增删改查 |
| A-02 | 菜品管理 | 菜品增删改查，上下架 |
| A-03 | 订单管理 | 查看所有订单，修改订单状态 |
| A-04 | 用户管理 | 查看用户列表，启用/禁用用户 |
| A-05 | 数据统计 | 查看分析结果（客流/销量/高峰/预测） |

### 3.3 大数据分析功能

| 编号 | 分析类型 | 描述 | 分析粒度 |
|------|----------|------|----------|
| P-01 | 客流分析 | 统计每日订单量、每日销售额、客单价 | 天 |
| P-02 | 高峰时段分析 | 统计各时段(小时)订单量，识别高峰时段 | 小时 |
| P-03 | 热门菜品分析 | 菜品销量 TOP10、销售额 TOP10 | 天/周/月 |
| P-04 | 备餐预测 | 基于历史数据预测未来菜品销量和建议备餐量 | 天 |

---

## 4. 数据库设计

### 4.1 设计规范

- 主键统一 `id BIGINT AUTO_INCREMENT`
- 时间字段：`create_time DATETIME`、`update_time DATETIME`
- 逻辑删除字段：`is_deleted TINYINT DEFAULT 0`
- 金额字段：`DECIMAL(10,2)`
- 状态字段用 `TINYINT` 注释说明含义
- 所有表使用 InnoDB 引擎，utf8mb4 字符集

### 4.2 数据库名称

`smart_canteen`

### 4.3 表结构

#### 4.3.1 user（用户表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| password | VARCHAR(255) | NOT NULL | 密码（BCrypt 加密） |
| real_name | VARCHAR(50) | DEFAULT '' | 真实姓名 |
| phone | VARCHAR(20) | DEFAULT '' | 手机号 |
| role | TINYINT | DEFAULT 0 | 角色：0=普通用户, 1=管理员 |
| status | TINYINT | DEFAULT 1 | 状态：0=禁用, 1=正常 |
| is_deleted | TINYINT | DEFAULT 0 | 逻辑删除 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

#### 4.3.2 category（分类表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| name | VARCHAR(50) | NOT NULL | 分类名称 |
| sort | INT | DEFAULT 0 | 排序值（越小越靠前） |
| is_deleted | TINYINT | DEFAULT 0 | 逻辑删除 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

#### 4.3.3 dish（菜品表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| category_id | BIGINT | NOT NULL | 分类ID |
| name | VARCHAR(100) | NOT NULL | 菜品名称 |
| price | DECIMAL(10,2) | NOT NULL | 价格（元） |
| image | VARCHAR(255) | DEFAULT '' | 图片路径 |
| description | VARCHAR(500) | DEFAULT '' | 菜品描述 |
| status | TINYINT | DEFAULT 1 | 状态：0=下架, 1=上架 |
| is_deleted | TINYINT | DEFAULT 0 | 逻辑删除 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

#### 4.3.4 orders（订单表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| order_no | VARCHAR(32) | UNIQUE, NOT NULL | 订单号（UUID 生成） |
| user_id | BIGINT | NOT NULL | 用户ID |
| total_amount | DECIMAL(10,2) | NOT NULL | 订单总金额 |
| status | TINYINT | DEFAULT 1 | 状态：0=已取消, 1=待支付, 2=已支付, 3=已完成 |
| remark | VARCHAR(255) | DEFAULT '' | 备注 |
| is_deleted | TINYINT | DEFAULT 0 | 逻辑删除 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

#### 4.3.5 order_item（订单明细表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| order_id | BIGINT | NOT NULL | 订单ID |
| dish_id | BIGINT | NOT NULL | 菜品ID |
| dish_name | VARCHAR(100) | NOT NULL | 菜品名（下单时快照） |
| dish_price | DECIMAL(10,2) | NOT NULL | 单价（下单时快照） |
| quantity | INT | NOT NULL | 数量 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### 4.3.6 peak_hour_analysis（高峰时段分析结果表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| analysis_date | DATE | NOT NULL | 分析日期 |
| hour | INT | NOT NULL | 小时（0-23） |
| order_count | INT | DEFAULT 0 | 订单数 |
| total_amount | DECIMAL(10,2) | DEFAULT 0 | 总金额 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### 4.3.7 dish_sales_analysis（菜品销量分析结果表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| analysis_date | DATE | NOT NULL | 分析日期 |
| dish_id | BIGINT | NOT NULL | 菜品ID |
| dish_name | VARCHAR(100) | NOT NULL | 菜品名 |
| sales_count | INT | DEFAULT 0 | 销量 |
| sales_amount | DECIMAL(10,2) | DEFAULT 0 | 销售额 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### 4.3.8 customer_flow_analysis（客流分析结果表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| analysis_date | DATE | NOT NULL | 分析日期 |
| daily_orders | INT | DEFAULT 0 | 日订单量 |
| daily_amount | DECIMAL(10,2) | DEFAULT 0 | 日总销售额 |
| avg_order_amount | DECIMAL(10,2) | DEFAULT 0 | 客单价（人均消费） |
| total_users | INT | DEFAULT 0 | 消费用户数 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### 4.3.9 meal_prediction（备餐预测结果表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| predict_date | DATE | NOT NULL | 预测日期 |
| dish_id | BIGINT | NOT NULL | 菜品ID |
| dish_name | VARCHAR(100) | NOT NULL | 菜品名 |
| predicted_sales | INT | DEFAULT 0 | 预测销量 |
| suggested_prepare | INT | DEFAULT 0 | 建议备餐量（预测销量 × 安全系数） |
| confidence | DECIMAL(5,4) | DEFAULT 0 | 预测置信度 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

---

## 5. API 设计

### 5.1 统一响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

| code | 含义 |
|------|------|
| 200 | 成功 |
| 400 | 参数错误 |
| 401 | 未登录 / token 过期 |
| 403 | 无权限 |
| 500 | 服务器错误 |

### 5.2 用户端接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /api/user/register | 注册 | 否 |
| POST | /api/user/login | 登录 | 否 |
| GET | /api/user/info | 获取个人信息 | 是 |
| PUT | /api/user/info | 修改个人信息 | 是 |
| GET | /api/category/list | 获取分类列表 | 否 |
| GET | /api/dish/page | 菜品分页查询 | 否 |
| GET | /api/dish/{id} | 菜品详情 | 否 |
| POST | /api/order | 提交订单 | 是 |
| GET | /api/order/page | 我的订单分页 | 是 |
| GET | /api/order/{id} | 订单详情 | 是 |
| PUT | /api/order/{id}/cancel | 取消订单 | 是 |

### 5.3 管理员端接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | /api/admin/user/page | 用户分页列表 | 管理员 |
| PUT | /api/admin/user/status | 启用/禁用用户 | 管理员 |
| POST | /api/admin/category | 新增分类 | 管理员 |
| PUT | /api/admin/category | 修改分类 | 管理员 |
| DELETE | /api/admin/category/{id} | 删除分类 | 管理员 |
| POST | /api/admin/dish | 新增菜品 | 管理员 |
| PUT | /api/admin/dish | 修改菜品 | 管理员 |
| DELETE | /api/admin/dish/{id} | 删除菜品 | 管理员 |
| PUT | /api/admin/dish/status | 菜品上下架 | 管理员 |
| GET | /api/admin/order/page | 所有订单分页 | 管理员 |
| PUT | /api/admin/order/{id}/status | 修改订单状态 | 管理员 |

### 5.4 数据分析接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/analysis/peak-hour | 高峰时段分析数据 |
| GET | /api/analysis/dish-sales | 菜品销量排行 |
| GET | /api/analysis/customer-flow | 客流分析数据 |
| GET | /api/analysis/prediction | 备餐预测数据 |

---

## 6. 前端页面设计

### 6.1 用户端页面

| 页面 | 路由 | 说明 |
|------|------|------|
| 登录/注册 | /login | 用户登录注册 |
| 首页 | /home | 菜品分类浏览 |
| 菜品详情 | /dish/{id} | 菜品详细信息 |
| 购物车 | /cart | 已选菜品确认 |
| 我的订单 | /orders | 订单列表和详情 |

### 6.2 管理员端页面

| 页面 | 路由 | 说明 |
|------|------|------|
| 登录 | /admin/login | 管理员登录 |
| 工作台 | /admin/dashboard | 核心数据概览 |
| 分类管理 | /admin/category | 分类增删改查 |
| 菜品管理 | /admin/dish | 菜品增删改查 |
| 订单管理 | /admin/order | 订单查看与状态变更 |
| 用户管理 | /admin/user | 用户列表与启停 |

### 6.3 数据可视化页面

| 页面 | 路由 | 说明 |
|------|------|------|
| 客流分析 | /admin/analysis/flow | 日订单量折线图、客单价趋势 |
| 高峰时段 | /admin/analysis/peak | 分时段柱状图 |
| 菜品销量 | /admin/analysis/dish | 销量/销售额 TOP10 图表 |
| 备餐预测 | /admin/analysis/prediction | 预测销量与建议备餐量表格+图 |

---

## 7. PySpark 分析模块设计

### 7.1 模块结构

```
pyspark-analysis/
├── config.py           // 数据库连接配置
├── customer_flow.py    // 客流分析
├── peak_hour.py        // 高峰时段分析
├── dish_sales.py       // 菜品销量分析
├── meal_prediction.py  // 备餐预测
├── main.py             // 总入口（调度各分析任务）
└── requirements.txt    // Python 依赖
```

### 7.2 分析流程

```
1. SparkSession 初始化
2. 通过 JDBC 读取 MySQL 中的 orders + order_item 数据
3. 执行分析逻辑（SparkSQL / DataFrame API）
4. 将分析结果通过 JDBC 写回 MySQL 对应的分析结果表
5. 关闭 SparkSession
```

### 7.3 各分析逻辑说明

#### 客流分析（customer_flow.py）

- 输入：orders 表
- 逻辑：按 `DATE(create_time)` 分组，统计每日订单量、总金额、去重用户数，计算客单价
- 输出：写入 `customer_flow_analysis` 表

#### 高峰时段分析（peak_hour.py）

- 输入：orders 表
- 逻辑：按 `DATE(create_time) + HOUR(create_time)` 分组，统计每小时的订单量和总金额
- 输出：写入 `peak_hour_analysis` 表

#### 菜品销量分析（dish_sales.py）

- 输入：order_item 表（关联 orders 的 create_time）
- 逻辑：按 `DATE(orders.create_time) + dish_id` 分组，统计销量和销售额，取 TOP10
- 输出：写入 `dish_sales_analysis` 表

#### 备餐预测（meal_prediction.py）

- 输入：`dish_sales_analysis` 表的历史数据
- 逻辑：基于过去 N 天的销量数据，使用移动平均或简单时序模型预测未来销量；建议备餐量 = 预测销量 × 1.2（安全系数）
- 输出：写入 `meal_prediction` 表

### 7.4 执行方式

- 使用 Windows 定时任务或 Linux crontab 定时执行 `main.py`
- 建议每天凌晨执行一次（如 02:00），分析前一天的订单数据

---

## 8. 配置管理规范

### 8.1 敏感信息管控

- 数据库密码、Redis 密码等敏感配置放入 `.env` 文件
- `.env` 文件已加入 `.gitignore`，不提交到仓库
- 提供 `.env.example` 模板文件供其他开发者参考
- SpringBoot 通过 `application.yml` 引用环境变量

### 8.2 .env 示例

```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=smart_canteen
DB_USER=root
DB_PASSWORD=your_password
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
JWT_SECRET=your_jwt_secret
```

---

## 9. 开发计划

### 第一阶段：后端基础搭建

- [ ] 完善 pom.xml，引入 SpringBoot、MyBatis Plus、Redis、JWT 等依赖
- [ ] 配置文件（application.yml、.env.example）
- [ ] 数据库建表 SQL 脚本
- [ ] 基础包结构创建
- [ ] 统一响应封装、全局异常处理
- [ ] JWT 登录认证 + 拦截器

### 第二阶段：业务功能开发

- [ ] 用户模块（注册、登录、个人信息）
- [ ] 分类模块（CRUD）
- [ ] 菜品模块（CRUD + 上下架）
- [ ] 订单模块（下单、查询、取消、状态管理）
- [ ] 管理员用户管理

### 第三阶段：数据分析开发

- [ ] PySpark 环境搭建
- [ ] 客流分析脚本
- [ ] 高峰时段分析脚本
- [ ] 菜品销量分析脚本
- [ ] 备餐预测脚本
- [ ] 分析结果查询 API

### 第四阶段：前端开发

- [ ] Vue 项目初始化
- [ ] 用户端页面
- [ ] 管理端页面
- [ ] 数据可视化页面

### 第五阶段：联调与部署

- [ ] 前后端联调
- [ ] PySpark 定时任务配置
- [ ] 项目打包部署

---

## 10. 附录

### 10.1 数据库名称

`smart_canteen`

### 10.2 Java 包名

`com.datastructure.smartcanteen`

### 10.3 Maven 坐标

```xml
<groupId>com.datastructure</groupId>
<artifactId>smart-canteen</artifactId>
```

### 10.4 Git 仓库结构（目标）

```
smart-canteen/
├── springboot-backend/     // SpringBoot 后端
├── pyspark-analysis/       // PySpark 分析模块
├── vue-frontend/           // Vue 前端
├── docs/                   // 项目文档
│   └── PRD.md
├── .env.example            // 环境变量模板
└── README.md
```
