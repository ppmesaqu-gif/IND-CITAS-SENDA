# OpsFlow · Qué creo que nos falta por completar

Análisis de Jarvis para Pedro · 25/10/2026 (actualizado 26/10/2026 · app en versión 2026.10.26.0852)
Se comparte por partes, una por mensaje. Partes ya enviadas: **1**. Siguiente: 2.

---

## Parte 1 · Lo que no se puede dejar para después

**Lo más importante: lo que corregimos no sirve hasta que esté en los celulares.**

1. **Subir el paquete `OPSFLOW_PARA_GITHUB_0852.zip` a GitHub.** Borra `index.html` y `sw.js` del repositorio, sube los 7 archivos del zip y espera 2 o 3 minutos. El QR no cambia. Este paquete cubre todo lo anterior (1538 y 1550) y suma: formatos anclados a cada proceso, sobrantes valorizados y datos nuevos de estaciones y clientes. *(El 1550 queda reemplazado.)*
2. **Probar el proceso 7 en un celular real, con una planilla real del día.** Todas nuestras pruebas corren en un navegador simulado. El problema del escáner en sobrantes lo encontraste tú en la bodega, no las pruebas. Eso dice todo: la cámara real, WhatsApp y «Compartir» solo se validan en campo. Una prueba de 30 minutos, un Android y un iPhone, con un auxiliar que no haya visto la app.
3. **Actualizar las tablas de rutas y estaciones.** Vienen de enero (el 26/10 sumamos 6 SKU de estación y 3 clientes del libro de septiembre). En el ejemplo del 15/10, 37 de 63 clientes salieron «sin ruta». La app los deja asignar a mano y aprende, pero cada día sin tabla al día es trabajo manual tuyo. Lo mejor es una sola carga con el listado vigente de clientes y ruta que tenga Logística.

**Mi crítica, como amigo:** en pocos días la app ganó análisis del cierre, cruces, tablero, manual y sobrantes en plata. Lo que aún no tiene es una semana de uso real. Hasta que no haya datos de campo, cada función nueva es una apuesta. Mi recomendación: congelar la versión 0852 durante una semana y solo corregir lo que el campo reporte.

---

## Parte 2 · Decisiones que son tuyas

1. **Pantallas CÍCLICO e ISLA sin pestaña.** El código existe y ahora está protegido por pruebas (21 y 35 comprobaciones), pero no hay pestaña que las abra, y los límites de isla están fijos en el código. Decide: ¿se habilitan o se retiran? Si se habilitan, los límites deben poder editarse.
2. **La clave.** Es «Alpina» más el código del centro. Quien conozca el patrón puede probar con otros centros. Si los datos de un centro no deben verlos otros, hace falta una clave propia por centro. Si no importa, se deja.
3. **El QR y la dirección de GitHub.** El celular muestra la dirección un instante. Para ocultar el nombre de usuario se necesita un dominio propio de Alpina. Es trámite con TI, no de código.
4. **Respaldo.** Lo que no se ha enviado vive solo en el celular. Si se borra el navegador, se pierde. Propongo una regla: «RESPALDO JSON» al cerrar la jornada, y envío del reporte siempre el mismo día.

---

## Parte 3 · Papeles y capacitación

1. **Manual de uso del 23/10 desactualizado.** No incluye análisis del cierre, zona, ajustes manuales, sobrante en plata ni los errores «Toque ENVIAR» y «elija familia y subfamilia». Hay que rehacerlo, pero corto: una hoja por rol (auxiliar, supervisor), no 47 páginas. El libro nuevo ya es la referencia completa.
2. **Guías QR y ejemplos al día.** Las imágenes de ejemplo deben mostrar la última versión.
3. **Hablador con QR.** Todavía no existe en la operación. La app ya lee uno con SKU, lote y vencimiento. Mientras no exista, se escanea el producto y se digita el lote.
4. **Capacitación.** Sesión de 20 minutos con los auxiliares: instalar por QR, contar, anotar faltante y sobrante, cerrar. Con una lista de chequeo que ellos mismos marquen.

---

## Parte 4 · Calidad técnica (mi parte)

1. **Pruebas: resuelto el 26/10.** Las siete pruebas viejas que fallaban ya se actualizaron al diseño actual (sin borrar cobertura) y las de entorno (cámara, login, compartir en Android, foto, PDF de bajas) ahora corren solas. Se agregaron pruebas de formatos por proceso y de sobrantes valorizados. Hoy: **52 pruebas, 0 con fallas**, con un solo comando (`bash tests/correr_todo.sh ../dist/INVENTARIO_ALPINA.html`). Lo que sigue: correr ese comando antes de cada entrega, y no entregar si algo sale en rojo.
2. **Un solo archivo de 1,8 MB y 9.000 líneas.** Funciona y es lo que permite el QR y el modo sin internet. El riesgo es que un cambio en un lado rompa otro. La batería de pruebas es la defensa, y ahora está en verde.
3. **Escala.** La app corre en el celular y se sirve como archivo estático: para más de 1.000 usuarios no es el cuello de botella. Lo es el tablero de tareas (Google Sheets + Apps Script): tiene cuotas diarias. Si crece a muchos centros, habría que pasarlo a una base de datos de verdad (Supabase).
4. **Pendientes técnicos pequeños (no hechos):** valorar los TROCADOS (pidió vs llegó), sembrar placas desde el libro de faltantes y sobrantes, y decidir si la pantalla de conteo del 7 vuelve a tener un panel de campos (hoy es siempre «a ciegas»).

---

## Parte 5 · El tablero de tareas por WhatsApp

1. **Servicio no oficial.** Los avisos salen por Whapi.cloud, que no es la API oficial de WhatsApp. Puede bloquear el número y no es lo más seguro para datos de Alpina. Conviene confirmar con TI que lo aceptan.
2. **Acceso.** TI solo permite entrar a usuarios Alpina. Hay que definir quién administra el tablero y quién lo reemplaza si no está.
3. **Confirmación «OK 15» en el grupo.** Funciona mientras todos escriban igual. Falta ver cómo responde con errores de digitación, y qué pasa si dos personas confirman la misma tarea.

---

## Parte 6 · Tú

1. **Tu tiempo.** Hay cambios hechos a las 23:20. Un negocio bien diseñado no depende de que lo arregles de noche. Cuando algo falle en campo, anótalo y revísalo en tu horario de trabajo.
2. **Delegar el soporte.** Elige un auxiliar «líder de la app» por turno. Cuando él pueda resolver el 80 % de las dudas, tú recuperas horas.
3. **Qué medir en un mes.** Cuántos auxiliares la usan solos, cuántos reportes salen el mismo día y cuánto tardas en cerrar una jornada. Si esos tres mejoran, la app cumplió.
