# 第4章 技术总结

## 4.1 大数据技术总结
### 4.1.1 Spark Core

本项目使用了 Spark Core 的核心抽象 **RDD** 和 **DataFrame**：

- **DataFrame**：所有分析任务均基于 DataFrame API 实现，DataFrame 提供了比 RDD 更高层次的抽象，支持 SQL 风格的声明式编程，且通过 Catalyst 优化器自动优化执行计划。
- **DAG 调度**：Spark 将多个 Transformation 操作（如 `groupBy`、`agg`、`withColumn`）合并为 Stage，通过 DAG 调度器高效执行，减少了不必要的中间数据落盘。

### 4.1.2 SparkSQL

本项目大量使用了 SparkSQL：

- **SQL 查询**：客流分析、高峰时段分析、菜品销量分析的核心逻辑均通过 SparkSQL 的 `SELECT ... GROUP BY ... ORDER BY` 实现，代码简洁且性能优异。
- **JDBC 数据源**：通过 `spark.read.jdbc()` 和 `df.write.jdbc()` 实现与 MySQL 的双向数据交互，SparkSQL 自动处理分区读取和批量写入。

### 4.1.3 DataFrame API

数据分析的核心编程模型为 DataFrame API：

- **列操作**：`withColumn()` 用于添加派生列（如从 `create_time` 提取 `hour`）
- **聚合操作**：`groupBy().agg(count(), sum(), avg())` 实现分组统计
- **窗口函数**：`Window.partitionBy().orderBy().rowsBetween()` 实现滑动窗口，用于计算移动平均（备餐预测的核心算法）
- **JOIN 操作**：菜品销量分析中 JOIN orders 和 order_item 两张表

### 4.1.4 Spark 工作原理在本项目中的体现

1. **Driver-Executor 架构**：`main.py` 作为 Driver 程序，定义分析逻辑；本地模式 `local[*]` 下，Driver 和 Executor 运行在同一 JVM 中
2. **延迟执行**：Transformation 操作（如 `groupBy`）不会立即执行，直到 Action 操作（如 `write`）时才触发实际计算
3. **Catalyst 优化器**：SparkSQL 查询经过 Catalyst 优化器的解析、逻辑优化、物理优化后生成执行计划
4. **Tungsten 执行引擎**：使用整行编码和内存列式存储加速计算

### 4.1.5 关键代码示例

#### SparkSession 初始化与 JDBC 读取

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("SmartCanteenAnalysis") \
    .master("local[*]") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()

# 从 MySQL 读取订单数据
orders_df = spark.read.jdbc(
    url="jdbc:mysql://localhost:3306/smart_canteen",
    table="orders",
    properties={"user": "root", "password": "xxx", "driver": "com.mysql.cj.jdbc.Driver"}
)
```

#### 窗口函数实现备餐预测

```python
from pyspark.sql.functions import col, avg, ceil
from pyspark.sql.window import Window

# 7 天滑动窗口
window_spec = Window.partitionBy("dish_id") \
    .orderBy("analysis_date") \
    .rowsBetween(-6, 0)

# 计算 7 日移动平均作为预测值
prediction_df = dish_sales_df \
    .withColumn("predicted_sales", ceil(avg("sales_count").over(window_spec))) \
    .withColumn("suggested_prepare", ceil(col("predicted_sales") * 1.2))

# 写入 MySQL
prediction_df.write.jdbc(
    url="jdbc:mysql://localhost:3306/smart_canteen",
    table="meal_prediction",
    mode="append",
    properties=db_properties
)
```

---

## 4.2 其他技术总结
### 4.2.1 SpringBoot 后端技术

- **Spring MVC**：基于注解的 RESTful API 开发，Controller-Service-Mapper 三层架构
- **MyBatis Plus**：通过 `BaseMapper<T>` 继承实现零 SQL 的 CRUD 操作；条件构造器 `LambdaQueryWrapper` 实现类型安全的动态查询
- **JWT 认证**：使用 `jjwt` 库生成和验证 token，通过拦截器对受保护接口进行认证；管理员接口额外校验角色权限
- **Redis 缓存**：对菜品列表、分类列表等高频读取数据使用 Redis 缓存，减少数据库压力
- **全局异常处理**：`@RestControllerAdvice` + `@ExceptionHandler` 统一处理各类异常，保证 API 返回格式一致

### 4.2.2 Vue 3 前端技术

- **Composition API**：使用 `setup()` 和响应式 API（`ref`、`reactive`）组织组件逻辑
- **Element Plus**：使用 `el-table`、`el-form`、`el-dialog` 等组件快速搭建管理后台
- **Axios**：封装请求拦截器和响应拦截器，自动携带 JWT token，统一处理 401 跳转登录
- **Vue Router**：前端路由守卫，未登录用户自动跳转登录页
- **Echarts**：折线图（客流趋势）、柱状图（高峰时段/菜品销量）、饼图（分类占比）的组合展示

### 4.2.3 项目整合

- SpringBoot + Vue 通过 CORS 配置实现跨域通信
- PySpark 通过 MySQL 与 SpringBoot 解耦：SpringBoot 不依赖 PySpark 运行，仅读取分析结果表
- 系统可独立部署：MySQL 独立运行，SpringBoot 可打包为 jar，Vue 可打包为静态文件由 Nginx 托管，PySpark 由定时任务触发
