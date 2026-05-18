from pyspark.sql import SparkSession
from pyspark.sql.functions import col, date_format, hour, count, sum
import config


def analyze_peak_hour(spark):
    # 从 MySQL 读取订单表数据
    orders_df = spark.read.jdbc(url=config.JDBC_URL, table="orders",
                                properties=config.JDBC_PROPERTIES)
    # 过滤已删除的订单
    orders_df = orders_df.filter(col("is_deleted") == 0)

    # 按日期和小时分组统计订单量和金额
    peak_hour_df = orders_df.groupBy(
        date_format(col("create_time"), "yyyy-MM-dd").alias("analysis_date"),
        hour(col("create_time")).alias("hour")
    ).agg(
        count("id").alias("order_count"),      # 每小时订单数
        sum("total_amount").alias("total_amount")  # 每小时销售额
    ).select("analysis_date", "hour", "order_count", "total_amount")

    # 将分析结果写入数据库
    peak_hour_df.write.jdbc(
        url=config.JDBC_URL, table="peak_hour_analysis",
        mode="overwrite", properties=config.JDBC_PROPERTIES
    )

    print("高峰时段分析完成。")


if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("高峰时段分析") \
        .config("spark.jars", config.MYSQL_JAR_PATH) \
        .getOrCreate()

    analyze_peak_hour(spark)
    spark.stop()
