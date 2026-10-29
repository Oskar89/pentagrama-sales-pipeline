# Notas de Spark

- Los DataFrames de Spark se parecen a los de pandas, pero la sintaxis cambia: `select`, `filter`, `withColumn`, `groupBy`.
- Spark evalúa de forma perezosa: las transformaciones solo describen el trabajo y las acciones (`show`, `count`) lo ejecutan.
- Los DataFrames de Spark son inmutables: cada operación devuelve uno nuevo.
- Verifiqué que los totales por producto coinciden con los de pandas.
