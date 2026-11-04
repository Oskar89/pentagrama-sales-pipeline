import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

SEMILLA = 2026
N_VENTAS = 50_000
N_CLIENTES = 10_000

random.seed(SEMILLA)
Faker.seed(SEMILLA)
fake = Faker("es_CO")

PRECIOS = {
    "Persiana enrollable": 250_000,
    "Cortina blackout": 320_000,
    "Persiana veneciana": 280_000,
    "Cortina translucida": 210_000,
    "Panel japones": 360_000,
}
PRODUCTOS = list(PRECIOS)
COLORES = ["Blanco", "Gris", "Beige", "Negro", "Azul"]
VENDEDORES = [
    "Ana Torres", "Luis Ramirez", "Sofia Gomez", "Camilo Ortiz",
    "Valentina Rios", "Andres Mejia", "Paula Castro", "Julian Vargas",
]

# Pool de clientes: cada uno compra varias veces (recompra)
clientes = set()
while len(clientes) < N_CLIENTES:
    clientes.add(fake.name())
clientes = sorted(clientes)

inicio = date(2025, 1, 1)
dias = (date(2026, 10, 31) - inicio).days

filas = []
for i in range(1, N_VENTAS + 1):
    producto = random.choice(PRODUCTOS)
    filas.append({
        "id_venta": i,
        "cliente": random.choice(clientes),
        "producto": producto,
        "color": random.choice(COLORES),
        "vendedor": random.choice(VENDEDORES),
        "monto": int(PRECIOS[producto] * random.uniform(0.7, 1.3)),
        "fecha": (inicio + timedelta(days=random.randint(0, dias))).isoformat(),
    })

df = pd.DataFrame(filas)

# Imperfecciones a propósito, como en un export real
nulos = df.sample(frac=0.02, random_state=SEMILLA).index
df.loc[nulos, "cliente"] = None
duplicadas = df.sample(frac=0.015, random_state=SEMILLA + 1)
df = pd.concat([df, duplicadas], ignore_index=True)

ruta = Path(__file__).resolve().parent.parent / "data" / "ventas_grande.csv"
df.to_csv(ruta, index=False)
print(f"Archivo creado: {ruta}")
print(
    f"Filas: {len(df)} | Clientes únicos: {df['cliente'].nunique()} "
    f"| Nulos en cliente: {df['cliente'].isnull().sum()}"
)