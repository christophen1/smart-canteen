from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, date_add, lag, when, lit
from pyspark.sql.window import Window
import config
from datetime import datetime, timedelta


def predict_meals(spark):
    # 从 MySQL 读取菜品销量分析结果
    sales_df = spark.read.jdbc(url=config.JDBC_URL, table="dish_sales_analysis",
                               properties=config.JDBC_PROPERTIES)

    # 将字符串日期转换为日期类型
    sales_df = sales_df.withColumn(
        "analysis_date",
        to_date(col("analysis_date"), "yyyy-MM-dd")
    )

    # 获取昨天和明天的日期
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    # 定义窗口：按菜品分组，按日期排序
    window_spec = Window.partitionBy("dish_id").orderBy("analysis_date")

    # 添加过去7天的销量滞后列
    sales_df = sales_df.withColumn("prev_1", lag("sales_count", 1).over(window_spec))
    sales_df = sales_df.withColumn("prev_2", lag("sales_count", 2).over(window_spec))
    sales_df = sales_df.withColumn("prev_3", lag("sales_count", 3).over(window_spec))
    sales_df = sales_df.withColumn("prev_4", lag("sales_count", 4).over(window_spec))
    sales_df = sales_df.withColumn("prev_5", lag("sales_count", 5).over(window_spec))
    sales_df = sales_df.withColumn("prev_6", lag("sales_count", 6).over(window_spec))
    sales_df = sales_df.withColumn("prev_7", lag("sales_count", 7).over(window_spec))

    # 计算过去7天的移动平均值
    sales_df = sales_df.withColumn(
        "moving_avg",
        (col("prev_1") + col("prev_2") + col("prev_3") + col("prev_4")
         + col("prev_5") + col("prev_6") + col("prev_7")) / 7
    )

    # 基于最新数据预测明天的销量
    prediction_df = sales_df.filter(col("analysis_date") == yesterday) \
        .withColumn("predict_date", to_date(lit(tomorrow), "yyyy-MM-dd")) \
        .withColumn("predicted_sales", col("moving_avg")) \
        .withColumn(
            "suggested_prepare",
            when(col("predicted_sales").isNotNull(),
                 (col("predicted_sales") * 1.2).cast("int")).otherwise(0)
        ) \
        .withColumn(
            "confidence",
            when(col("moving_avg").isNotNull(), 0.8).otherwise(0.0)
        ) \
        .select("predict_date", "dish_id", "dish_name",
                "predicted_sales", "suggested_prepare", "confidence")

    # 将预测结果写入数据库
    prediction_df.write.jdbc(
        url=config.JDBC_URL, table="meal_prediction",
        mode="overwrite", properties=config.JDBC_PROPERTIES
    )

    print("备餐预测完成。")


if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("备餐预测") \
        .config("spark.jars", config.MYSQL_JAR_PATH) \
        .getOrCreate()

    predict_meals(spark)
    spark.stop()
