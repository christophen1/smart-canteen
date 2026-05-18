from pyspark.sql import SparkSession
from pyspark.sql.functions import col, date_format, sum, row_number
from pyspark.sql.window import Window
import config


def analyze_dish_sales(spark):
    # 从 MySQL 读取订单表和订单明细表
    orders_df = spark.read.jdbc(url=config.JDBC_URL, table="orders",
                                properties=config.JDBC_PROPERTIES)
    order_item_df = spark.read.jdbc(url=config.JDBC_URL, table="order_item",
                                    properties=config.JDBC_PROPERTIES)

    # 过滤已删除的订单
    orders_df = orders_df.filter(col("is_deleted") == 0)

    # 关联订单表和订单明细表，获取所需字段
    joined_df = order_item_df.alias("oi").join(
        orders_df.alias("o"),
        col("oi.order_id") == col("o.id")
    ).select(
        col("o.create_time"),
        col("oi.dish_id"),
        col("oi.dish_name"),
        col("oi.quantity"),
        col("oi.dish_price")
    )

    # 按日期和菜品分组统计销量和销售额
    dish_sales_df = joined_df.groupBy(
        date_format(col("create_time"), "yyyy-MM-dd").alias("analysis_date"),
        col("dish_id"),
        col("dish_name")
    ).agg(
        sum(col("quantity")).alias("sales_count"),      # 销量
        sum(col("dish_price") * col("quantity")).alias("sales_amount")  # 销售额
    ).select("analysis_date", "dish_id", "dish_name", "sales_count", "sales_amount")

    # 按日期分组，取销量 TOP10 的菜品
    window_spec = Window.partitionBy("analysis_date") \
        .orderBy(col("sales_count").desc())
    top_dish_sales_df = dish_sales_df.withColumn(
        "rank", row_number().over(window_spec)
    ).filter(col("rank") <= 10).drop("rank")

    # 将分析结果写入数据库（使用 truncate 保留表结构）
    write_props = {**config.JDBC_PROPERTIES, "truncate": "true"}
    top_dish_sales_df.write.jdbc(
        url=config.JDBC_URL, table="dish_sales_analysis",
        mode="overwrite", properties=write_props
    )

    print("菜品销量分析完成。")


if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("菜品销量分析") \
        .config("spark.jars", config.MYSQL_JAR_PATH) \
        .getOrCreate()

    analyze_dish_sales(spark)
    spark.stop()
