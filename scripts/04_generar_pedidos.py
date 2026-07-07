"""
Genera la tabla de PEDIDOS (líneas de pedido) — la tabla central del análisis.
Objetivo: ~100.000 líneas.

Aquí es donde se "siembran" matemáticamente los 5 patrones de oportunidad
de negocio que el proyecto debe detectar. No son ruido aleatorio: tienen
una lógica de negocio real detrás para que el análisis los pueda descubrir
con SQL/Excel/Power BI de forma legítima.

PATRONES SEMBRADOS:

1. CHURN (riesgo de fuga): ~10% de clientes "Taller/Pequeña Empresa" tienen
   frecuencia normal durante los primeros 30 meses y luego una caída fuerte
   (70-90%) en los últimos 6 meses.

2. OPORTUNIDAD DE ALTO MARGEN DESATENDIDA: ~8% de clientes "Taller/Pequeña
   Empresa" compran poco en volumen pero casi siempre productos de margen
   alto (>35%) — son clientes rentables con poco contacto comercial.

3. GAP DE CROSS-SELLING: entre clientes que compran mucho "Metal", el 40%
   nunca compra "Herramientas" (a pesar de ser un patrón común en el resto),
   representando una venta cruzada no explotada.

4. INCONSISTENCIA DE PRECIOS: ~5% de las líneas tienen un descuento no
   autorizado (10-25%) aplicado sin razón aparente, generando fuga de margen.

5. WHITESPACE REGIONAL: Castellón, Murcia y Málaga tienen clientes activos
   y pedidos crecientes en el tiempo, pero NINGÚN comercial asignado
   (ver vendedores.csv).

SUCIEDAD INTENCIONAL (para justificar limpieza):
- Fechas en formatos mixtos (dd/mm/yyyy, yyyy-mm-dd, dd-mm-yyyy) y algunas inválidas
- Cantidades con texto ("diez"), negativas o en cero por error de captura
- Precio de venta con formato de decimal mixto (coma/punto)
- Un pequeño porcentaje de moneda mal registrada (USD/PTA sin convertir)
- Líneas duplicadas exactas (~1.5%) simulando doble captura
"""

import pandas as pd
import numpy as np
import random
from datetime import date, timedelta

random.seed(99)
np.random.seed(99)

FECHA_INICIO = date(2023, 7, 1)
FECHA_FIN = date(2026, 6, 30)
FECHA_CORTE_CHURN = date(2025, 12, 31)  # a partir de aquí cae la frecuencia en clientes churn

SIN_COBERTURA = {"Castellón", "Murcia", "Málaga"}


def fecha_aleatoria(inicio, fin):
    delta = (fin - inicio).days
    return inicio + timedelta(days=random.randint(0, max(delta, 0)))


def ensuciar_fecha(fecha):
    """Devuelve la fecha en formato de texto inconsistente, o inválida en un 2% de casos."""
    r = random.random()
    if r < 0.02:
        # fecha corrupta a propósito
        return random.choice(["31/02/2025", "2025-13-40", "00/00/0000", ""])
    formatos = [
        fecha.strftime("%d/%m/%Y"),
        fecha.strftime("%Y-%m-%d"),
        fecha.strftime("%d-%m-%Y"),
        fecha.strftime("%d/%m/%y"),
    ]
    return random.choice(formatos)


def ensuciar_cantidad(cantidad):
    r = random.random()
    if r < 0.015:
        return random.choice(["diez", "n/a", "-", str(-abs(cantidad)), "0"])
    return str(cantidad)


def ensuciar_precio(precio):
    if random.random() < 0.3:
        return f"{precio:.2f}".replace(".", ",")
    return f"{precio:.2f}"


def main():
    clientes = pd.read_csv("/home/claude/proyecto6/data/clientes.csv")
    productos = pd.read_csv("/home/claude/proyecto6/data/productos.csv")
    vendedores = pd.read_csv("/home/claude/proyecto6/data/vendedores.csv")

    # Solo clientes "originales" (no duplicados de captura) generan pedidos reales;
    # los duplicados de clientes.csv existen para el ejercicio de limpieza, no para pedidos.
    clientes_base = clientes.drop_duplicates(subset=["nif"], keep="first").copy()

    # Mapear vendedor por provincia (None si no hay cobertura)
    vendedor_por_provincia = {}
    for prov in clientes_base["provincia_normalizada"].unique():
        candidatos = vendedores[vendedores["provincia_asignada"] == prov]
        vendedor_por_provincia[prov] = candidatos["vendedor_id"].tolist() if not candidatos.empty else []

    # --- Definir subconjuntos con patrones sembrados ---
    talleres = clientes_base[clientes_base["segmento"] == "Taller/Pequeña Empresa"]
    churn_ids = set(talleres.sample(frac=0.10, random_state=1)["cliente_id"])
    restantes_talleres = talleres[~talleres["cliente_id"].isin(churn_ids)]
    alto_margen_ids = set(restantes_talleres.sample(frac=0.09, random_state=2)["cliente_id"])

    clientes_metal_heavy = clientes_base[
        clientes_base["segmento"].isin(["Fabricante Grande", "Distribuidor Mediano"])
    ]
    excluir_herramientas_ids = set(clientes_metal_heavy.sample(frac=0.40, random_state=3)["cliente_id"])

    # Medias de líneas de pedido por segmento (para aproximar ~100k líneas totales)
    medias_lineas = {
        "Fabricante Grande": 150,
        "Distribuidor Mediano": 40,
        "Taller/Pequeña Empresa": 15,
        "Consumidor Final": 3,
    }

    prod_metal = productos[productos["categoria_normalizada"] == "Metal"]["producto_id"].tolist()
    prod_herramientas = productos[productos["categoria_normalizada"] == "Herramientas"]["producto_id"].tolist()
    prod_alto_margen = productos[productos["margen_estandar_pct"] > 35]["producto_id"].tolist()
    prod_todos = productos["producto_id"].tolist()
    precio_por_producto = dict(zip(productos["producto_id"], productos["precio_unitario"]))

    lineas = []
    pedido_id = 900000
    linea_id = 1

    for _, cli in clientes_base.iterrows():
        cid = cli["cliente_id"]
        segmento = cli["segmento"]
        provincia = cli["provincia_normalizada"]
        canal = "B2C" if segmento == "Consumidor Final" else "B2B"

        media = medias_lineas[segmento]
        n_lineas_cliente = max(1, int(np.random.lognormal(mean=np.log(media), sigma=0.5)))

        vendedores_disponibles = vendedor_por_provincia.get(provincia, [])
        sin_cobertura = provincia in SIN_COBERTURA

        for _ in range(n_lineas_cliente):
            # --- Fecha, con lógica de churn ---
            if cid in churn_ids:
                if random.random() < 0.85:
                    fecha = fecha_aleatoria(FECHA_INICIO, FECHA_CORTE_CHURN)
                else:
                    fecha = fecha_aleatoria(FECHA_CORTE_CHURN, FECHA_FIN)
            elif sin_cobertura:
                # whitespace regional: sesgar fechas hacia el tramo reciente (demanda creciente)
                if random.random() < 0.6:
                    fecha = fecha_aleatoria(FECHA_CORTE_CHURN, FECHA_FIN)
                else:
                    fecha = fecha_aleatoria(FECHA_INICIO, FECHA_CORTE_CHURN)
            else:
                fecha = fecha_aleatoria(FECHA_INICIO, FECHA_FIN)

            # --- Selección de producto según patrones ---
            if cid in alto_margen_ids and random.random() < 0.75:
                producto_id = random.choice(prod_alto_margen)
            elif cid in excluir_herramientas_ids:
                pool = [p for p in prod_todos if p not in prod_herramientas]
                producto_id = random.choice(pool)
            elif segmento in ["Fabricante Grande", "Distribuidor Mediano"] and random.random() < 0.4:
                producto_id = random.choice(prod_metal)
            else:
                producto_id = random.choice(prod_todos)

            precio_base = precio_por_producto[producto_id]

            # --- Inconsistencia de precio (fuga de margen) ---
            if random.random() < 0.05:
                descuento = random.uniform(0.10, 0.25)
                precio_venta = round(precio_base * (1 - descuento), 2)
            else:
                precio_venta = precio_base

            cantidad_real = random.randint(1, 200) if segmento != "Consumidor Final" else random.randint(1, 5)

            vendedor_id = random.choice(vendedores_disponibles) if vendedores_disponibles else np.nan

            moneda = "EUR"
            if random.random() < 0.01:
                moneda = random.choice(["USD", "PTA"])  # error de captura, sin conversión

            lineas.append({
                "pedido_id": pedido_id,
                "linea_id": linea_id,
                "cliente_id": cid,
                "producto_id": producto_id,
                "vendedor_id": vendedor_id,
                "fecha_pedido_texto": ensuciar_fecha(fecha),
                "fecha_pedido_real": fecha,  # se usa solo para validar limpieza, no para el análisis final
                "cantidad_texto": ensuciar_cantidad(cantidad_real),
                "precio_venta_unitario_texto": ensuciar_precio(precio_venta),
                "moneda": moneda,
                "canal": canal,
            })
            linea_id += 1

            if random.random() < 0.3:  # varias líneas por pedido
                pedido_id += 1

        pedido_id += 1

    df = pd.DataFrame(lineas)

    # --- Duplicados exactos de líneas (doble captura) ---
    n_dup = int(len(df) * 0.015)
    dup = df.sample(n=n_dup, random_state=42).copy()
    df = pd.concat([df, dup], ignore_index=True)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df["linea_id"] = range(1, len(df) + 1)

    df.to_csv("/home/claude/proyecto6/data/pedidos.csv", index=False, encoding="utf-8-sig")
    print(f"pedidos.csv generado: {len(df)} filas")
    print(f"Clientes churn sembrados: {len(churn_ids)}")
    print(f"Clientes alto margen desatendido sembrados: {len(alto_margen_ids)}")
    print(f"Clientes con gap cross-sell (excluyen herramientas) sembrados: {len(excluir_herramientas_ids)}")


if __name__ == "__main__":
    main()
