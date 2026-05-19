from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, date_add, lag, when, lit, max
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

    # 获取数据中的最大日期（最近有数据的日期）作为基准
    max_date_row = sales_df.agg(max("analysis_date")).collect()[0][0]
    if max_date_row is None:
        print("没有历史数据，跳过备餐预测。")
        return

    base_date = max_date_row.strftime("%Y-%m-%d")
    # 预测日期 = 基准日期 + 1 天
    from datetime import timedelta
    predict_date_obj = max_date_row + timedelta(days=1)
    predict_date_str = predict_date_obj.strftime("%Y-%m-%d")

    print(f"基于 {base_date} 的数据预测 {predict_date_str} 的销量")

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

    # 基于最近有数据的日期预测下一天的销量
    prediction_df = sales_df.filter(col("analysis_date") == base_date) \
        .withColumn("predict_date", to_date(lit(predict_date_str), "yyyy-MM-dd")) \
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

    # 将预测结果写入数据库（使用 truncate 保留表结构）
    write_props = {**config.JDBC_PROPERTIES, "truncate": "true"}
    prediction_df.write.jdbc(
        url=config.JDBC_URL, table="meal_prediction",
        mode="overwrite", properties=write_props
    )

    print(f"备餐预测完成，共 {prediction_df.count()} 条预测记录。")


if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("备餐预测") \
        .config("spark.jars", config.MYSQL_JAR_PATH) \
        .getOrCreate()

    predict_meals(spark)
    spark.stop()
