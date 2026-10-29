# Notas de Spark

- Los DataFrames de Spark se parecen a los de pandas, pero la sintaxis cambia: `select`, `filter`, `withColumn`, `groupBy`.
- Spark evalúa de forma perezosa: las transformaciones solo describen el trabajo y las acciones (`show`, `count`) lo ejecutan.
- Los DataFrames de Spark son inmutables: cada operación devuelve uno nuevo.
- Verifiqué que los totales por producto coinciden con los de pandas.


## Particiones y paralelismo

- Spark divide los datos en particiones; cada una la procesa una tarea, y varias tareas corren a la vez en distintos núcleos.
- Mi CSV de ventas se leyó en [1] partición(es). Con `repartition(4)` quedaron unas [51] filas por partición.
- `groupBy` genera un shuffle (aparece `Exchange` en `explain()`); `filter` y `select` no.
- Repartir por una columna con pocos valores distintos puede crear particiones desiguales (sesgo).
- Experimento con 40 millones de filas: 1 núcleo tardó [29.4] s y todos mis núcleos [5.6] s. 
- 1 núcleo: 2.4 s, todos los núcleos: 1.4 s, mejora: 1.7x