import os
import sys
import logging
from pathlib import Path

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, IntegerType, StringType

# Reutilizamos las funciones del pipeline anterior
from pipeline_dw import (
    construir_dim_cliente,
    construir_dim_producto,
    construir_dim_fecha,
    construir_dim_vendedor,
    construir_dim_sede,
    construir_hechos,
    validar_integridad,
    cargar_a_snowflake,
    verificar_carga,
)

logger = logging.getLogger("pipeline_dw")

ESQUEMA = StructType([
    StructField("id_venta", IntegerType()),
    StructField("cliente", StringType()),
    StructField("producto", StringType()),
    StructField("color", StringType()),
    StructField("vendedor", StringType()),
    StructField("monto", IntegerType()),
    StructField("fecha", StringType()),
])


def extraer_y_limpiar_con_spark():
    spark = None
    try:
        ruta = Path(__file__).resolve().parent.parent / "data" / "ventas_grande.csv"
        if not ruta.exists():
            raise FileNotFoundError(f"No existe {ruta}. Ejecuta etapa-2/generar_dataset_grande.py")

        spark = SparkSession.builder.master("local[*]").appName("pipeline_ventas").getOrCreate()
        spark.sparkContext.setLogLevel("ERROR")

        df = spark.read.csv(ruta.as_uri(), header=True, schema=ESQUEMA)
        leidas = df.count()
        logger.info(f"Spark leyó {leidas} filas de {ruta.name}")

        sin_nulos = df.dropna(subset=["cliente"])
        n_nulos = leidas - sin_nulos.count()
        limpio = sin_nulos.dropDuplicates(["cliente", "producto", "monto", "fecha"]).withColumn(
            "fecha", F.to_date("fecha")
        )
        pdf = limpio.toPandas()
        if pdf.empty:
            raise ValueError("La limpieza dejó 0 filas")
        n_dups = leidas - n_nulos - len(pdf)
        logger.info(
            f"Spark limpió los datos: {n_nulos} sin cliente, {n_dups} duplicadas, quedan {len(pdf)} ventas"
        )
        return pdf
    except Exception as e:
        logger.error(f"Error en la extracción con Spark: {e}")
        raise
    finally:
        if spark is not None:
            spark.stop()


def main():
    logger.info("=" * 50)
    logger.info("Iniciando pipeline Spark -> Snowflake (esquema estrella)")
    logger.info("=" * 50)
    try:
        df = extraer_y_limpiar_con_spark()
        dims = {
            "dim_cliente": construir_dim_cliente(df),
            "dim_producto": construir_dim_producto(df),
            "dim_fecha": construir_dim_fecha(df),
            "dim_vendedor": construir_dim_vendedor(df),
            "dim_sede": construir_dim_sede(),
        }
        hechos = construir_hechos(
            df, dims["dim_cliente"], dims["dim_producto"], dims["dim_vendedor"], dims["dim_sede"]
        )
        validar_integridad(hechos, dims, len(df))

        tablas = {**dims, "fact_ventas": hechos}
        cargar_a_snowflake(tablas)
        verificar_carga(tablas)
        logger.info("Pipeline completado exitosamente")
    except Exception as e:
        logger.error(f"El pipeline falló: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()