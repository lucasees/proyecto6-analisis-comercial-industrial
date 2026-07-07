"""
Genera la tabla de VENDEDORES/COMERCIALES.

Esta tabla es clave para una de las oportunidades de negocio sembradas:
el "whitespace regional" (zonas con demanda potencial sin cobertura de ventas).

Diseño intencional:
- Algunas provincias de alta demanda (Valencia, Barcelona, Madrid) tienen
  varios comerciales asignados.
- Otras provincias con clientes activos (ver clientes.csv) NO tienen ningún
  comercial asignado -> esto es lo que el análisis debe detectar como oportunidad.
"""

import pandas as pd
from faker import Faker
import random

random.seed(11)
fake = Faker('es_ES')
Faker.seed(11)

# Provincias CON comercial asignado (cobertura)
PROVINCIAS_CON_COBERTURA = {
    "Valencia": 3,
    "Barcelona": 3,
    "Madrid": 3,
    "Alicante": 2,
    "Sevilla": 1,
    "Zaragoza": 1,
    "Bilbao": 1,
}

# Provincias donde HAY clientes pero NO hay comercial (oportunidad de whitespace)
# Castellón, Murcia y Málaga quedan sin cobertura a propósito


def main():
    vendedores = []
    vendedor_id = 200

    for provincia, n_comerciales in PROVINCIAS_CON_COBERTURA.items():
        for _ in range(n_comerciales):
            vendedores.append({
                "vendedor_id": vendedor_id,
                "nombre_vendedor": fake.name(),
                "provincia_asignada": provincia,
                "fecha_ingreso": fake.date_between(start_date="-5y", end_date="-6M"),
                "objetivo_mensual_eur": random.choice([15000, 20000, 25000, 30000]),
            })
            vendedor_id += 1

    df = pd.DataFrame(vendedores)
    df.to_csv("/home/claude/proyecto6/data/vendedores.csv", index=False, encoding="utf-8-sig")
    print(f"vendedores.csv generado: {len(df)} filas")
    print("Provincias SIN cobertura (oportunidad a detectar): Castellón, Murcia, Málaga")


if __name__ == "__main__":
    main()
