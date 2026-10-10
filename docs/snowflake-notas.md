# Notas de Snowflake

**¿Qué es un warehouse en Snowflake?**
Es el motor de cómputo que ejecuta las consultas. No es el lugar donde se guardan los datos: esos viven aparte, y el warehouse solo se enciende cuando hay que consultarlos.

**¿Por qué separar cómputo de almacenamiento ayuda a ahorrar?**
Porque los créditos solo se gastan mientras el warehouse está encendido. Puedo tener muchos datos guardados sin pagar cómputo, y el warehouse se apaga solo tras un minuto de inactividad.

**¿En qué se diferencia de mi PostgreSQL local?**
En PostgreSQL el servidor corre siempre y los datos están pegados al cómputo. En Snowflake se encienden y se apagan por separado, y además puedo cambiar el tamaño del cómputo sin tocar los datos.