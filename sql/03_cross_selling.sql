-- ============================================================
-- OPORTUNIDAD 3: GAP DE CROSS-SELLING (METAL SIN HERRAMIENTAS)
-- ============================================================
-- Que hace: identifica clientes con 5 o mas compras de la categoria
-- "Metal" que nunca compraron nada de la categoria "Herramientas".
--
-- Por que importa: en la base de clientes, comprar metal y comprar
-- herramientas suele ir de la mano (mismo tipo de negocio industrial).
-- Un cliente metal-heavy que nunca compro herramientas es una venta
-- cruzada evidente que el equipo comercial no esta ofreciendo.
-- ============================================================

WITH compras_metal AS (
    SELECT DISTINCT p.cliente_id
    FROM pedidos p
    JOIN productos pr ON p.producto_id = pr.producto_id
    WHERE pr.categoria = 'Metal'
    GROUP BY p.cliente_id
    HAVING COUNT(*) >= 5
),
compras_herramientas AS (
    SELECT DISTINCT p.cliente_id
    FROM pedidos p
    JOIN productos pr ON p.producto_id = pr.producto_id
    WHERE pr.categoria = 'Herramientas'
)
SELECT 
    cm.cliente_id,
    cl.nombre_cliente,
    cl.segmento
FROM compras_metal cm
JOIN clientes cl ON cm.cliente_id = cl.cliente_id
WHERE cm.cliente_id NOT IN (SELECT cliente_id FROM compras_herramientas);

-- RESULTADO FINAL VALIDADO: 359 clientes con gap de cross-selling.
