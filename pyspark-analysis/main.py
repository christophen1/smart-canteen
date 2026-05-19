from pyspark.sql import SparkSession
import config
import customer_flow
import peak_hour
import dish_sales
import meal_prediction
import os


def main():
    # 设置假的 HADOOP_HOME 以避免 Windows 环境问题
    os.environ['HADOOP_HOME'] = 'C:\\fake'
    
    # 初始化 SparkSession
    spark = SparkSession.builder \
        .appName("校园食堂数据分析") \
        .master("local[*]") \
        .config("spark.jars", config.MYSQL_JAR_PATH) \
        .config("spark.sql.warehouse.dir", "file:///tmp/spark-warehouse") \
        .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem") \
        .config("spark.hadoop.fs.hdfs.impl", "org.apache.hadoop.fs.LocalFileSystem") \
        .config("spark.hadoop.fs.defaultFS", "file:///") \
        .config("spark.hadoop.io.native.lib.available", "false") \
        .getOrCreate()

    try:
        # 执行客流分析
        customer_flow.analyze_customer_flow(spark)

        # 执行高峰时段分析
        peak_hour.analyze_peak_hour(spark)

        # 执行菜品销量分析
        dish_sales.analyze_dish_sales(spark)

        # 执行备餐预测
        meal_prediction.predict_meals(spark)

        print("所有分析任务执行完成。")

    except Exception as e:
        print(f"分析过程中发生错误: {e}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
