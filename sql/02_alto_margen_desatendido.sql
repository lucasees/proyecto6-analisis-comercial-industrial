-- ============================================================
-- OPORTUNIDAD 2: ALTO MARGEN DESATENDIDO
-- ============================================================
-- Que hace: identifica clientes con volumen de compra bajo-medio
-- (entre 3 y 25 lineas de pedido en total) donde al menos el 60%
-- de sus compras son de productos de margen alto (mas de 35%).
--
-- Por que importa: son clientes rentables por cada venta, pero que
-- reciben poco contacto comercial (compran poco en cantidad de
-- pedidos). Son candidatos ideales para aumentar la frecuencia de
-- contacto: cuesta menos crecer una cuenta rentable existente que
-- conseguir un cliente nuevo desde cero.
-- ============================================================

WITH compras_cliente AS (
    SELECT 
        p.cliente_id,
        COUNT(*) AS total_lineas,
        SUM(CASE WHEN pr.margen_estandar_pct > 35 THEN 1 ELSE 0 END) AS lineas_alto_margen
    FROM pedidos p
    JOIN productos pr ON p.producto_id = pr.producto_id
    GROUP BY p.cliente_id
)
SELECT 
    c.cliente_id,
    cl.nombre_cliente,
    cl.segmento,
    c.total_lineas,
    c.lineas_alto_margen,
    ROUND(100.0 * c.lineas_alto_margen / c.total_lineas, 1) AS pct_alto_margen
FROM compras_cliente c
JOIN clientes cl ON c.cliente_id = cl.cliente_id
WHERE c.total_lineas BETWEEN 3 AND 25
  AND c.lineas_alto_margen * 1.0 / c.total_lineas >= 0.6
ORDER BY pct_alto_margen DESC;

-- RESULTADO FINAL VALIDADO: 176 clientes de alto margen desatendidos.
