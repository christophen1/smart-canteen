from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_date, date_format, sum as spark_sum, row_number
from pyspark.sql.window import Window
import config
import mysql.connector


def analyze_dish_sales(spark):
    # 先清空表数据
    conn = mysql.connector.connect(
        host=config.DB_CONFIG['host'],
        port=int(config.DB_CONFIG['port']),
        database=config.DB_CONFIG['database'],
        user=config.DB_CONFIG['user'],
        password=config.DB_CONFIG['password']
    )
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dish_sales_analysis")
    conn.commit()
    cursor.close()
    conn.close()

    # 从 MySQL 读取订单表和订单明细表
    orders_df = spark.read.jdbc(url=config.JDBC_URL, table="orders",
                                properties=config.JDBC_PROPERTIES)
    order_item_df = spark.read.jdbc(url=config.JDBC_URL, table="order_item",
                                    properties=config.JDBC_PROPERTIES)

    # 过滤已删除的订单
    orders_df = orders_df.filter(col("is_deleted") == 0)

    # 计算数据覆盖的天数
    total_days = orders_df.select(
        date_format(col("create_time"), "yyyy-MM-dd")
    ).distinct().count()

    # 关联订单表和订单明细表，获取所需字段
    joined_df = order_item_df.alias("oi").join(
        orders_df.alias("o"),
        col("oi.order_id") == col("o.id")
    ).select(
        col("oi.dish_id"),
        col("oi.dish_name"),
        col("oi.quantity"),
        col("oi.dish_price")
    )

    # 按菜品聚合所有日期的销量，除以天数得到日均值
    dish_sales_df = joined_df.groupBy(
        col("dish_id"),
        col("dish_name")
    ).agg(
        (spark_sum(col("quantity")) / total_days).alias("sales_count"),
        (spark_sum(col("dish_price") * col("quantity")) / total_days).alias("sales_amount")
    ).select("dish_id", "dish_name", "sales_count", "sales_amount")

    # 取全局销量 TOP10
    window_spec = Window.orderBy(col("sales_count").desc())
    top_dish_sales_df = dish_sales_df.withColumn(
        "rank", row_number().over(window_spec)
    ).filter(col("rank") <= 10).drop("rank") \
     .withColumn("analysis_date", current_date()) \
     .select("analysis_date", "dish_id", "dish_name", "sales_count", "sales_amount")

    # 使用追加模式写入，避免覆盖表结构
    top_dish_sales_df.write.jdbc(
        url=config.JDBC_URL, table="dish_sales_analysis",
        mode="append", properties=config.JDBC_PROPERTIES
    )

    print("菜品销量分析完成。TOP10 已写入 dish_sales_analysis。")


if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("菜品销量分析") \
        .config("spark.jars", config.MYSQL_JAR_PATH) \
        .getOrCreate()

    analyze_dish_sales(spark)
    spark.stop()
