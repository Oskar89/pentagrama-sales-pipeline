USE DATABASE ventas_dw;
USE SCHEMA core;

DROP TABLE IF EXISTS fact_ventas;
DROP TABLE IF EXISTS dim_sede;
DROP TABLE IF EXISTS dim_vendedor;
DROP TABLE IF EXISTS dim_fecha;
DROP TABLE IF EXISTS dim_producto;
DROP TABLE IF EXISTS dim_cliente;

CREATE TABLE dim_cliente (
    id_cliente NUMBER AUTOINCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    identificacion VARCHAR(20),
    direccion VARCHAR(200),
    telefono VARCHAR(20),
    email VARCHAR(150)
);

CREATE TABLE dim_producto (
    id_producto NUMBER AUTOINCREMENT PRIMARY KEY,
    nombre_producto VARCHAR(150) NOT NULL,
    descripcion VARCHAR(300),
    categoria VARCHAR(100),
    precio_venta NUMBER(12, 2),
    estado VARCHAR(15),
    color VARCHAR(50)
);

CREATE TABLE dim_fecha (
    id_fecha NUMBER PRIMARY KEY,
    fecha DATE NOT NULL UNIQUE,
    ano NUMBER NOT NULL,
    mes NUMBER NOT NULL,
    dia_semana VARCHAR(9) NOT NULL,
    trimestre NUMBER NOT NULL,
    es_fin_de_semana BOOLEAN NOT NULL,
    es_festivo BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE dim_vendedor (
    id_vendedor NUMBER AUTOINCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    identificacion VARCHAR(20),
    cargo VARCHAR(100),
    zona VARCHAR(100),
    fecha_de_ingreso DATE NOT NULL,
    porcentaje_comision NUMBER(5, 2) NOT NULL,
    estado VARCHAR(15)
);

CREATE TABLE dim_sede (
    id_sede NUMBER AUTOINCREMENT PRIMARY KEY,
    nombre_sede VARCHAR(150) NOT NULL,
    direccion VARCHAR(200),
    ciudad VARCHAR(100),
    tipo_sede VARCHAR(50)
);

CREATE TABLE fact_ventas (
    id_venta NUMBER AUTOINCREMENT PRIMARY KEY,
    id_cliente NUMBER NOT NULL REFERENCES dim_cliente(id_cliente),
    id_producto NUMBER NOT NULL REFERENCES dim_producto(id_producto),
    id_fecha NUMBER NOT NULL REFERENCES dim_fecha(id_fecha),
    id_vendedor NUMBER NOT NULL REFERENCES dim_vendedor(id_vendedor),
    id_sede NUMBER NOT NULL REFERENCES dim_sede(id_sede),
    monto NUMBER(12, 2) NOT NULL,
    cantidad NUMBER NOT NULL
);