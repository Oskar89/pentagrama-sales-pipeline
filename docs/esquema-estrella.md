# Esquema Estrella — Ventas Pentagrama

## fact_ventas
Tabla de hechos: cada fila es una venta individual.

| Columna | Tipo | Descripción |
|---|---|---|
| id_venta | INTEGER (PK) | Identificador único de la venta |
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
| id_cliente | INTEGER (PK) | Identificador único |
| nombre | VARCHAR(150) | Nombre completo |
| identificacion | VARCHAR(20) | Cédula/NIT |
| direccion | VARCHAR(200) | Dirección |
| telefono | VARCHAR(20) | Teléfono de contacto |
| email | VARCHAR(150) | Correo electrónico |

## dim_producto
| Columna | Tipo | Descripción |
|---|---|---|
| id_producto | INTEGER (PK) | Identificador único |
| nombre_producto | VARCHAR(150) | Nombre del producto |
| descripcion | VARCHAR(300) | Descripción |
| categoria | VARCHAR(100) | Categoría del producto |
| precio_venta | NUMERIC(12,2) | Precio de catálogo actual (referencia) |
| estado | VARCHAR(20) | Activo/Inactivo |
| color | VARCHAR(50) | Color del producto |

## dim_fecha
| Columna | Tipo | Descripción |
|---|---|---|
| id_fecha | INTEGER (PK) | Identificador único (formato AAAAMMDD sugerido) |
| año | INTEGER | Año |
| mes | INTEGER | Mes |
| dia_semana | VARCHAR(20) | Día de la semana |
| trimestre | INTEGER | Trimestre (1-4) |
| es_fin_de_semana | BOOLEAN | Si cae en sábado/domingo |
| es_festivo | BOOLEAN | Si es día festivo en Colombia |

## dim_vendedor
| Columna | Tipo | Descripción |
|---|---|---|
| id_vendedor | INTEGER (PK) | Identificador único |
| nombre | VARCHAR(150) | Nombre completo |
| identificacion | VARCHAR(20) | Cédula |
| cargo | VARCHAR(100) | Cargo del vendedor |
| zona | VARCHAR(100) | Zona asignada |
| fecha_de_ingreso | DATE | Fecha de ingreso a la empresa |
| porcentaje_comision | NUMERIC(5,2) | Comisión actual (referencia) |
| estado | VARCHAR(20) | Activo/Inactivo |

## dim_sede
| Columna | Tipo | Descripción |
|---|---|---|
| id_sede | INTEGER (PK) | Identificador único |
| nombre_sede | VARCHAR(150) | Nombre de la sede |
| direccion | VARCHAR(200) | Dirección |
| ciudad | VARCHAR(100) | Ciudad |
| tipo_sede | VARCHAR(50) | Tipo (principal, sucursal, etc.) |