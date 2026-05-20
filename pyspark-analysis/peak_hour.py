from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_date, date_format, hour, count, sum
import config
import mysql.connector


def analyze_peak_hour(spark):
    # 先清空表数据
    conn = mysql.connector.connect(
        host=config.DB_CONFIG['host'],
        port=int(config.DB_CONFIG['port']),
        database=config.DB_CONFIG['database'],
        user=config.DB_CONFIG['user'],
        password=config.DB_CONFIG['password']
    )
    cursor = conn.cursor()
    cursor.execute("DELETE FROM peak_hour_analysis")
    conn.commit()
    cursor.close()
    conn.close()

    # 从 MySQL 读取订单表数据
    orders_df = spark.read.jdbc(url=config.JDBC_URL, table="orders",
                                properties=config.JDBC_PROPERTIES)
    # 过滤已删除的订单
    orders_df = orders_df.filter(col("is_deleted") == 0)

    # 计算数据覆盖的天数
    total_days = orders_df.select(
        date_format(col("create_time"), "yyyy-MM-dd")
    ).distinct().count()

    # 按小时聚合所有日期，然后除以天数得到日均值
    peak_hour_df = orders_df.groupBy(
        hour(col("create_time")).alias("hour")
    ).agg(
        (count("id") / total_days).alias("order_count"),
        (sum("total_amount") / total_days).alias("total_amount")
    ).withColumn("analysis_date", current_date()) \
     .select("analysis_date", "hour", "order_count", "total_amount") \
     .orderBy(col("order_count").desc())

    # 使用追加模式写入，避免覆盖表结构
    peak_hour_df.write.jdbc(
        url=config.JDBC_URL, table="peak_hour_analysis",
        mode="append", properties=config.JDBC_PROPERTIES
    )

    top = peak_hour_df.first()
    print(f"高峰时段分析完成。最高峰: {top.hour}:00, 订单量: {top.order_count}")


if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("高峰时段分析") \
        .config("spark.jars", config.MYSQL_JAR_PATH) \
        .getOrCreate()

    analyze_peak_hour(spark)
    spark.stop()
