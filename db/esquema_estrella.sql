DROP TABLE IF EXISTS fact_ventas;
DROP TABLE IF EXISTS dim_sede;
DROP TABLE IF EXISTS dim_vendedor;
DROP TABLE IF EXISTS dim_fecha;
DROP TABLE IF EXISTS dim_producto;
DROP TABLE IF EXISTS dim_cliente;


CREATE TABLE dim_cliente (
    id_cliente SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    identificacion VARCHAR(20),
    direccion VARCHAR(200),
    telefono VARCHAR(20),
    email VARCHAR(150)
);

CREATE TABLE dim_producto(
    id_producto SERIAL PRIMARY KEY,
    nombre_producto VARCHAR(150) NOT NULL,
    descripcion VARCHAR(300),
    categoria VARCHAR(100),
    precio_venta NUMERIC(12, 2) CHECK (precio_venta >= 0),
    estado VARCHAR(15),
    color VARCHAR(50)
);

CREATE TABLE dim_fecha(
    id_fecha INTEGER PRIMARY KEY,
    fecha DATE NOT NULL UNIQUE,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
    dia_semana VARCHAR(9) NOT NULL,
    trimestre SMALLINT NOT NULL CHECK (trimestre BETWEEN 1 AND 4),
    es_fin_de_semana BOOLEAN NOT NULL,
    es_festivo BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE dim_vendedor(
    id_vendedor SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    identificacion VARCHAR(20),
    cargo VARCHAR(100),
    zona VARCHAR(100),
    fecha_de_ingreso DATE NOT NULL,
    porcentaje_comision NUMERIC(5, 2) NOT NULL CHECK (porcentaje_comision BETWEEN 0 AND 100),
    estado VARCHAR(15)
);

CREATE TABLE dim_sede(
    id_sede SERIAL PRIMARY KEY,
    nombre_sede VARCHAR(150) NOT NULL,
    direccion VARCHAR(200),
    ciudad VARCHAR(100),
    tipo_sede VARCHAR(50)
);

CREATE TABLE fact_ventas (
    id_venta SERIAL PRIMARY KEY,
    id_cliente INTEGER NOT NULL REFERENCES dim_cliente(id_cliente),
    id_producto INTEGER NOT NULL REFERENCES dim_producto(id_producto),
    id_fecha INTEGER NOT NULL REFERENCES dim_fecha(id_fecha),
    id_vendedor INTEGER NOT NULL REFERENCES dim_vendedor(id_vendedor),
    id_sede INTEGER NOT NULL REFERENCES dim_sede(id_sede),
    monto NUMERIC(12, 2) NOT NULL CHECK (monto >= 0),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0)
);