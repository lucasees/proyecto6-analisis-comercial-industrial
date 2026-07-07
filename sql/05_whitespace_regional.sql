-- ============================================================
-- OPORTUNIDAD 5: WHITESPACE REGIONAL (ZONAS SIN COMERCIAL)
-- ============================================================
-- Que hace: identifica provincias donde hay clientes activos con
-- pedidos reales, pero que no tienen NINGUN comercial asignado
-- (comparando contra la tabla de vendedores por provincia).
--
-- Por que importa: son zonas con demanda comprobada (no es un
-- mercado hipotetico, ya hay clientes comprando ahi) que la empresa
-- esta dejando sin cobertura comercial dedicada. Asignar un vendedor
-- a estas zonas podria capturar aun mas demanda de la ya existente.
-- ============================================================

SELECT 
    cl.provincia,
    COUNT(DISTINCT cl.cliente_id) AS clientes_activos,
    COUNT(p.linea_id) AS total_pedidos,
    SUM(p.cantidad * p.precio_venta_unitario) AS facturacion_estimada
FROM clientes cl
JOIN pedidos p ON cl.cliente_id = p.cliente_id
WHERE cl.provincia NOT IN (SELECT DISTINCT provincia_asignada FROM vendedores)
GROUP BY cl.provincia
ORDER BY facturacion_estimada DESC;

-- RESULTADO FINAL VALIDADO: Murcia (352 clientes, ~196.3M EUR),
-- Castellon (361 clientes, ~183.7M EUR), Malaga (356 clientes, ~160.3M EUR).
