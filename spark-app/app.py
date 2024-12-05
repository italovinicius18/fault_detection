from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, DoubleType, TimestampType
from pyspark.sql.functions import from_json, col

if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("VibrationAnalysis") \
        .getOrCreate()

    # Definir o esquema dos dados
    schema = StructType([
        StructField("x", DoubleType(), True),
        StructField("y", DoubleType(), True),
        StructField("z", DoubleType(), True),
        StructField("timestamp", TimestampType(), True)
    ])

    # Ler o stream do Kafka
    df_raw = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "vibration-data") \
        .option("startingOffsets", "latest") \
        .load()

    # Converter os valores de bytes para string
    df_string = df_raw.selectExpr("CAST(value AS STRING) as json_string")

    # Deserializar o JSON e aplicar o esquema
    df_parsed = df_string.select(from_json(col("json_string"), schema).alias("data")).select("data.*")

    # Escrever o stream no Elasticsearch sem o tipo
    query = df_parsed.writeStream \
        .outputMode("append") \
        .format("org.elasticsearch.spark.sql") \
        .option("checkpointLocation", "/tmp/checkpoints") \
        .option("es.nodes", "elasticsearch") \
        .option("es.port", "9200") \
        .option("es.resource", "vibration-index") \
        .start()

    query.awaitTermination()
