# ¿Qué es OLTP, qué es OLAP, y por qué separarlos evita problemas de rendimiento?

OLTP significa 'Online Transaction Processing' y OLAP significa 'Online Analytical Processing'. Son dos arquitecturas de bases de datos diseñadas para propósitos completamente opuestos. Separarlas es una práctica estándar en la ingeniería de datos porque evita que los reportes analíticos pesados dejen fuera de servicio a las aplicaciones que usan los clientes en el día a día.

# Propósito Principal:
OLTP: Procesar transacciones comerciales del día a día.
OLAP: Analizar  grandes volúmenes de datos históricos

# Operaciones comunes:
OLTP: Inserciones, actualizaciones y eliminaciones rápidas (INSERT, UPDATE).
OLAP: Consultas complejas de lectura y agregaciones (SUM, AVG).

# Velocidad de respuesta:
OLTP: Milisegundos
OLAP: Segundos, minutos u horas.

# EJEMPLO REAL EN PENTAGRAMA

"En Pentagrama, distintas áreas corren consultas SQL directamente sobre la base de datos de SAP B1 para generar reportes de apoyo a su gestión. Como estas consultas se ejecutan sobre la misma base transaccional donde se registran ventas, facturación e inventario en tiempo real, cuando esos queries son pesados (agregan muchos datos históricos) compiten por los mismos recursos del servidor con las operaciones diarias del negocio — exactamente el problema que resuelve tener un OLAP separado."

# ¿Por qué es un riesgo técnico, no solo de percepción?
# Bloqueos/concurrencia, consumo de recursos compartidos, y el trade-off de frescura de datos.

No es solo que un reporte "se sienta lento": cuando una consulta pesada lee una tabla mientras
SAP B1 está registrando ventas o facturas al mismo tiempo, la base de datos usa bloqueos
(locks) para evitar que los datos se corrompan, lo que obliga a esas transacciones a esperar
su turno. Además, ese query consume CPU, memoria y disco del mismo servidor que necesita el
negocio para operar en tiempo real — es competencia directa por los mismos recursos, no solo
una molestia de velocidad.

Por eso separar los reportes analíticos en un warehouse aparte también implica aceptar un
trade-off: los datos ahí no están actualizados al segundo, sino que se sincronizan cada cierto
tiempo (por hora o por día). Eso es aceptable para preguntas históricas ("ventas del mes
pasado"), pero no serviría para operaciones que sí necesitan el dato al instante, como
verificar stock disponible antes de facturar una venta — esas siguen corriendo sobre SAP B1.

# Entiende qué es una tabla de hechos (fact table)
Una tabla de hechos (fact table) contiene las MÉTRICAS NUMÉRICAS que quieres analizar — los eventos que realmente pasaron. En tu caso: cada venta es un 'hecho'. La tabla de hechos típicamente tiene pocas columnas descriptivas y muchas filas (una por cada evento/transacción). Ejemplo: fact_ventas tendría columnas como monto, cantidad — los NÚMEROS que quieres sumar, promediar o comparar.

# Entiende qué es una tabla de dimensión (dimension table)
Una tabla de dimensión (dimension table) contiene el CONTEXTO DESCRIPTIVO alrededor de cada hecho — el 'quién, qué, cuándo, dónde' de la venta. Ejemplo: dim_cliente (nombre, ciudad, tipo de cliente), dim_producto (nombre, categoría, color), dim_fecha (día, mes, año, trimestre). Las dimensiones tienen MENOS filas que la tabla de hechos (hay menos clientes únicos que ventas totales), pero MUCHAS más columnas descriptivas.

# Por qué se llama 'esquema estrella' (star schema)
Se llama 'esquema estrella' porque si lo dibujas, la tabla de hechos queda en el centro, y cada dimensión se conecta a ella como un rayo de estrella — fact_ventas en el medio, con dim_cliente, dim_producto, dim_fecha, dim_vendedor rodeándola, cada una conectada por una llave foránea (foreign key). Este diseño es intencional: hace que las consultas de agregación (SUM, AVG, COUNT) sean rápidas y fáciles de escribir, porque casi siempre unes la tabla de hechos con 1 o 2 dimensiones a la vez, nunca todas contra todas de forma compleja.

# La pregunta clave: ¿hecho o dimensión?
La pregunta clave para decidir si un dato va en la tabla de hechos o en una dimensión es: ¿este dato CAMBIA con cada transacción, o es un ATRIBUTO que describe algo que se repite? El monto de una venta cambia siempre (va en hechos). El nombre de un cliente no cambia entre una venta y otra del mismo cliente (va en dimensión, y se relaciona por un ID). Practica mentalmente: ¿dónde iría 'color del producto'? ¿Y 'fecha de la venta'? (ambas son dimensiones — describen contexto, no son métricas que sumas).

# Ver el diseño del esquema estrella en `docs/EstrellaDatos_drawio.png`