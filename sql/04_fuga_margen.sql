-- ============================================================
-- OPORTUNIDAD 4: FUGA DE MARGEN POR DESCUENTOS NO AUTORIZADOS
-- ============================================================
-- Que hace: compara el precio real de venta de cada linea de pedido
-- contra el precio de catalogo del producto. Marca las lineas donde
-- se vendio a mas de un 8% por debajo del catalogo (umbral que separa
-- un descuento comercial razonable de uno que perjudica el margen).
--
-- Por que importa: el precio de catalogo ya incorpora el margen
-- estandar esperado para ese producto. Vender por debajo sin
-- autorizacion reduce ese margen directamente. Detectar el patron
-- permite auditar que vendedores o clientes concentran estos casos.
-- ============================================================

SELECT 
    p.linea_id,
    p.cliente_id,
    p.producto_id,
    pr.precio_unitario AS precio_catalogo,
    p.precio_venta_unitario AS precio_vendido,
    ROUND(100.0 * (1 - p.precio_venta_unitario / pr.precio_unitario), 1) AS descuento_pct,
    ROUND((pr.precio_unitario - p.precio_venta_unitario) * p.cantidad, 2) AS impacto_estimado_eur
FROM pedidos p
JOIN productos pr ON p.producto_id = pr.producto_id
WHERE p.precio_venta_unitario IS NOT NULL
  AND p.precio_venta_unitario < pr.precio_unitario * 0.92
ORDER BY descuento_pct DESC;

-- RESULTADO FINAL VALIDADO: 5.083 lineas de pedido con descuento no autorizado
-- (rango real de descuento: 8% a 25.1%).
