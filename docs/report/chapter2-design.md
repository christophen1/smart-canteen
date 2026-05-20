# 第2章 项目设计

## 2.1 概要设计
### 2.1.1 系统架构

```
┌──────────────────────────────────────────────────────────────┐
│                        用户层                                  │
│  ┌────────────────────┐    ┌────────────────────┐             │
│  │   Vue 3 前端        │    │   Vue 3 管理后台     │             │
│  │   (Element Plus)   │    │   (Element Plus)   │             │
│  │   用户点餐 / 查订单  │    │   数据管理 / 看板    │             │
│  └────────┬───────────┘    └────────┬───────────┘             │
└───────────┼─────────────────────────┼─────────────────────────┘
            │ HTTP (Axios)            │ HTTP (Axios)
            │ JWT Token               │ JWT Token
┌───────────┼─────────────────────────┼─────────────────────────┐
│           ▼                         ▼                          │
│                     业务服务层                                   │
│  ┌──────────────────────────────────────────────────────┐     │
│  │              SpringBoot 3.x REST API                  │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │     │
│  │  │ 用户模块  │  │ 菜品模块  │  │ 订单模块          │   │     │
│  │  │ /api/user │  │ /api/dish│  │ /api/order       │   │     │
│  │  └──────────┘  └──────────┘  └──────────────────┘   │     │
│  │  ┌──────────┐  ┌──────────────────────────────────┐ │     │
│  │  │ 分类模块  │  │ 分析查询模块                      │ │     │
│  │  │/api/ctgry│  │ /api/analysis (查分析结果表)       │ │     │
│  │  └──────────┘  └──────────────────────────────────┘ │     │
│  │  ┌──────────────────────────────────────────────┐   │     │
│  │  │  MyBatis Plus ORM  /  Redis 缓存             │   │     │
│  │  └──────────────────────────────────────────────┘   │     │
│  └──────────────────────┬───────────────────────────────┘     │
└──────────────────────────┼─────────────────────────────────────┘
                           │ JDBC
┌──────────────────────────┼─────────────────────────────────────┐
│                          ▼                                      │
│                     数据存储层                                    │
│  ┌──────────────────────────────────────────────────────┐     │
│  │                    MySQL 8.0                           │     │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────┐  │     │
│  │  │  user   │ │  dish   │ │ orders  │ │order_item │  │     │
│  │  └─────────┘ └─────────┘ └─────────┘ └───────────┘  │     │
│  │  ┌─────────┐ ┌──────────────────────────────────┐   │     │
│  │  │category │ │  分析结果表 (PySpark 写入)         │   │     │
│  │  └─────────┘ │  peak_hour / dish_sales /         │   │     │
│  │               │  customer_flow / meal_prediction  │   │     │
│  │               └──────────────────────────────────┘   │     │
│  └──────────────────────┬───────────────────────────────┘     │
└──────────────────────────┼─────────────────────────────────────┘
                           │ JDBC (读 + 写)
┌──────────────────────────┼─────────────────────────────────────┐
│                          ▼                                      │
│                   大数据分析层 (离线)                              │
│  ┌──────────────────────────────────────────────────────┐     │
│  │                   PySpark                             │     │
│  │  ┌────────────┐  ┌────────────┐  ┌───────────────┐  │     │
│  │  │ customer   │  │ peak_hour  │  │ dish_sales    │  │     │
│  │  │ _flow.py   │  │ .py        │  │ .py           │  │     │
│  │  │ 客流分析    │  │ 高峰分析    │  │ 菜品销量分析   │  │     │
│  │  └────────────┘  └────────────┘  └───────────────┘  │     │
│  │  ┌────────────┐  ┌────────────────────────────────┐  │     │
│  │  │ meal       │  │ main.py (定时调度入口)          │  │     │
│  │  │_prediction │  │                                │  │     │
│  │  │ .py        │  │ crontab / 定时任务 每日执行      │  │     │
│  │  │ 备餐预测    │  │                                │  │     │
│  │  └────────────┘  └────────────────────────────────┘  │     │
│  └──────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

### 2.1.2 Spark 在架构中的位置和作用

**位置**：Spark 位于数据存储层（MySQL）之下，作为独立的离线分析层。

**作用**：
1. **数据读取**：通过 JDBC 连接 MySQL，读取 orders 和 order_item 表中的原始订单数据
2. **数据分析**：利用 SparkSQL 和 DataFrame API 对订单数据进行分组聚合、排序、时间序列计算
3. **结果写入**：将分析结果通过 JDBC 写回 MySQL 的分析结果表（peak_hour_analysis、dish_sales_analysis、customer_flow_analysis、meal_prediction）
4. **与业务系统解耦**：SpringBoot 不直接调用 PySpark，而是读取 PySpark 写入的分析结果表，两者通过 MySQL 异步解耦

**数据流**：
```
订单产生 (SpringBoot) → 写入 MySQL (orders/order_item)
                              ↓
               PySpark 定时读取并分析
                              ↓
               PySpark 写回 MySQL (分析结果表)
                              ↓
               前端请求 → SpringBoot 查询 → Echarts 渲染图表
```

### 2.1.3 技术选型总结

| 层次 | 技术 | 选型理由 |
|------|------|----------|
| 前端 | Vue 3 + Element Plus | 课程要求前后端分离；Element Plus 组件丰富 |
| 图表 | Echarts | 支持折线图、柱状图、饼图，交互效果好 |
| 后端 | SpringBoot 3.x | Java 主流框架，REST API 开发效率高 |
| ORM | MyBatis Plus | 简化 CRUD，条件构造器灵活 |
| 认证 | JWT | 无状态认证，前后端分离标准方案 |
| 数据库 | MySQL 8 | 关系型数据存储，课程标配 |
| 缓存 | Redis | 热点数据缓存，提升查询性能 |
| 大数据计算 | PySpark | 见 1.2 章节详细论证 |

---

## 2.2 系统详细设计——大数据部分与数据集
### 2.2.1 数据集设计

#### 数据集来源

数据集通过**大语言模型生成模拟数据**。由于校园食堂没有公开的真实订单数据集，且课程设计以演示系统能力为目标，采用 LLM 生成符合真实食堂消费规律的模拟数据。

#### 生成方式

编写 Python 脚本 `scripts/generate_data.py`，调用大模型 API 批量生成 SQL INSERT 语句。生成逻辑如下：

1. **用户数据**：生成 200 名学生用户 + 5 名管理员
2. **菜品数据**：生成 30 个菜品，分配到 5 个分类（主食类、炒菜类、汤品类、小吃类、饮品类）
3. **订单数据**：生成 90 天的订单记录（约 5000-8000 条），模拟以下真实规律：
   - 工作日订单量 > 周末订单量
   - 午餐(11:00-13:00)和晚餐(17:00-19:00)为高峰时段
   - 部分菜品有季节性偏好
   - 价格分布符合学生消费水平（8-25 元）

#### 数据集规模

| 表 | 记录数 | 说明 |
|------|------|------|
| user | 205 | 200 普通用户 + 5 管理员 |
| category | 5 | 5 个菜品分类 |
| dish | 30 | 30 个菜品 |
| orders | ~7,000 | 90 天订单数据 |
| order_item | ~12,000 | 每个订单平均 1.7 个菜品 |

数据量在 MB 级别，适合课程演示。PySpark 的处理逻辑本身对数据规模无限制，可扩展至 TB 级。

### 2.2.2 PySpark 详细设计

#### Spark 应用整体设计

```
main.py (总入口)
  │
  ├── 1. SparkSession 初始化
  │     .appName("SmartCanteenAnalysis")
  │     .master("local[*]")    // 本地模式，课程演示
  │     .config("spark.sql.adaptive.enabled", "true")
  │
  ├── 2. JDBC 读取 MySQL 数据
  │     spark.read.jdbc(url, "orders", properties)
  │     spark.read.jdbc(url, "order_item", properties)
  │
  ├── 3. 依次执行分析任务
  │     ├── analyze_customer_flow(spark)      → customer_flow_analysis 表
  │     ├── analyze_peak_hour(spark)           → peak_hour_analysis 表
  │     ├── analyze_dish_sales(spark)           → dish_sales_analysis 表
  │     └── predict_meal_preparation(spark)     → meal_prediction 表
  │
  └── 4. SparkSession 关闭
```

#### 分析任务 1：客流分析 (customer_flow.py)

**Spark 编程要点**：
- 使用 `SparkSession.read.jdbc()` 读取 orders 表为 DataFrame
- 使用 `DATE(create_time)` 提取日期维度
- 使用 `groupBy("analysis_date").agg(count(), sum(), countDistinct())` 聚合
- 使用 `withColumn()` 计算客单价
- 使用 `DataFrame.write.jdbc()` 将结果写回 customer_flow_analysis 表

**核心 SparkSQL**：
```sql
SELECT
    DATE(create_time) AS analysis_date,
    COUNT(*) AS daily_orders,
    SUM(total_amount) AS daily_amount,
    SUM(total_amount) / COUNT(*) AS avg_order_amount,
    COUNT(DISTINCT user_id) AS total_users
FROM orders
WHERE status IN (2, 3)
GROUP BY DATE(create_time)
ORDER BY analysis_date
```

#### 分析任务 2：高峰时段分析 (peak_hour.py)

**Spark 编程要点**：
- 统计数据覆盖天数 `total_days = orders_df.select(date_format(...)).distinct().count()`
- 按 `HOUR(create_time)` 跨所有日期聚合，除以天数得日均订单量和日均销售额
- 按日均订单量降序排列，识别峰值时段
- 结果写入 peak_hour_analysis 表

**核心 SparkSQL**：
```sql
SELECT
    CURRENT_DATE AS analysis_date,
    HOUR(create_time) AS hour,
    COUNT(*) / (SELECT COUNT(DISTINCT DATE(create_time)) FROM orders WHERE is_deleted = 0) AS order_count,
    SUM(total_amount) / (SELECT COUNT(DISTINCT DATE(create_time)) FROM orders WHERE is_deleted = 0) AS total_amount
FROM orders
WHERE is_deleted = 0
GROUP BY HOUR(create_time)
ORDER BY order_count DESC
```

#### 分析任务 3：菜品销量分析 (dish_sales.py)

**Spark 编程要点**：
- JOIN orders 和 order_item 两张表
- 统计数据覆盖天数用于计算日均值
- 按 `(dish_id, dish_name)` 跨所有日期聚合，除以天数得日均销量和日均销售额
- 使用 `row_number().over(Window.orderBy(sales_count.desc()))` 取全局 TOP 10
- 结果写入 dish_sales_analysis 表

**核心 SparkSQL (TOP10)**：
```sql
SELECT
    CURRENT_DATE AS analysis_date,
    oi.dish_id,
    oi.dish_name,
    SUM(oi.quantity) / (SELECT COUNT(DISTINCT DATE(create_time)) FROM orders WHERE is_deleted = 0) AS sales_count,
    SUM(oi.quantity * oi.dish_price) / (SELECT COUNT(DISTINCT DATE(create_time)) FROM orders WHERE is_deleted = 0) AS sales_amount
FROM order_item oi
JOIN orders o ON oi.order_id = o.id
WHERE o.is_deleted = 0
GROUP BY oi.dish_id, oi.dish_name
ORDER BY sales_count DESC
LIMIT 10
```

#### 分析任务 4：备餐预测 (meal_prediction.py)

**Spark 编程要点**：
- 直接从 orders + order_item 原始数据读取，先按 `(DATE, dish_id)` 聚合得到每日销量
- 使用 `Window.partitionBy("dish_id").orderBy("analysis_date")` + `lag()` 获取前 7 天销量
- 计算 7 日移动平均作为预测值，取最近一天数据预测下一天
- `建议备餐量 = 预测销量 * 1.2`（20% 安全冗余）
- 使用 `mode("overwrite")` + `truncate` 覆盖写入 meal_prediction 表

**关键 Spark 代码结构**：
```python
from pyspark.sql.window import Window

# 先按日期+菜品聚合每日销量
daily_sales_df = joined_df.groupBy(
    date_format(col("o.create_time"), "yyyy-MM-dd").alias("analysis_date"),
    col("oi.dish_id"),
    col("oi.dish_name")
).agg(sum(col("oi.quantity")).alias("sales_count"))

# 用 lag 获取前 7 天销量，计算移动平均
window_spec = Window.partitionBy("dish_id").orderBy("analysis_date")
sales_df = daily_sales_df \
    .withColumn("prev_1", lag("sales_count", 1).over(window_spec)) \
    ...
    .withColumn("moving_avg", (col("prev_1") + ... + col("prev_7")) / 7)

# 取最近有数据的一天，预测下一天
prediction_df = sales_df.filter(col("analysis_date") == base_date) \
    .withColumn("predict_date", to_date(lit(predict_date_str))) \
    .withColumn("suggested_prepare", (col("moving_avg") * 1.2).cast("int"))
```

### 2.2.3 数据库连接配置

```python
# config.py
JDBC_URL = "jdbc:mysql://localhost:3306/smart_canteen"
DB_PROPERTIES = {
    "user": "root",
    "password": "xxx",    # 实际从环境变量读取
    "driver": "com.mysql.cj.jdbc.Driver"
}
```

Spark 读取 MySQL 时需要 `mysql-connector-java` jar 包，启动时通过 `--jars` 参数传入或放入 Spark 的 jars 目录。

---

## 2.3 系统详细设计——前后端及其他部分
### 2.3.1 数据库设计

数据库名：`smart_canteen`，共 9 张表，详见 `docs/PRD.md` 第 4 章。

表结构关系：
```
user ──1:N── orders ──1:N── order_item ──N:1── dish ──N:1── category
```

### 2.3.2 RESTful API 设计

统一响应格式：
```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

完整 API 清单见 `docs/PRD.md` 第 5 章，共 26 个端点。

### 2.3.3 前端页面设计

用户端 5 个页面，管理端 6 个页面，数据可视化 4 个页面。详细路由和功能见 `docs/PRD.md` 第 6 章。

### 2.3.4 安全设计

- 用户密码使用 BCrypt 加密存储
- JWT token 有效期 24 小时
- 管理员接口通过拦截器校验 role=1
- CORS 跨域配置仅允许前端域名
