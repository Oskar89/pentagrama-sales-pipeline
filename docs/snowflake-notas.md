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
- Las llaves primarias, únicas y foráneas se aceptan al crear la tabla pero no se hacen cumplir; solo `NOT NULL` se exige. En un warehouse la calidad de los datos la garantiza el pipeline, no la base de datos.