from pyspark.sql import SparkSession
import config
import customer_flow
import peak_hour
import dish_sales
import meal_prediction
import os

def main():
    # Set fake HADOOP_HOME to avoid Windows issues
    os.environ['HADOOP_HOME'] = 'C:\\fake'
    
    # Initialize SparkSession
    spark = SparkSession.builder \
        .appName("Smart Canteen Analysis") \
        .master("local[*]") \
        .config("spark.jars", config.MYSQL_JAR_PATH) \
        .config("spark.sql.warehouse.dir", "file:///tmp/spark-warehouse") \
        .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem") \
        .config("spark.hadoop.fs.hdfs.impl", "org.apache.hadoop.fs.LocalFileSystem") \
        .config("spark.hadoop.fs.defaultFS", "file:///") \
        .config("spark.hadoop.io.native.lib.available", "false") \
        .getOrCreate()

    try:
        # Run customer flow analysis
        customer_flow.analyze_customer_flow(spark)

        # Run peak hour analysis
        peak_hour.analyze_peak_hour(spark)

        # Run dish sales analysis
        dish_sales.analyze_dish_sales(spark)

        # Run meal prediction
        meal_prediction.predict_meals(spark)

        print("All analyses completed successfully.")

    except Exception as e:
        print(f"Error during analysis: {e}")
    finally:
        spark.stop()

if __name__ == "__main__":
    main()