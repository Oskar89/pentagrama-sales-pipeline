# PRIMER BLOQUE: imports y el logging

import pandas as pd
import logging
from dotenv import load_dotenv
import os

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()


# SEGUNDO BLOQUE: Función de lectura - la función que lee el CSV crudo.

def leer_datos(ruta_archivo):
    try:
        logger.info(f"Leyendo archivo: {ruta_archivo}")
        df = pd.read_csv(ruta_archivo)
        logger.info(f"Archivo leído correctamente: {df.shape[0]} filas, {df.shape[1]} columnas")
        return df
    except FileNotFoundError:
        logger.error(f"No se encontró el archivo: {ruta_archivo}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado al leer el archivo: {e}")
        raise


# TERCER BLOQUE: Función de limpieza

def limpiar_datos(df):
    try:
        filas_iniciales = df.shape[0]
        logger.info(f"Iniciando limpieza. Filas antes de limpiar: {filas_iniciales}")

        # Eliminar filas sin cliente (dato crítico, sin él la venta es inservible)
        df = df.dropna(subset=["cliente"])

        # Eliminar duplicados exactos (mismo cliente, producto, monto y fecha)
        df = df.drop_duplicates(subset=["cliente", "producto", "monto", "fecha"])

        # Asegurar que monto sea numérico
        df["monto"] = df["monto"].astype(int)

        filas_finales = df.shape[0]
        logger.info(f"Limpieza completada. Filas después de limpiar: {filas_finales} (se eliminaron {filas_iniciales - filas_finales})")

        return df
    except Exception as e:
        logger.error(f"Error durante la limpieza de datos: {e}")
        raise


# CUARTO BLOQUE: función que carga los datos limpios a PostgreSQL. Realice la descarga de PostgreSQL y la creacion de la BD

# CÓDIGO DE CONEXIÓN

from sqlalchemy import create_engine

def cargar_datos(df, nombre_tabla):
    try:
        db_host = os.getenv("DB_HOST")
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_port = os.getenv("DB_PORT")

        conexion_str = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(conexion_str)

        logger.info(f"Conectando a la base de datos '{db_name}'...")
        df.to_sql(nombre_tabla, engine, if_exists="replace", index=False)
        logger.info(f"Datos cargados exitosamente en la tabla '{nombre_tabla}': {df.shape[0]} filas")

    except Exception as e:
        logger.error(f"Error al cargar datos a la base de datos: {e}")
        raise


# BLOQUE FINAL: main

def main():
    logger.info("=" * 50)
    logger.info("Iniciando pipeline de ventas Pentagrama")
    logger.info("=" * 50)

    try:
        df = leer_datos("../data/ventas_pentagrama_sim.csv")
        df = limpiar_datos(df)
        cargar_datos(df, "ventas")

        logger.info("Pipeline completado exitosamente")
    except Exception as e:
        logger.error(f"El pipeline falló: {e}")

if __name__ == "__main__":
    main()