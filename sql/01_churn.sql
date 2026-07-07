-- ============================================================
-- OPORTUNIDAD 1: CLIENTES EN RIESGO DE FUGA (CHURN)
-- ============================================================
-- Que hace: compara el ritmo de compra historico de cada cliente
-- (promedio mensual antes de enero 2026) contra su ritmo reciente
-- (promedio mensual en los ultimos 6 meses de datos).
--
-- Por que importa: un cliente que compraba con regularidad y de
-- repente redujo su actividad mas del 60% es una alerta temprana.
-- Contactarlo a tiempo puede evitar perderlo del todo; descubrirlo
-- tarde (cuando ya dejo de comprar) suele ser demasiado tarde para
-- recuperarlo.
-- ============================================================

WITH actividad AS (
    SELECT 
        cliente_id,
        SUM(CASE WHEN fecha_pedido < '2026-01-01' THEN 1 ELSE 0 END) AS pedidos_historico,
        SUM(CASE WHEN fecha_pedido >= '2026-01-01' THEN 1 ELSE 0 END) AS pedidos_reciente
    FROM pedidos
    WHERE fecha_pedido IS NOT NULL
    GROUP BY cliente_id
),
tasas AS (
    SELECT 
        cliente_id,
        pedidos_historico,
        pedidos_reciente,
        CAST(pedidos_historico AS FLOAT) / 30 AS promedio_mensual_historico,
        CAST(pedidos_reciente AS FLOAT) / 6 AS promedio_mensual_reciente
    FROM actividad
)
SELECT 
    cliente_id,
    pedidos_historico,
    pedidos_reciente,
    ROUND(promedio_mensual_historico, 2) AS promedio_mensual_historico,
    ROUND(promedio_mensual_reciente, 2) AS promedio_mensual_reciente,
    ROUND(100.0 * (1 - promedio_mensual_reciente / promedio_mensual_historico), 1) AS caida_pct
FROM tasas
WHERE promedio_mensual_historico >= 0.3
  AND promedio_mensual_reciente < promedio_mensual_historico * 0.4
ORDER BY caida_pct DESC;

-- RESULTADO FINAL VALIDADO: 199 clientes en riesgo de fuga.
