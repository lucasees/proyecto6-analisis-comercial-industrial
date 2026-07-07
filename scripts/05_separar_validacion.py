"""
Separa las columnas 'respuesta' (usadas solo para construir el dataset)
de los archivos de trabajo, y las deja en un archivo aparte de validación
que Lucas puede usar para comprobar su propia limpieza — pero que NO debe
subir a GitHub ni compartir públicamente, porque revela las respuestas.
"""

import pandas as pd

# --- Clientes ---
clientes = pd.read_csv("/home/claude/proyecto6/data/clientes.csv")
validacion_clientes = clientes[["cliente_id", "provincia", "provincia_normalizada"]].copy()
clientes_trabajo = clientes.drop(columns=["provincia_normalizada"])
clientes_trabajo.to_csv("/home/claude/proyecto6/data/clientes.csv", index=False, encoding="utf-8-sig")

# --- Productos ---
productos = pd.read_csv("/home/claude/proyecto6/data/productos.csv")
validacion_productos = productos[["producto_id", "categoria", "categoria_normalizada"]].copy()
productos_trabajo = productos.drop(columns=["categoria_normalizada"])
productos_trabajo.to_csv("/home/claude/proyecto6/data/productos.csv", index=False, encoding="utf-8-sig")

# --- Pedidos ---
pedidos = pd.read_csv("/home/claude/proyecto6/data/pedidos.csv")
validacion_pedidos = pedidos[["linea_id", "fecha_pedido_texto", "fecha_pedido_real"]].copy()
pedidos_trabajo = pedidos.drop(columns=["fecha_pedido_real"])
pedidos_trabajo.to_csv("/home/claude/proyecto6/data/pedidos.csv", index=False, encoding="utf-8-sig")

# --- Archivo de validación (privado, solo para Lucas) ---
with pd.ExcelWriter("/home/claude/proyecto6/data/SOLO_PARA_TI_validacion_no_subir.xlsx") as writer:
    validacion_clientes.to_excel(writer, sheet_name="clientes_provincia", index=False)
    validacion_productos.to_excel(writer, sheet_name="productos_categoria", index=False)
    validacion_pedidos.to_excel(writer, sheet_name="pedidos_fecha", index=False)

print("Listo. Archivos de trabajo limpiados de columnas solución.")
print("Archivo de validación privado creado: SOLO_PARA_TI_validacion_no_subir.xlsx")
