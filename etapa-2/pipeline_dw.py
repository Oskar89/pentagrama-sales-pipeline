import os
import random
import logging
from datetime import date, timedelta

import pandas as pd
import holidays
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from sqlalchemy import create_engine
from dotenv import load_dotenv
from faker import Faker

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("pipeline_dw.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("pipeline_dw")
logger.setLevel(logging.INFO)

load_dotenv(override=True)
random.seed(42) #semillas
Faker.seed(42)
fake = Faker("es_CO")


def extraer_ventas():
    try:
        url = (
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )
        engine = create_engine(url)
        df = pd.read_sql("SELECT * FROM ventas", engine)
        logger.info(f"Extraídas {len(df)} filas de PostgreSQL (tabla ventas)")
        return df
    except Exception as e:
        logger.error(f"Error al extraer desde PostgreSQL: {e}")
        raise


def _categoria(nombre):
    if nombre.startswith("Persiana"):
        return "Persianas"
    if nombre.startswith("Cortina"):
        return "Cortinas"
    return "Paneles"


def construir_dim_cliente(df):
    nombres = sorted(df["cliente"].dropna().unique())
    dim = pd.DataFrame({"nombre": nombres})
    dim.insert(0, "id_cliente", range(1, len(dim) + 1))
    # Datos SIMULADOS: la tabla fuente solo trae el nombre
    dim["identificacion"] = [fake.numerify("##########") for _ in nombres]
    dim["direccion"] = [fake.address().replace("\n", ", ")[:200] for _ in nombres]
    dim["telefono"] = [fake.numerify("3#########") for _ in nombres]
    dim["email"] = [fake.email() for _ in nombres]
    logger.info(f"dim_cliente: {len(dim)} clientes únicos")
    return dim


def construir_dim_producto(df):
    dim = (
        df.groupby(["producto", "color"], as_index=False)["monto"]
        .mean()
        .rename(columns={"producto": "nombre_producto", "monto": "precio_venta"})
    )
    # precio_venta = precio de referencia calculado (promedio de monto), no un precio de catálogo real
    dim["precio_venta"] = dim["precio_venta"].round(2)
    dim.insert(0, "id_producto", range(1, len(dim) + 1))
    dim["descripcion"] = dim["nombre_producto"] + " color " + dim["color"].str.lower()
    dim["categoria"] = dim["nombre_producto"].apply(_categoria)
    dim["estado"] = "Activo"
    dim = dim[
        ["id_producto", "nombre_producto", "descripcion", "categoria",
         "precio_venta", "estado", "color"]
    ]
    logger.info(f"dim_producto: {len(dim)} combinaciones producto-color")
    return dim


def construir_dim_vendedor(df):
    rng = random.Random(42)
    nombres = sorted(df["vendedor"].dropna().unique())
    zonas = ["Pereira", "Dosquebradas", "Manizales"]
    filas = []
    for i, nombre in enumerate(nombres, start=1):
        # Datos SIMULADOS: la tabla fuente solo trae el nombre
        filas.append({
            "id_vendedor": i,
            "nombre": nombre,
            "identificacion": fake.numerify("##########"),
            "cargo": "Asesor Comercial",
            "zona": rng.choice(zonas),
            "fecha_de_ingreso": date(2020, 1, 1) + timedelta(days=rng.randint(0, 1800)),
            "porcentaje_comision": rng.choice([2.5, 3.0, 3.5, 4.0]),
            "estado": "Activo",
        })
    dim = pd.DataFrame(filas)
    logger.info(f"dim_vendedor: {len(dim)} vendedores")
    return dim


def construir_dim_sede():
    # Sedes SIMULADAS (inventadas): la tabla fuente no tiene información de sedes
    dim = pd.DataFrame([
        {"id_sede": 1, "nombre_sede": "Sede Principal", "ciudad": "Pereira", "tipo_sede": "Principal"},
        {"id_sede": 2, "nombre_sede": "Sucursal Dosquebradas", "ciudad": "Dosquebradas", "tipo_sede": "Sucursal"},
        {"id_sede": 3, "nombre_sede": "Sucursal Manizales", "ciudad": "Manizales", "tipo_sede": "Sucursal"},
    ])
    dim["direccion"] = [fake.address().replace("\n", ", ")[:200] for _ in range(len(dim))]
    dim = dim[["id_sede", "nombre_sede", "direccion", "ciudad", "tipo_sede"]]
    logger.info(f"dim_sede: {len(dim)} sedes")
    return dim


DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def construir_dim_fecha(df):
    fechas = pd.to_datetime(df["fecha"])
    rango = pd.date_range(fechas.min(), fechas.max(), freq="D")
    festivos = holidays.country_holidays("CO", years=sorted({int(a) for a in rango.year}))

    dim = pd.DataFrame({"fecha": rango})
    dim["id_fecha"] = dim["fecha"].dt.strftime("%Y%m%d").astype(int)
    dim["ano"] = dim["fecha"].dt.year
    dim["mes"] = dim["fecha"].dt.month
    dim["dia_semana"] = dim["fecha"].dt.weekday.map(dict(enumerate(DIAS)))
    dim["trimestre"] = dim["fecha"].dt.quarter
    dim["es_fin_de_semana"] = dim["fecha"].dt.weekday >= 5
    dim["es_festivo"] = dim["fecha"].dt.date.map(lambda d: d in festivos)
    dim["fecha"] = dim["fecha"].dt.date
    dim = dim[
        ["id_fecha", "fecha", "ano", "mes", "dia_semana", "trimestre",
         "es_fin_de_semana", "es_festivo"]
    ]
    logger.info(f"dim_fecha: {len(dim)} días ({dim['fecha'].min()} a {dim['fecha'].max()})")
    return dim


def construir_hechos(df, dim_cliente, dim_producto, dim_vendedor, dim_sede):
    rng = random.Random(7)
    h = df.copy()
    h["fecha"] = pd.to_datetime(h["fecha"])

    h = h.merge(
        dim_cliente[["id_cliente", "nombre"]],
        left_on="cliente", right_on="nombre", how="left", validate="many_to_one",
    )
    h = h.merge(
        dim_producto[["id_producto", "nombre_producto", "color"]],
        left_on=["producto", "color"], right_on=["nombre_producto", "color"],
        how="left", validate="many_to_one",
    )
    h = h.merge(
        dim_vendedor[["id_vendedor", "nombre", "zona"]].rename(columns={"nombre": "nombre_vendedor"}),
        left_on="vendedor", right_on="nombre_vendedor", how="left", validate="many_to_one",
    )

    # La sede se deriva de la zona del vendedor (dato SIMULADO pero coherente)
    sede_por_ciudad = dim_sede.set_index("ciudad")["id_sede"]
    h["id_sede"] = h["zona"].map(sede_por_ciudad)
    h["id_fecha"] = h["fecha"].dt.strftime("%Y%m%d").astype(int)
    # cantidad SIMULADA: la fuente no la trae
    h["cantidad"] = [rng.randint(1, 5) for _ in range(len(h))]

    hechos = h[
        ["id_venta", "id_cliente", "id_producto", "id_fecha",
         "id_vendedor", "id_sede", "monto", "cantidad"]
    ].copy()

    if hechos.isnull().any().any():
        raise ValueError("Hay ventas que no encontraron su dimensión (valores nulos en las llaves)")
    hechos = hechos.astype(int)
    logger.info(f"fact_ventas: {len(hechos)} filas")
    return hechos


def validar_integridad(hechos, dims, n_esperado):
    # Snowflake NO hace cumplir las llaves foráneas: las validamos aquí, antes de cargar
    if len(hechos) != n_esperado:
        raise ValueError(f"Se esperaban {n_esperado} ventas y hay {len(hechos)}")
    llaves = {
        "id_cliente": dims["dim_cliente"]["id_cliente"],
        "id_producto": dims["dim_producto"]["id_producto"],
        "id_fecha": dims["dim_fecha"]["id_fecha"],
        "id_vendedor": dims["dim_vendedor"]["id_vendedor"],
        "id_sede": dims["dim_sede"]["id_sede"],
    }
    for columna, validas in llaves.items():
        huerfanas = ~hechos[columna].isin(validas)
        if huerfanas.any():
            raise ValueError(f"{int(huerfanas.sum())} ventas con {columna} inexistente")
    if (hechos["monto"] < 0).any() or (hechos["cantidad"] <= 0).any():
        raise ValueError("Hay montos negativos o cantidades no positivas")

    # Reglas que antes eran CHECK en la base (COPY INTO no admite tablas con CHECK)
    if (dims["dim_producto"]["precio_venta"] < 0).any():
        raise ValueError("Hay precios de venta negativos en dim_producto")
    if not dims["dim_fecha"]["mes"].between(1, 12).all():
        raise ValueError("Hay meses fuera de 1-12 en dim_fecha")
    if not dims["dim_fecha"]["trimestre"].between(1, 4).all():
        raise ValueError("Hay trimestres fuera de 1-4 en dim_fecha")
    if not dims["dim_vendedor"]["porcentaje_comision"].between(0, 100).all():
        raise ValueError("Hay comisiones fuera de 0-100 en dim_vendedor")
    logger.info("Validación de integridad OK")


ORDEN_CARGA = ["dim_cliente", "dim_producto", "dim_fecha", "dim_vendedor", "dim_sede", "fact_ventas"]


def conectar_snowflake():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )


def cargar_a_snowflake(tablas):
    conn = conectar_snowflake()
    try:
        with conn.cursor() as cur:
            # Recarga completa: se vacía en orden inverso (hechos primero)
            for nombre in reversed(ORDEN_CARGA):
                cur.execute(f"TRUNCATE TABLE {nombre}")
                logger.info(f"Tabla {nombre.upper()} vaciada")
        # Dimensiones primero, hechos al final
        for nombre in ORDEN_CARGA:
            df = tablas[nombre].copy()
            df.columns = [c.upper() for c in df.columns]
            ok, _, nfilas, _ = write_pandas(conn, df, nombre.upper())
            if not ok:
                raise RuntimeError(f"Falló la carga de {nombre}")
            logger.info(f"Cargadas {nfilas} filas en {nombre.upper()}")
    except Exception as e:
        logger.error(f"Error al cargar a Snowflake: {e}")
        raise
    finally:
        conn.close()


def verificar_carga(tablas):
    conn = conectar_snowflake()
    try:
        with conn.cursor() as cur:
            for nombre in ORDEN_CARGA:
                cur.execute(f"SELECT COUNT(*) FROM {nombre}")
                en_snowflake = cur.fetchone()[0]
                esperado = len(tablas[nombre])
                if en_snowflake != esperado:
                    raise ValueError(
                        f"{nombre}: Snowflake tiene {en_snowflake} filas y se esperaban {esperado}"
                    )
                logger.info(f"{nombre}: {en_snowflake} filas verificadas")

            # Snowflake no hace cumplir las llaves foráneas: buscamos ventas huérfanas
            for columna, dimension in [
                ("id_cliente", "dim_cliente"),
                ("id_producto", "dim_producto"),
                ("id_fecha", "dim_fecha"),
                ("id_vendedor", "dim_vendedor"),
                ("id_sede", "dim_sede"),
            ]:
                cur.execute(
                    f"SELECT COUNT(*) FROM fact_ventas f "
                    f"LEFT JOIN {dimension} d ON f.{columna} = d.{columna} "
                    f"WHERE d.{columna} IS NULL"
                )
                huerfanas = cur.fetchone()[0]
                if huerfanas:
                    raise ValueError(f"{huerfanas} ventas huérfanas en {columna}")
            logger.info("Verificación en Snowflake OK: sin ventas huérfanas")
    finally:
        conn.close()


def main():
    logger.info("=" * 50)
    logger.info("Iniciando pipeline PostgreSQL -> Snowflake (esquema estrella)")
    logger.info("=" * 50)
    try:
        df = extraer_ventas()
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