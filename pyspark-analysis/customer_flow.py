from pyspark.sql import SparkSession
from pyspark.sql.functions import col, date_format, count, sum, countDistinct
import config


def analyze_customer_flow(spark):
    # 从 MySQL 读取订单表数据
    orders_df = spark.read.jdbc(url=config.JDBC_URL, table="orders",
                                properties=config.JDBC_PROPERTIES)
    # 过滤已删除的订单
    orders_df = orders_df.filter(col("is_deleted") == 0)

    # 按日期分组统计：订单量、销售额、消费用户数
    customer_flow_df = orders_df.groupBy(
        date_format(col("create_time"), "yyyy-MM-dd").alias("analysis_date")
    ).agg(
        count("id").alias("daily_orders"),        # 日订单量
        sum("total_amount").alias("daily_amount"),  # 日销售额
        countDistinct("user_id").alias("total_users")  # 消费用户数
    ).withColumn(
        "avg_order_amount", col("daily_amount") / col("daily_orders")  # 客单价
    ).select("analysis_date", "daily_orders", "daily_amount",
             "avg_order_amount", "total_users")

    # 将分析结果写入数据库（使用 truncate 保留表结构）
    write_props = {**config.JDBC_PROPERTIES, "truncate": "true"}
    customer_flow_df.write.jdbc(
        url=config.JDBC_URL, table="customer_flow_analysis",
        mode="overwrite", properties=write_props
    )

    print("客流分析完成。")


if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("客流分析") \
        .config("spark.jars", config.MYSQL_JAR_PATH) \
        .getOrCreate()

    analyze_customer_flow(spark)
    spark.stop()
