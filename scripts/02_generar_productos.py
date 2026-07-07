"""
Genera la tabla de PRODUCTOS del distribuidor industrial.

Categorías: Metal, Plástico, Componentes, Herramientas, Packaging.
La mezcla de metal + plástico + componentes es intencional: evita que el
dataset "grite" un sector único y lo hace aplicable a distintas industrias
(incluida la plástica) sin ser obvio.

Suciedad intencional:
- Precios en distintas unidades de referencia mezcladas (por unidad, por kg, por caja de 100)
  sin normalizar en un campo separado -> obliga a limpiar antes de comparar
- Algunos precios con coma decimal (formato español) y otros con punto (mezclado a propósito)
- Nombres de producto con variantes de mayúsculas y espacios extra
- Categoría con inconsistencias de escritura (Ej: "Metal" / "METAL" / "metal ")
"""

import pandas as pd
import numpy as np
import random

random.seed(7)
np.random.seed(7)

CATEGORIAS = {
    "Metal": {
        "productos": [
            "Perfil de acero galvanizado", "Chapa de aluminio", "Tornillería industrial",
            "Varilla de acero inoxidable", "Bisagra reforzada", "Placa base metálica",
        ],
        "precio_rango": (8, 450),
        "unidad": "unidad",
    },
    "Plástico": {
        "productos": [
            "Granza de polipropileno", "Lámina de PVC rígido", "Tubo de polietileno",
            "Pieza inyectada ABS", "Film retráctil industrial", "Perfil de PVC extruido",
        ],
        "precio_rango": (0.8, 6.5),
        "unidad": "kg",
    },
    "Componentes": {
        "productos": [
            "Rodamiento industrial", "Motor eléctrico 1CV", "Sensor de proximidad",
            "Conector eléctrico industrial", "Válvula neumática", "Actuador lineal",
        ],
        "precio_rango": (15, 800),
        "unidad": "unidad",
    },
    "Herramientas": {
        "productos": [
            "Taladro industrial", "Juego de llaves fijas", "Amoladora angular",
            "Pistola de calor", "Prensa manual", "Sierra de banco",
        ],
        "precio_rango": (25, 600),
        "unidad": "unidad",
    },
    "Packaging": {
        "productos": [
            "Caja de cartón reforzado", "Palet de plástico", "Film de paletizado",
            "Bolsa industrial polietileno", "Cinta de embalaje", "Envase plástico rígido",
        ],
        "precio_rango": (0.3, 40),
        "unidad": "caja",
    },
}

VARIANTES_CATEGORIA_SUCIA = {
    "Metal": ["Metal", "METAL", "metal", "Metal "],
    "Plástico": ["Plástico", "PLASTICO", "plastico", "Plástico "],
    "Componentes": ["Componentes", "COMPONENTES", "componentes"],
    "Herramientas": ["Herramientas", "HERRAMIENTAS", "herramientas"],
    "Packaging": ["Packaging", "PACKAGING", "packaging"],
}


def formatear_precio_sucio(precio):
    """Mezcla formato decimal español (coma) e inglés (punto) a propósito."""
    if random.random() < 0.35:
        return f"{precio:.2f}".replace(".", ",")
    return f"{precio:.2f}"


def main():
    productos = []
    producto_id = 5000

    for categoria, info in CATEGORIAS.items():
        for nombre_base in info["productos"]:
            for variante in range(random.randint(3, 6)):  # varias referencias por producto base
                precio = round(random.uniform(*info["precio_rango"]), 2)
                nombre_sucio = nombre_base
                if random.random() < 0.2:
                    nombre_sucio = nombre_sucio.upper()
                if random.random() < 0.1:
                    nombre_sucio = "  " + nombre_sucio

                producto = {
                    "producto_id": producto_id,
                    "nombre_producto": f"{nombre_sucio} Ref.{100+variante}",
                    "categoria": random.choice(VARIANTES_CATEGORIA_SUCIA[categoria]),
                    "categoria_normalizada": categoria,
                    "precio_unitario_texto": formatear_precio_sucio(precio),
                    "precio_unitario": precio,
                    "unidad_medida": info["unidad"],
                    "margen_estandar_pct": round(random.uniform(12, 45), 1),
                }
                productos.append(producto)
                producto_id += 1

    df = pd.DataFrame(productos)
    df.to_csv("/home/claude/proyecto6/data/productos.csv", index=False, encoding="utf-8-sig")
    print(f"productos.csv generado: {len(df)} filas")


if __name__ == "__main__":
    main()
