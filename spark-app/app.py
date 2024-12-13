from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, DoubleType, IntegerType, StringType, ArrayType, StructType, StructField, IntegerType
from pyspark.sql.functions import from_json, col, explode, pandas_udf
import joblib
import pandas as pd

if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("MillingAnalysisWithMultipleModels") \
        .getOrCreate()

    single_record_schema = StructType([
        StructField("air_temp_k", DoubleType(), True),
        StructField("process_temp_k", DoubleType(), True),
        StructField("rotational_speed_rpm", DoubleType(), True),
        StructField("torque_nm", DoubleType(), True),
        StructField("tool_wear_min", DoubleType(), True),
        StructField("machine_failure", IntegerType(), True),
        StructField("product_id", StringType(), True),
        StructField("type", StringType(), True),
        StructField("timestamp", StringType(), True)  # Mantém como StringType para compatibilidade
    ])

    array_schema = ArrayType(single_record_schema)

    prediction_schema = StructType([
        StructField("HDF_Prediction", IntegerType(), True),
        StructField("Machine_failure_Prediction", IntegerType(), True),
        StructField("OSF_Prediction", IntegerType(), True),
        StructField("PWF_Prediction", IntegerType(), True)
    ])

    model_HDF = joblib.load("/app/models/cat_model_HDF.joblib")
    model_Machine_failure = joblib.load("/app/models/cat_model_Machine failure.joblib")
    model_OSF = joblib.load("/app/models/cat_model_OSF.joblib")
    model_PWF = joblib.load("/app/models/cat_model_PWF.joblib")

    # Broadcast dos modelos
    bc_model_HDF = spark.sparkContext.broadcast(model_HDF)
    bc_model_Machine_failure = spark.sparkContext.broadcast(model_Machine_failure)
    bc_model_OSF = spark.sparkContext.broadcast(model_OSF)
    bc_model_PWF = spark.sparkContext.broadcast(model_PWF)

    @pandas_udf(prediction_schema, 'scalar')
    def predict_udf(*cols):
        data = pd.DataFrame({
            "AIR_TEMPERATURE_K": cols[0],
            "PROCESS_TEMPERATURE_K": cols[1],
            "ROTATIONAL_SPEED_RPM": cols[2],
            "TORQUE_NM": cols[3],
            "TOOL_WEAR_MIN": cols[4],
            "POWER": cols[5],
            "POWER_WEAR": cols[6],
            "TEMPERATURE_DIFFERENCE": cols[7],
            "TEMPERATURE_POWER": cols[8],
            "TYPE_L": cols[9],
            "TYPE_M": cols[10],
        })
        
        HDF_pred = bc_model_HDF.value.predict(data)
        Machine_failure_pred = bc_model_Machine_failure.value.predict(data)
        OSF_pred = bc_model_OSF.value.predict(data)
        PWF_pred = bc_model_PWF.value.predict(data)

        pred_df = pd.DataFrame({
            "HDF_Prediction": HDF_pred,
            "Machine_failure_Prediction": Machine_failure_pred,
            "OSF_Prediction": OSF_pred,
            "PWF_Prediction": PWF_pred
        })
        
        return pred_df

    def write_to_elasticsearch(batch_df, batch_id):
        """
        Função para escrever cada micro-batch no Elasticsearch.
        """
        batch_df.write \
            .format("org.elasticsearch.spark.sql") \
            .option("es.nodes", "elasticsearch") \
            .option("es.port", "9200") \
            .option("es.resource", "milling-index") \
            .option("es.mapping.id", "timestamp") \
            .mode("append") \
            .save()
        
    df_raw = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "milling-data") \
        .option("startingOffsets", "latest") \
        .load()

    df_string = df_raw.selectExpr("CAST(value AS STRING) as json_string")

    df_array = df_string.select(from_json(col("json_string"), array_schema).alias("data_array"))

    df_parsed = df_array.select(explode(col("data_array")).alias("data")).select("data.*")

    df_transformed = df_parsed \
        .withColumn("Power", col("rotational_speed_rpm") * col("torque_nm")) \
        .withColumn("Power_wear", col("Power") * col("tool_wear_min")) \
        .withColumn("Temperature_difference", col("process_temp_k") - col("air_temp_k")) \
        .withColumn("Temperature_power", col("Temperature_difference").cast("double") / col("Power").cast("double")) \
        .withColumn("TYPE_L", col("type") == "L") \
        .withColumn("TYPE_M", col("type") == "M")

    df_features = df_transformed.select(
        col("air_temp_k").alias("AIR_TEMPERATURE_K"),
        col("process_temp_k").alias("PROCESS_TEMPERATURE_K"),
        col("rotational_speed_rpm").alias("ROTATIONAL_SPEED_RPM"),
        col("torque_nm").alias("TORQUE_NM"),
        col("tool_wear_min").alias("TOOL_WEAR_MIN"),
        col("Power").alias("POWER"),
        col("Power_wear").alias("POWER_WEAR"),
        col("Temperature_difference").alias("TEMPERATURE_DIFFERENCE"),
        col("Temperature_power").alias("TEMPERATURE_POWER"),
        col("TYPE_L"),
        col("TYPE_M")
    )

    df_with_predictions = df_features.withColumn("predictions", predict_udf(*df_features.columns))

    df_final = df_with_predictions.select("*", "predictions.*").drop("predictions")


    console_query = df_final.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "true") \
        .start()
    console_query.awaitTermination()


    es_query = df_final.writeStream \
        .outputMode("append") \
        .format("org.elasticsearch.spark.sql") \
        .option("checkpointLocation", "/tmp/checkpoints_es") \
        .option("es.nodes", "elasticsearch") \
        .option("es.port", "9200") \
        .option("es.resource", "milling-index") \
        .option("es.mapping.id", "timestamp") \
        .start()
    es_query.awaitTermination()