# Esquema Estrella — Ventas Pentagrama

## fact_ventas
Tabla de hechos: cada fila es una venta individual.

| Columna | Tipo | Descripción |
|---|---|---|
| id_venta | SERIAL (PK) | Identificador único de la venta |
| id_cliente | INTEGER (FK) | Referencia a dim_cliente |
| id_producto | INTEGER (FK) | Referencia a dim_producto |
| id_fecha | INTEGER (FK) | Referencia a dim_fecha |
| id_vendedor | INTEGER (FK) | Referencia a dim_vendedor |
| id_sede | INTEGER (FK) | Referencia a dim_sede |
| monto | NUMERIC(12,2) | Valor real de la venta |
| cantidad | INTEGER | Unidades vendidas |

## dim_cliente
| Columna | Tipo | Descripción |
|---|---|---|
| id_cliente | SERIAL (PK) | Identificador único |
| nombre | VARCHAR(150) NOT NULL | Nombre completo |
| identificacion | VARCHAR(20) | Cédula/NIT |
| direccion | VARCHAR(200) | Dirección |
| telefono | VARCHAR(20) | Teléfono de contacto |
| email | VARCHAR(150) | Correo electrónico |

## dim_producto
| Columna | Tipo | Descripción |
|---|---|---|
| id_producto | SERIAL (PK) | Identificador único |
| nombre_producto | VARCHAR(150) NOT NULL | Nombre del producto |
| descripcion | VARCHAR(300) | Descripción |
| categoria | VARCHAR(100) | Categoría del producto |
| precio_venta | NUMERIC(12,2) | Precio de catálogo actual (referencia). Debe ser >= 0 |
| estado | VARCHAR(15) | Activo/Inactivo |
| color | VARCHAR(50) | Color del producto |

## dim_fecha
| Columna | Tipo | Descripción |
|---|---|---|
| id_fecha | INTEGER (PK) | Identificador único con formato AAAAMMDD (ej: 20260921). No es autoincremental: se calcula al cargar |
| fecha | DATE NOT NULL UNIQUE | Fecha calendario completa |
| ano | INTEGER NOT NULL | Año |
| mes | INTEGER NOT NULL | Mes (1-12) |
| dia_semana_texto | VARCHAR(9) NOT NULL | Día de la semana en texto (ej: Lunes, Miércoles) |
| trimestre | SMALLINT NOT NULL | Trimestre (1-4) |
| es_fin_de_semana | BOOLEAN NOT NULL | Si cae en sábado/domingo |
| es_festivo | BOOLEAN NOT NULL DEFAULT FALSE | Si es día festivo en Colombia |

## dim_vendedor
| Columna | Tipo | Descripción |
|---|---|---|
| id_vendedor | SERIAL (PK) | Identificador único |
| nombre | VARCHAR(150) NOT NULL | Nombre completo |
| identificacion | VARCHAR(20) | Cédula |
| cargo | VARCHAR(100) | Cargo del vendedor |
| zona | VARCHAR(100) | Zona asignada |
| fecha_de_ingreso | DATE NOT NULL | Fecha de ingreso a la empresa |
| porcentaje_comision | NUMERIC(5,2) NOT NULL | Comisión actual (referencia). Entre 0 y 100 |
| estado | VARCHAR(15) | Activo/Inactivo |

## dim_sede
| Columna | Tipo | Descripción |
|---|---|---|
| id_sede | SERIAL (PK) | Identificador único |
| nombre_sede | VARCHAR(150) NOT NULL | Nombre de la sede |
| direccion | VARCHAR(200) | Dirección |
| ciudad | VARCHAR(100) | Ciudad |
| tipo_sede | VARCHAR(50) | Tipo (principal, sucursal, etc.) |

## Decisiones de diseño

- **Dinero con NUMERIC, no FLOAT:** los tipos FLOAT guardan aproximaciones y acumulan errores de centavos; NUMERIC es exacto.
- **id_fecha como AAAAMMDD:** permite identificar el día directamente desde la clave y ordenar cronológicamente sin unir tablas.
- **Slowly Changing Dimensions:** `precio_venta` y `porcentaje_comision` se manejan como SCD Tipo 1 (se sobrescriben). El valor real de cada venta queda protegido en `fact_ventas.monto`.