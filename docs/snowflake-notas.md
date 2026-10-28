# Notas de Snowflake

**¿Qué es un warehouse en Snowflake?**
Es el motor de cómputo que ejecuta las consultas. No es el lugar donde se guardan los datos: esos viven aparte, y el warehouse solo se enciende cuando hay que consultarlos.

**¿Por qué separar cómputo de almacenamiento ayuda a ahorrar?**
Porque los créditos solo se gastan mientras el warehouse está encendido. Puedo tener muchos datos guardados sin pagar cómputo, y el warehouse se apaga solo tras un minuto de inactividad.

**¿En qué se diferencia de mi PostgreSQL local?**
En PostgreSQL el servidor corre siempre y los datos están pegados al cómputo. En Snowflake se encienden y se apagan por separado, y además puedo cambiar el tamaño del cómputo sin tocar los datos.


## Base de datos y esquema en Snowflake

- La jerarquía es cuenta, base de datos, esquema y tablas. Puedo consultar tablas de distintas bases en una misma consulta escribiendo `base.esquema.tabla`.
- Snowflake convierte a mayúsculas los nombres sin comillas (`VENTAS_DW`), y PostgreSQL los convierte a minúsculas. Conviene evitar las comillas dobles en los nombres.
- `SERIAL` no existe en Snowflake: se usa `NUMBER AUTOINCREMENT`. `VARCHAR` puede ir sin largo, y `NUMBER(12,2)` es lo habitual para dinero.
- Las llaves primarias, únicas y foráneas se aceptan al crear la tabla pero no se hacen cumplir: solo documentan. `NOT NULL` y `CHECK` sí se hacen cumplir en las tablas estándar. Por eso el pipeline debe cargar las dimensiones antes que los hechos y validar las referencias con consultas, por ejemplo con un `LEFT JOIN` que busque huérfanos.


## Comparación PostgreSQL vs Snowflake (5 millones de filas)

Consulta: suma de `monto` y conteo por `id_producto`, top 10, sobre una tabla de 5 millones de filas.

| | Ejecución 1 | Ejecución 2 |
|---|---|---|
| PostgreSQL local | 3,98 s | 3,03 s |
| Snowflake X-Small | 1,00 s | 0,99 s |
| Snowflake Small | 0,89 s | 0,20 s |

**Lo que medí**
- Snowflake X-Small fue unas 3 a 4 veces más rápido que mi PostgreSQL local en esta consulta. Es una prueba con una tabla y pocas ejecuciones, no un benchmark.
- Pasar de X-Small a Small fue una línea de SQL (`ALTER WAREHOUSE`), sin mover datos.
- La caché de resultados devolvió la consulta en 40 ms, con 0 bytes leídos y sin usar el warehouse.
- La tabla ocupa 36.210.688 bytes. Las ejecuciones en Small leyeron 36.210.688 bytes (100 % de la tabla) y las de X-Small 133.276.672 bytes (≈ 368 % del tamaño de la tabla).

**Lo que no pude explicar**
- No sé por qué X-Small reportó más bytes leídos que el tamaño de la tabla, ni por qué Small reportó menos que X-Small. Mi medición no demuestra por sí sola que Snowflake lea solo las columnas necesarias.

**Lo que sé por la teoría**
- Snowflake guarda los datos por columnas y PostgreSQL por filas. En tablas anchas, esto reduce lo que se lee en consultas analíticas.


## Pipeline PostgreSQL a Snowflake (`etapa-2/pipeline_dw.py`)

- Extrae la tabla `ventas` de PostgreSQL, construye cinco dimensiones y la tabla de hechos con pandas, valida la integridad y carga a Snowflake con `write_pandas`.
- Las tablas se vacían con `TRUNCATE` y se recargan completas, así que el pipeline se puede ejecutar varias veces sin duplicar datos.
- `COPY INTO` no funciona sobre tablas con `CHECK`; quité los `CHECK` de Snowflake y moví esas reglas a `validar_integridad`.
- Snowflake no hace cumplir las llaves foráneas: el pipeline valida las referencias antes de cargar y busca ventas huérfanas con `LEFT JOIN` después.
- `write_pandas` busca las columnas por nombre exacto, así que hay que pasar los nombres de columna en mayúsculas.

**Datos simulados** (la tabla fuente no los trae): identificación, dirección, teléfono y correo de los clientes; cargo, zona, fecha de ingreso y comisión de los vendedores; las tres sedes; la cantidad de cada venta; y la categoría y estado de los productos. `precio_venta` es el promedio del monto, no un precio de catálogo real.

**Limitaciones de los datos:** hay 192 clientes únicos para 192 ventas, así que no se puede analizar recompra; y las direcciones generadas con Faker no corresponden a la ciudad de cada sede.