from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, DoubleType, IntegerType, StringType, ArrayType
from pyspark.sql.functions import from_json, col, explode

if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("VibrationAnalysis") \
        .getOrCreate()

    # Esquema para um único registro
    single_record_schema = StructType([
        StructField("air_temp_k", DoubleType(), True),
        StructField("process_temp_k", DoubleType(), True),
        StructField("rotational_speed_rpm", DoubleType(), True),
        StructField("torque_nm", DoubleType(), True),
        StructField("tool_wear_min", DoubleType(), True),
        StructField("machine_failure", IntegerType(), True),
        StructField("product_id", StringType(), True),
        StructField("type", StringType(), True),
        StructField("timestamp", StringType(), True) # Precisa ser StringType pois o ES converte o TimestampType para long
    ])

    # Agora definimos um esquema para um array de registros
    array_schema = ArrayType(single_record_schema)

    # Ler o stream do Kafka
    df_raw = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "vibration-data") \
        .option("startingOffsets", "latest") \
        .load()

    # Converter os valores de bytes para string
    df_string = df_raw.selectExpr("CAST(value AS STRING) as json_string")

    # Agora, 'json_string' representa um JSON do tipo:
    # [ { ...registro1... }, { ...registro2... }, ... ]
    # Portanto, usamos o schema de array:
    df_array = df_string.select(from_json(col("json_string"), array_schema).alias("data_array"))

    # Explodir o array em múltiplas linhas
    df_parsed = df_array.select(explode(col("data_array")).alias("data")).select("data.*")

    # Query para imprimir no console (para validar os dados)
    console_query = df_parsed.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .start()

    # Query para escrever no Elasticsearch
    es_query = df_parsed.writeStream \
        .outputMode("append") \
        .format("org.elasticsearch.spark.sql") \
        .option("checkpointLocation", "/tmp/checkpoints") \
        .option("es.nodes", "elasticsearch") \
        .option("es.port", "9200") \
        .option("es.resource", "vibration-index") \
        .option("es.mapping.id", "timestamp") \
        .start()

    # Aguarda a finalização de qualquer um dos streams
    spark.streams.awaitAnyTermination()
