from pyspark.sql import SparkSession
from pyspark.sql.functions import col, date_format, sum
import config

def analyze_dish_sales(spark):
    # Read orders and order_item tables
    orders_df = spark.read.jdbc(url=config.JDBC_URL, table="orders", properties=config.JDBC_PROPERTIES)
    order_item_df = spark.read.jdbc(url=config.JDBC_URL, table="order_item", properties=config.JDBC_PROPERTIES)

    # Filter out deleted orders
    orders_df = orders_df.filter(col("is_deleted") == 0)

    # Join order_item with orders on order_id
    joined_df = order_item_df.join(orders_df, order_item_df.order_id == orders_df.id)

    # Group by date and dish_id
    dish_sales_df = joined_df.groupBy(
        date_format(orders_df.create_time, "yyyy-MM-dd").alias("analysis_date"),
        order_item_df.dish_id,
        order_item_df.dish_name
    ) \
    .agg(
        sum(order_item_df.quantity).alias("sales_count"),
        sum(order_item_df.dish_price * order_item_df.quantity).alias("sales_amount")
    ) \
    .select("analysis_date", "dish_id", "dish_name", "sales_count", "sales_amount")

    # Get top 10 by sales_count per date (assuming we want top 10 per day)
    # For simplicity, get overall top 10, but PRD says per day/week/month, adjust as needed
    # Here, I'll assume per day
    from pyspark.sql.window import Window
    from pyspark.sql.functions import row_number

    window_spec = Window.partitionBy("analysis_date").orderBy(col("sales_count").desc())
    top_dish_sales_df = dish_sales_df.withColumn("rank", row_number().over(window_spec)) \
        .filter(col("rank") <= 10) \
        .drop("rank")

    # Write to dish_sales_analysis table
    top_dish_sales_df.write.jdbc(url=config.JDBC_URL, table="dish_sales_analysis", mode="overwrite", properties=config.JDBC_PROPERTIES)

    print("Dish sales analysis completed.")

if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("Dish Sales Analysis") \
        .config("spark.jars", config.MYSQL_JAR_PATH) \
        .getOrCreate()

    analyze_dish_sales(spark)
    spark.stop()