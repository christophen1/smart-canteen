from pyspark.sql import SparkSession
from pyspark.sql.functions import col, date_format, count, sum, avg, countDistinct
import config

def analyze_customer_flow(spark):
    # Read orders table
    orders_df = spark.read.jdbc(url=config.JDBC_URL, table="orders", properties=config.JDBC_PROPERTIES)

    # Filter out deleted orders
    orders_df = orders_df.filter(col("is_deleted") == 0)

    # 按日期分类
    customer_flow_df = orders_df.groupBy(date_format(col("create_time"), "yyyy-MM-dd").alias("analysis_date")) \
        .agg(
            count("id").alias("daily_orders"),
            sum("total_amount").alias("daily_amount"),
            countDistinct("user_id").alias("total_users")
        ) \
        .withColumn("avg_order_amount", col("daily_amount") / col("daily_orders")) \
        .select("analysis_date", "daily_orders", "daily_amount", "avg_order_amount", "total_users")

    # Write to customer_flow_analysis table
    customer_flow_df.write.jdbc(url=config.JDBC_URL, table="customer_flow_analysis", mode="overwrite", properties=config.JDBC_PROPERTIES)

    print("Customer flow analysis completed.")

if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("Customer Flow Analysis") \
        .config("spark.jars", config.MYSQL_JAR_PATH) \
        .getOrCreate()

    analyze_customer_flow(spark)
    spark.stop()