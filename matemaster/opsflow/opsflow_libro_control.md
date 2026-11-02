# OpsFlow · Libro de la app: control y actualización rápida

Uso: Pedro dice «actualiza el libro». Solo entonces se actualiza. No hay tareas automáticas ni horarios. Meta: minutos, no horas.

## Dónde está
- Libro (Docs): https://claude.ai/artifact/KVMqcY6N9qWJCZarwA5tGE
- Contenedor `{"kind":"project","id":"95ba29d4-f884-4ac6-accb-36e42e78c64f"}`, archivo `60ec3c9d-3e25`, cuerpo `d8f0cc33-2227`, motor `prose`.
- Edición actual: 1.1 (25/10/2026). Describe la app 2026.10.25.1550. 14 capítulos.
- Pendientes aún no reflejados en el libro: ninguno a esta fecha.

## Pasos de «Actualiza el libro»
1. Saber qué cambió desde la versión de la tabla «Esta edición» (cap. 14). Fuente: `README.md` del código (carpeta `inventario-alpina`, dentro de `FUENTE_INVENTARIO_ALPINA.zip`; secciones nuevas al final) o lo que Pedro cuente. Sin el código no se inventa: se pregunta qué cambió.
2. Ubicar los capítulos afectados con el mapa de abajo. Buscar la frase vieja con `read` + `search` (texto o regex Rust, sin `\u`).
3. Editar solo esas frases: `update` con `{"engine":"prose","ops":[{"op":"replace","target":{"kind":"find","find":{"kind":"text","text":"frase vieja"}},"with":{"from":{"kind":"inline","content":"frase nueva"},"as":"text"}}]}`. Para agregar bloques: `op:"insert"`, `side:"after"`, `target:{"kind":"blocks","ids":[id]}`, `source:{from:{kind:"inline",content},as:"markdown"}` (insert usa `source`, replace usa `with`). Guiones bajos en markdown: `\_`.
4. Cap. 14: agregar fila ARRIBA en «Registro de cambios» (fecha, qué cambió, capítulos), subir la edición y la versión de la app en la tabla «Esta edición» y en la línea bajo el título («Edición … · describe la app en su versión …»).
5. PDF: `mcp__Claude_Docs__create` con `object:"blob"`, `payload {from:{object:"file",id:"60ec3c9d-3e25"},format:"pdf"}` → devuelve un asset; `Artifact read` con la url del libro, `path=<asset>`, `out_dir=/mnt/attach/outputs`; luego SendUserFile. (El export inline falla por tamaño.)
6. Estilo: español, trato «tú», frases de menos de 25 palabras, sin emoji, sin ids técnicos en el texto.

## Mapa: qué cambió en la app → capítulo
- Entrada, clave, instalación, sin internet, actualización → 2 y 12
- Escaneo, previa, grabado, formatos comunes → 3 y 10
- Procesos 1 y 2 → 4 · Procesos 3 y 6 → 5 · Procesos 4 y 5 → 6
- Proceso 7: preparar, Excel, contar → 7
- Proceso 7: faltante/sobrante/trocado, cruce, finalizar, reportes y envío → 8
- Proceso 7: análisis del cierre (rutas, estaciones, imágenes, Excel, ajustes manuales) → 9
- Datos maestros y reglas (costos, capacidades, familias, EAN) → 11
- Fallas, límites y glosario → 13
- Versiones y cambios → 14

## Hechos que no se deben afirmar sin revisar el código
Costos visibles (proceso 7 siempre los muestra), BORRAR GRABADO (solo ese proceso), RESPALDO JSON, CSV separado por `;`, respaldo de envíos (pestaña ADMIN), clave = «Alpina» + código del centro.
