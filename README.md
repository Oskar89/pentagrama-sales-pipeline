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