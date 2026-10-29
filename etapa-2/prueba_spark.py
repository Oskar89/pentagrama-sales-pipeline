import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession

spark = SparkSession.builder.master("local[*]").appName("prueba").getOrCreate()
print("Spark", spark.version)

df = spark.createDataFrame([("Ana", 100), ("Luis", 200)], ["vendedor", "monto"])
df.show()
print(df.toPandas())
spark.stop()