from pyspark.sql import SparkSession
from pyspark.sql.functions import col, date_add, lag, avg, when
from pyspark.sql.window import Window
import config
from datetime import datetime, timedelta

def predict_meals(spark):
    # Read dish_sales_analysis table
    sales_df = spark.read.jdbc(url=config.JDBC_URL, table="dish_sales_analysis", properties=config.JDBC_PROPERTIES)

    # Assuming we predict for tomorrow based on past data
    predict_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    # For each dish, calculate moving average of past 7 days
    window_spec = Window.partitionBy("dish_id").orderBy("analysis_date")

    # Add lag columns for past 7 days
    for i in range(1, 8):
        sales_df = sales_df.withColumn(f"lag_{i}", lag("sales_count", i).over(window_spec))

    # Calculate average of past 7 days
    sales_df = sales_df.withColumn("moving_avg", (col("lag_1") + col("lag_2") + col("lag_3") + col("lag_4") + col("lag_5") + col("lag_6") + col("lag_7")) / 7)

    # Predict for tomorrow: use moving_avg as predicted_sales
    prediction_df = sales_df.filter(col("analysis_date") == (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")) \
        .withColumn("predict_date", date_add(col("analysis_date"), 1)) \
        .withColumn("predicted_sales", col("moving_avg")) \
        .withColumn("suggested_prepare", (col("predicted_sales") * 1.2).cast("int")) \
        .withColumn("confidence", when(col("moving_avg").isNotNull(), 0.8).otherwise(0.0)) \
        .select("predict_date", "dish_id", "dish_name", "predicted_sales", "suggested_prepare", "confidence")

    # Write to meal_prediction table
    prediction_df.write.jdbc(url=config.JDBC_URL, table="meal_prediction", mode="overwrite", properties=config.JDBC_PROPERTIES)

    print("Meal prediction completed.")

if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("Meal Prediction") \
        .config("spark.jars", config.MYSQL_JAR_PATH) \
        .getOrCreate()

    predict_meals(spark)
    spark.stop()