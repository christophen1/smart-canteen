from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, date_format, sum as spark_sum, lag, when, lit, max as spark_max
from pyspark.sql.window import Window
import config
from datetime import timedelta


def predict_meals(spark):
    # 直接从原始订单数据计算每日每菜品销量（不依赖 dish_sales_analysis）
    orders_df = spark.read.jdbc(url=config.JDBC_URL, table="orders",
                                properties=config.JDBC_PROPERTIES)
    order_item_df = spark.read.jdbc(url=config.JDBC_URL, table="order_item",
                                    properties=config.JDBC_PROPERTIES)

    # 过滤已删除订单
    orders_df = orders_df.filter(col("is_deleted") == 0)

    # 关联订单和明细，按日期+菜品聚合
    daily_sales_df = order_item_df.alias("oi").join(
        orders_df.alias("o"),
        col("oi.order_id") == col("o.id")
    ).groupBy(
        date_format(col("o.create_time"), "yyyy-MM-dd").alias("analysis_date"),
        col("oi.dish_id"),
        col("oi.dish_name")
    ).agg(
        spark_sum(col("oi.quantity")).alias("sales_count")
    ).withColumn(
        "analysis_date", to_date(col("analysis_date"), "yyyy-MM-dd")
    )

    # 获取数据中最大日期作为基准
    max_date_row = daily_sales_df.agg(spark_max("analysis_date")).collect()[0][0]
    if max_date_row is None:
        print("没有历史订单数据，跳过备餐预测。")
        return

    base_date = max_date_row
    predict_date_obj = base_date + timedelta(days=1)
    predict_date_str = predict_date_obj.strftime("%Y-%m-%d")

    print(f"基于 {base_date.strftime('%Y-%m-%d')} 的数据预测 {predict_date_str} 的销量")

    # 窗口：按菜品分组，按日期排序，用于计算历史移动平均
    window_spec = Window.partitionBy("dish_id").orderBy("analysis_date")

    daily_sales_df = daily_sales_df \
        .withColumn("prev_1", lag("sales_count", 1).over(window_spec)) \
        .withColumn("prev_2", lag("sales_count", 2).over(window_spec)) \
        .withColumn("prev_3", lag("sales_count", 3).over(window_spec)) \
        .withColumn("prev_4", lag("sales_count", 4).over(window_spec)) \
        .withColumn("prev_5", lag("sales_count", 5).over(window_spec)) \
        .withColumn("prev_6", lag("sales_count", 6).over(window_spec)) \
        .withColumn("prev_7", lag("sales_count", 7).over(window_spec))

    # 7天移动平均
    daily_sales_df = daily_sales_df.withColumn(
        "moving_avg",
        (col("prev_1") + col("prev_2") + col("prev_3") + col("prev_4")
         + col("prev_5") + col("prev_6") + col("prev_7")) / 7
    )

    # 取最近一天的数据，预测下一天
    prediction_df = daily_sales_df.filter(col("analysis_date") == base_date) \
        .withColumn("predict_date", to_date(lit(predict_date_str), "yyyy-MM-dd")) \
        .withColumn("predicted_sales", col("moving_avg")) \
        .withColumn(
            "suggested_prepare",
            when(col("predicted_sales").isNotNull(),
                 (col("predicted_sales") * 1.2).cast("int")).otherwise(0)
        ) \
        .withColumn(
            "confidence",
            when(col("moving_avg").isNotNull(), lit(0.8)).otherwise(lit(0.0))
        ) \
        .select("predict_date", "dish_id", "dish_name",
                "predicted_sales", "suggested_prepare", "confidence")

    # 覆盖写入（清空旧预测 + 写入新预测）
    write_props = {**config.JDBC_PROPERTIES, "truncate": "true"}
    prediction_df.write.jdbc(
        url=config.JDBC_URL, table="meal_prediction",
        mode="overwrite", properties=write_props
    )

    count = prediction_df.count()
    print(f"备餐预测完成，共 {count} 条预测记录。")


if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("备餐预测") \
        .config("spark.jars", config.MYSQL_JAR_PATH) \
        .getOrCreate()

    predict_meals(spark)
    spark.stop()
