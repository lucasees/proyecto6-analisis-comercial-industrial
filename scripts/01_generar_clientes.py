"""
Genera la tabla de CLIENTES para el dataset sintético del Proyecto 6.

Simula un distribuidor industrial B2B/B2C con clientes de:
- Fabricantes grandes (compran mucho, pocos)
- Distribuidores medianos (B2B)
- Talleres/pequeñas empresas (B2B pequeño, segmento clave para detectar oportunidad)
- Consumidores finales B2C (minoría, compras puntuales)

Suciedad intencional (para justificar el trabajo de limpieza en Excel/Power Query):
- Nombres de empresa con mayúsculas/minúsculas inconsistentes
- NIFs con formato variable (con guiones, sin guiones, con espacios, algunos inválidos)
- Duplicados exactos y casi-duplicados (mismo cliente, distinto ID, nombre con typo)
- Provincias con nombres inconsistentes (Valencia / VALENCIA / Valencia (VLC) / Comunidad Valenciana)
- Emails con formato inválido en un porcentaje de filas
- Campos vacíos aleatorios en teléfono y provincia
"""

import pandas as pd
import numpy as np
from faker import Faker
import random

random.seed(42)
np.random.seed(42)
fake = Faker('es_ES')
Faker.seed(42)

N_CLIENTES = 3500  # clientes únicos reales antes de duplicar

SEGMENTOS = {
    "Fabricante Grande": 0.05,
    "Distribuidor Mediano": 0.20,
    "Taller/Pequeña Empresa": 0.55,
    "Consumidor Final": 0.20,
}

PROVINCIAS_BASE = [
    "Valencia", "Barcelona", "Madrid", "Alicante", "Castellón",
    "Sevilla", "Zaragoza", "Murcia", "Bilbao", "Málaga"
]

# Variantes sucias de cada provincia para simular inconsistencia de captura
VARIANTES_PROVINCIA = {
    "Valencia": ["Valencia", "VALENCIA", "valencia", "Valencia (VLC)", "Comunidad Valenciana"],
    "Barcelona": ["Barcelona", "BARCELONA", "Bcn", "Barna"],
    "Madrid": ["Madrid", "MADRID", "madrid", "Comunidad de Madrid"],
    "Alicante": ["Alicante", "ALICANTE", "Alacant"],
    "Castellón": ["Castellón", "Castellon", "CASTELLON"],
    "Sevilla": ["Sevilla", "SEVILLA", "sevilla"],
    "Zaragoza": ["Zaragoza", "ZARAGOZA"],
    "Murcia": ["Murcia", "MURCIA", "murcia"],
    "Bilbao": ["Bilbao", "BILBAO", "Bizkaia"],
    "Málaga": ["Málaga", "Malaga", "MALAGA"],
}


def generar_nif_sucio(valido=True):
    """Genera un NIF/CIF con formato inconsistente a propósito."""
    letras = "ABCDEFGHJKLMNPQRSUVW"
    numero = random.randint(10000000, 99999999)
    letra = random.choice(letras)
    formatos = [
        f"{letra}{numero}",
        f"{letra}-{numero}",
        f"{letra} {numero}",
        f"{letra}{numero}".lower(),
    ]
    nif = random.choice(formatos)
    if not valido:
        # NIF corrupto: le falta un dígito o tiene caracteres basura
        nif = nif[:-2] if len(nif) > 4 else nif + "??"
    return nif


def ensuciar_nombre_empresa(nombre):
    """Aplica inconsistencia de capitalización aleatoriamente."""
    r = random.random()
    if r < 0.15:
        return nombre.upper()
    elif r < 0.25:
        return nombre.lower()
    elif r < 0.30:
        return nombre + "  "  # espacios extra al final
    return nombre


def generar_email_sucio(nombre, valido=True):
    base = nombre.lower().replace(" ", ".").replace(",", "")[:20]
    dominio = random.choice(["gmail.com", "empresa.es", "hotmail.com", "outlook.es"])
    email = f"{base}@{dominio}"
    if not valido:
        # email malformado: sin arroba, con espacio, dominio incompleto
        variante = random.choice([
            email.replace("@", ""),
            email.replace(".com", ""),
            email + " ",
            base,  # sin dominio
        ])
        return variante
    return email


def main():
    clientes = []
    cliente_id = 1000

    for _ in range(N_CLIENTES):
        segmento = np.random.choice(list(SEGMENTOS.keys()), p=list(SEGMENTOS.values()))

        if segmento == "Consumidor Final":
            nombre = fake.name()
            es_empresa = False
        else:
            nombre = fake.company()
            es_empresa = True

        provincia_base = random.choice(PROVINCIAS_BASE)
        provincia_sucia = random.choice(VARIANTES_PROVINCIA[provincia_base])

        nif_valido = random.random() > 0.06  # 6% de NIFs corruptos
        email_valido = random.random() > 0.08  # 8% de emails malformados
        tiene_telefono = random.random() > 0.10  # 10% sin teléfono

        cliente = {
            "cliente_id": cliente_id,
            "nombre_cliente": ensuciar_nombre_empresa(nombre) if es_empresa else nombre,
            "es_empresa": es_empresa,
            "segmento": segmento,
            "nif": generar_nif_sucio(valido=nif_valido),
            "provincia": provincia_sucia,
            "provincia_normalizada": provincia_base,  # oculto: se usa para validar limpieza, no para el análisis final
            "email": generar_email_sucio(nombre, valido=email_valido),
            "telefono": fake.phone_number() if tiene_telefono else np.nan,
            "fecha_alta": fake.date_between(start_date="-6y", end_date="-3M"),
        }
        clientes.append(cliente)
        cliente_id += 1

    df = pd.DataFrame(clientes)

    # Duplicados intencionales: ~4% de clientes duplicados con pequeñas variaciones
    n_duplicados = int(N_CLIENTES * 0.04)
    duplicados = df.sample(n=n_duplicados, random_state=42).copy()
    duplicados["cliente_id"] = range(cliente_id, cliente_id + n_duplicados)
    duplicados["nombre_cliente"] = duplicados["nombre_cliente"].apply(
        lambda x: x.strip() + random.choice([" SL", " S.L.", ".", ""])
    )
    df = pd.concat([df, duplicados], ignore_index=True)

    df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # mezclar orden

    df.to_csv("/home/claude/proyecto6/data/clientes.csv", index=False, encoding="utf-8-sig")
    print(f"clientes.csv generado: {len(df)} filas ({n_duplicados} duplicados intencionales)")


if __name__ == "__main__":
    main()
