# Proyecto 6 — Análisis Comercial Industrial B2B/B2C
## Documento de conceptos, herramientas y comandos (material de estudio)

Este documento se actualiza durante todo el proyecto y al finalizar se convierte
a PDF como guía de estudio: teoría + práctica + comandos + decisiones.

---

## 1. Contexto y objetivo del proyecto

**Qué es:** Análisis comercial de un distribuidor industrial ficticio (metal,
plástico, componentes, herramientas, packaging) con datos sucios a gran escala
(~100.000 líneas de pedido), diseñado para demostrar dos capacidades distintas:

1. **Limpieza de datos "sucios"** con SQL + Excel avanzado (Power Query)
2. **Detección de oportunidades de negocio** — no solo "qué pasó" sino "qué se puede hacer"

**Por qué el dataset es sintético:** los datos comerciales B2B reales son
información sensible que las empresas no publican. Generar un dataset sintético
pero realista es la práctica estándar en portfolios de analytics. Se documenta
de forma transparente en el README del repositorio (igual que la metodología
de rental yield del Proyecto 5).

**Contexto estratégico:** el proyecto está diseñado para resultar relevante al
sector industrial/plástico sin ser obviamente dirigido a una empresa o proceso
de selección puntual — por eso el dataset mezcla metal + plástico + componentes
en vez de un único material.

---

## 2. Estructura del dataset

| Archivo | Filas aprox. | Contenido |
|---|---|---|
| `clientes.csv` | ~3.640 | Empresas B2B + consumidores B2C |
| `productos.csv` | 144 | Catálogo: Metal, Plástico, Componentes, Herramientas, Packaging |
| `vendedores.csv` | 14 | Comerciales por provincia (cobertura desigual a propósito) |
| `pedidos.csv` | ~99.915 | Líneas de pedido — tabla central del análisis |

Archivo privado `SOLO_PARA_TI_validacion_no_subir.xlsx`: contiene las columnas
"respuesta" (valores reales antes de ensuciarlos) para que Lucas verifique su
propia limpieza. **Nunca se sube a GitHub.**

---

## 3. Conceptos técnicos

### 3.1 Generación de datos sintéticos (Python)

- **Faker:** librería que genera datos ficticios realistas (nombres, empresas,
  teléfonos, fechas). Se usó `Faker('es_ES')` para que suene español.
- **Semillas aleatorias (`random.seed`, `np.random.seed`):** fijan el punto de
  partida del generador aleatorio para que el dataset sea reproducible.
- **Distribución lognormal:** usada para el número de pedidos por cliente —
  crea una "cola larga" (pocos clientes con muchísimos pedidos, muchos con
  pocos), que es el patrón real de compra B2B.

### 3.2 Power Query — conceptos generales

- **Power Query** es el motor de limpieza y transformación de datos integrado
  en Excel. Cada acción que hacés con los botones (Recortar, Reemplazar
  valores, etc.) se traduce automáticamente a código en un lenguaje llamado
  **M**, visible en la "barra de fórmulas" de arriba.
- **"Pasos aplicados":** cada transformación queda registrada como un paso
  independiente y reversible. Se pueden editar, reordenar o eliminar sin
  tocar los demás — a condición de no crear referencias rotas (ver lección
  aprendida en la sección 6).
- **Regla de oro aprendida en este proyecto:** para editar la lógica de una
  columna personalizada ya creada, usar siempre el ⚙️ de ese paso (abre una
  ventanita con un cuadro de fórmula acotado). Nunca editar directamente la
  barra de fórmulas grande de arriba pensando que es lo mismo — ese cuadro
  contiene el `Table.AddColumn(..., each ...)` completo, y si se borra ese
  "envoltorio" el paso se rompe.

### 3.3 Funciones M usadas y para qué sirven

| Función | Qué hace |
|---|---|
| `Text.Trim(texto)` | Quita espacios en blanco al principio y al final |
| `Text.Upper(texto)` / `Text.Lower(texto)` | Convierte a mayúsculas / minúsculas |
| `Text.Proper(texto)` | Pone en mayúscula la primera letra de cada palabra |
| `Text.Length(texto)` | Cuenta cuántos caracteres tiene un texto |
| `Text.Contains(texto, "x")` | Devuelve verdadero/falso si el texto contiene "x" |
| `Text.AfterDelimiter(texto, "@")` | Devuelve todo lo que hay después de un carácter (ej. el dominio de un email) |
| `Text.Split(texto, "-")` | Separa un texto en partes usando un carácter como corte |
| `Table.ReplaceValue(tabla, buscar, reemplazar, Replacer.ReplaceText, {"columna"})` | Reemplaza un valor por otro dentro de una columna |
| `Table.AddColumn(tabla, "nombre", each ...)` | Crea una columna nueva calculada a partir de una fórmula |
| `Table.TransformColumnTypes(tabla, {{"columna", tipo}}, "es")` | Cambia el tipo de dato de una o más columnas, opcionalmente indicando configuración regional |
| `Table.Group(tabla, {"columna"}, {{"Cantidad", each Table.RowCount(_), Int64.Type}})` | Agrupa filas y cuenta cuántas hay por cada valor — útil para verificar resultados |
| `Number.FromText(texto, "en-US")` | Convierte texto a número, indicando el formato regional |
| `Date.FromText(texto, [Format="dd/MM/yyyy"])` | Convierte texto a fecha, indicando el formato esperado |
| `try ... otherwise ...` | Intenta ejecutar una operación; si falla (error), devuelve un valor alternativo en vez de romper toda la columna |
| `if condición then A else B` | Estructura condicional básica del lenguaje M |

---

## 4. Esquema del proceso de limpieza (visión general)

```
                    ┌─────────────────────┐
                    │   Archivo CSV sucio  │
                    │  (clientes/productos │
                    │       /pedidos)       │
                    └──────────┬──────────┘
                               │
                    Datos > Obtener datos >
                    Desde archivo > Desde texto/CSV
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Vista previa        │
                    │  → "Transformar      │
                    │     datos"           │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  EDITOR DE POWER     │
                    │  QUERY               │
                    │  (cada acción crea   │
                    │  un "paso aplicado") │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
     Texto inconsistente  Categorías/valores  Formatos numéricos
     (nombres, espacios)  repetidos distinto  o de fecha mezclados
              │                ▼                ▼
      Recortar +         Reemplazar valores  Columna personalizada
      Mayúscula inicial  (uno por variante)  con lógica if/then
      en cada palabra                        o Cambiar tipo con
                                              configuración regional
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │  Columnas de         │
                    │  VALIDACIÓN          │
                    │  (marca "Válido" /   │
                    │  "Revisar" en vez de │
                    │  inventar datos)     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Verificar con       │
                    │  "Agrupar por" +     │
                    │  Contar filas        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Cerrar y cargar +   │
                    │  Guardar (Cmd+S)     │
                    └─────────────────────┘
```

**Principio clave aplicado en todo el proyecto:** cuando un dato está roto o
incompleto (NIF corrupto, email inválido, teléfono vacío, moneda incorrecta),
**no se intenta "adivinar" el valor correcto.** Se crea una columna de
validación que lo marca como "Revisar", para decidir qué hacer con esas filas
más adelante (excluirlas, tratarlas aparte, etc.) sin ensuciar el análisis con
datos inventados.

---

## 5. Limpieza realizada, archivo por archivo

### 5.1 `clientes.csv` (~3.640 filas) — COMPLETO

```
nombre_cliente ──► Recortar ──► Poner en mayúsculas cada palabra
                                    │
                                    ▼
                        "grupo bravo  " → "Grupo Bravo"

provincia ──► Reemplazar valores (14 reemplazos, uno por variante)
                                    │
                                    ▼
                "VALENCIA"/"Valencia (VLC)"/"Comunidad Valenciana" → "Valencia"

nif ──► Mayúsculas ──► Recortar ──► Reemplazar "-" por nada
                                 ──► Reemplazar " " por nada
                                    │
                                    ▼
                        "w 50446607" → "W50446607"

nif_valido ──► Columna personalizada:
    if Text.Length([nif]) = 9 then "Válido" else "Revisar"
    Resultado: 3.388 Válido / 252 Revisar (6,9%)

email_valido ──► Columna personalizada:
    if Text.Contains([email], "@") and
       Text.Contains(Text.AfterDelimiter([email], "@"), ".")
    then "Válido" else "Revisar"
    Resultado: 3.450 Válido / 190 Revisar (5,2%)

telefono_valido ──► Columna personalizada:
    if [telefono] = null or Text.Trim(Text.From([telefono])) = ""
    then "Revisar" else "Válido"
    Resultado: 3.271 Válido / 369 Revisar (10,1%)
```

### 5.2 `productos.csv` (144 filas) — COMPLETO

```
categoria ──► Recortar ──► Reemplazar valores (5 reemplazos)
                                    │
                                    ▼
        "METAL"/"metal"/"Metal " → "Metal"   (mismo patrón para las 5 categorías)

nombre_producto ──► Recortar ──► Poner en mayúsculas cada palabra
                                    │
                                    ▼
            "PISTOLA DE CALOR Ref.101" → "Pistola De Calor Ref.101"

precio_unitario_texto ──► Cambiar tipo ►
    "Usando configuración regional" → Número decimal fijo → Español (España)
                                    │
                                    ▼
                        "232,29" → 232,29  (correcto)

    ⚠️ Sin este paso específico, Excel interpreta la coma como separador de
    miles (formato inglés) y "232,29" se convierte por error en 23.229.
```

### 5.3 `pedidos.csv` (~99.915 filas) — COMPLETO

```
fecha_pedido_texto ──► Columna personalizada "fecha_pedido":

    Detecta el formato según el separador y la posición del año:
    - Si tiene "-" y el primer bloque tiene 4 dígitos  → yyyy-MM-dd
    - Si tiene "-"                                     → dd-MM-yyyy
    - Si tiene "/" y el último bloque tiene 4 dígitos   → dd/MM/yyyy
    - Si tiene "/" y el último bloque tiene 2 dígitos   → dd/MM/yy
    - Si no calza en ningún patrón, o la fecha no existe
      en el calendario (ej. 31/02/2025)                → null

    Resultado: 97.955 fechas válidas / 1.960 inválidas (1,96%)

cantidad_texto ──► Columna personalizada "Cantidad":

    Intenta convertir a número con Number.FromText().
    Si falla (texto como "diez", "n/a", "-") o si el número
    es negativo o cero → null. Si es válido y positivo → el número.

    Resultado: 98.494 válidas / 1.511 inválidas (1,51%)

precio_venta_unitario_texto ──► Cambiar tipo ►
    "Usando configuración regional" → Número decimal fijo → Español (España)
    (mismo procedimiento que en productos.csv)

moneda ──► Columna personalizada "moneda_valida":
    if [moneda] = "EUR" then "Válido" else "Revisar"

    Resultado: 98.957 Válido / 958 Revisar (0,96%)

vendedor_id ──► SIN TOCAR a propósito.
    Los valores vacíos en Castellón, Murcia y Málaga no son un error de
    datos — son el patrón de "whitespace regional" que el análisis debe
    detectar más adelante (clientes activos sin comercial asignado).
```

---

## 6. Errores encontrados durante el proyecto y cómo se resolvieron

Estos errores forman parte del aprendizaje y son útiles para entender cómo
funciona Power Query "por dentro":

1. **Espacio en blanco no reconocido en "Reemplazar valores":** al intentar
   quitar el espacio en medio de un NIF (ej. "W 50446607"), escribir un
   espacio directamente en el campo del diálogo no siempre se registra.
   Solución: editar el paso directamente en la barra de fórmulas M, escribiendo
   un espacio real entre comillas (`" "`), o usando el código `#(sp)` **dentro
   de la fórmula M** (no dentro del cuadro de diálogo, ahí se toma como texto
   literal).

2. **Editar la barra de fórmulas grande en vez del cuadro de "Columna
   personalizada":** al reabrir un paso con el ⚙️, la ventana que aparece
   tiene un cuadro de fórmula acotado (solo la lógica de la columna). Si en
   cambio se edita la barra de fórmulas grande de arriba, se puede borrar por
   error el `Table.AddColumn(tabla, "nombre", each ...)` que "envuelve" esa
   lógica, dejando una expresión inválida que rompe el paso.

3. **El paso "Origen" graba un número fijo de columnas:** la conexión a un
   CSV guarda `Columns = N` en el momento de crearse. Si después se reemplaza
   el archivo fuente por una versión con distinta cantidad de columnas (por
   ejemplo, al quitar una columna "respuesta"), la conexión vieja queda
   desalineada y hay que **eliminar la consulta y crearla de nuevo**, no
   alcanza con "Actualizar".

4. **Los archivos que edita Claude viven en su propio entorno, no en la Mac
   del usuario:** cualquier corrección a un CSV hecha por Claude debe
   descargarse desde el chat y copiarse manualmente a la carpeta del proyecto
   (con `cp` en Terminal es más confiable que arrastrar en Finder, que puede
   dejar duplicados o crear archivos con extensión equivocada como `.numbers`).

5. **Auto-detección de tipo de columna interpreta mal los decimales:** si una
   columna de texto con decimales en formato español (coma) se convierte con
   el botón normal de "Tipo de datos", Power Query puede interpretar la coma
   como separador de miles (formato inglés), corrompiendo el valor
   (`"232,29"` → `23229`). Solución: usar siempre **Cambiar tipo → "Usando
   configuración regional" → Español (España)**.

6. **`Number.FromText` sobre texto no numérico rompe toda la columna:**
   si se aplica sin protección sobre valores como `"diez"` o `"n/a"`, Power
   Query no devuelve un error silencioso — puede propagar "Error" a la
   columna entera. Hay que envolver la conversión en `try ... otherwise null`.

7. **Una columna detectada automáticamente como número puede perder datos
   antes de intervenir:** si el CSV tiene una columna con texto mezclado con
   números (ej. `cantidad_texto` con "diez" y "150"), y Power Query la detecta
   como tipo numérico al cargarla, los valores no numéricos se convierten
   directamente en "Error" **dentro de la celda original**, antes de aplicar
   ninguna limpieza. Solución: forzar esa columna a tipo **texto** en el paso
   "Tipo de columna cambiado" (editando `Table.TransformColumnTypes`), y
   recién ahí aplicar la lógica de conversión segura.

---

## 7. Decisiones tomadas y por qué

- **Distribuidor industrial "general"** (metal + plástico + componentes) en
  vez de exclusivamente plástico, para que el proyecto demuestre dominio del
  sector sin ser obviamente dirigido a un proceso de selección puntual.
- **Columnas "solución" separadas en un archivo privado**
  (`SOLO_PARA_TI_validacion_no_subir.xlsx`, nunca subido a GitHub), para que
  el dataset de trabajo sea genuinamente sucio y el ejercicio de limpieza real.
- **Errores no se "corrigen a ciegas":** en cada columna problemática (NIF,
  email, teléfono, moneda, fecha, cantidad) se optó por crear una columna de
  validación en vez de intentar adivinar o reparar el dato original. Esto es
  más honesto analíticamente y es una práctica que se puede explicar bien en
  una entrevista.
- **`vendedor_id` se deja sin tocar** en las provincias sin cobertura — no es
  un dato faltante que haya que "arreglar", es el hallazgo de negocio en sí.

---

## 8. Próximos pasos

- [x] Generar dataset sintético
- [x] Limpieza de `clientes.csv`
- [x] Limpieza de `productos.csv`
- [x] Limpieza de `pedidos.csv`
- [ ] Análisis exploratorio con SQL
- [ ] Detección de las 5 oportunidades de negocio (churn, alto margen
      desatendido, gap cross-selling, fuga de margen por precio, whitespace
      regional)
- [ ] Dashboard en Power BI (VM Windows)
- [ ] README con metodología transparente
- [ ] Crear repositorio en GitHub (`proyecto6-analisis-comercial-industrial`) — al final
- [ ] Publicación en portfolio y LinkedIn
