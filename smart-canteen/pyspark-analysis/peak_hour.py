from pyspark.sql import SparkSession
from pyspark.sql.functions import col, date_format, hour, count, sum
import config

def analyze_peak_hour(spark):
    # Read orders table
    orders_df = spark.read.jdbc(url=config.JDBC_URL, table="orders", properties=config.JDBC_PROPERTIES)

    # Filter out deleted orders
    orders_df = orders_df.filter(col("is_deleted") == 0)

    # Group by date and hour
    peak_hour_df = orders_df.groupBy(
        date_format(col("create_time"), "yyyy-MM-dd").alias("analysis_date"),
        hour(col("create_time")).alias("hour")
    ) \
    .agg(
        count("id").alias("order_count"),
        sum("total_amount").alias("total_amount")
    ) \
    .select("analysis_date", "hour", "order_count", "total_amount")

    # Write to peak_hour_analysis table
    peak_hour_df.write.jdbc(url=config.JDBC_URL, table="peak_hour_analysis", mode="overwrite", properties=config.JDBC_PROPERTIES)

    print("Peak hour analysis completed.")

if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("Peak Hour Analysis") \
        .config("spark.jars", config.MYSQL_JAR_PATH) \
        .getOrCreate()

    analyze_peak_hour(spark)
    spark.stop()