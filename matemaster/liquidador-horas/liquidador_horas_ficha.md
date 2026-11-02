# LIQUIDADOR_HORAS_COLOMBIA — ficha del proyecto
Actualizada: 2026-11-01 (noche)

## Qué es
App HTML de un solo archivo (sin internet, sin instalar) para liquidar HORAS de nómina de personal temporal (Adecco) y directo (SAP/ALP) bajo la ley laboral colombiana. Por ahora solo horas; el pago en dinero y el recibo vienen después. Meta: poder venderla a otras empresas, con esquemas de liquidación configurables.

## Versión actual (1 nov 2026) — archivo: LIQUIDADOR_HORAS_COLOMBIA.html (~1 MB)
Fusión de las dos conversaciones del proyecto. Trae:
- Navegación en 3 pasos: 1 Cargar · 2 Conciliar · 3 Pagar (+ menú "Más": todos los turnos, alertas, personal, planes, indicadores, resumen, ajustes).
- Cargar: subir Excel/CSV (busca sola la mejor hoja y la fila de títulos; el archivo completo de octubre carga en ~7 s), digitación rápida, ventana "Digitar" por día/mes, marcación propia (cédula, QR, foto).
- Conciliar: una persona, sus días del mes, casillas de hora en 24 h, color por estado, aprobar por día / por cédula / todas las listas, novedades, INV/PROG. Tras subir un archivo la app salta sola aquí, con el mes ya elegido.
- Calendario por cédula con horario SAP sugerido, nota "JND 8.5HR", etiqueta "Reducc. X h" y reporte del grupo del mes.
- Tabla de 17 turnos de temporales (T1–T17) además de Turno 1 y 2.
- Esquemas de jornada: SAP (directos), tabla ADECCO (temporales), otras empresas.
- Alertas: bajo jornada, techo diario, jornada semanal 42 h, turnos cruzados.

## Regla de turnos vigente (alineada a la hoja ADECCO de la NOMINA)
- Turno 1 = 7,5 h de reloj, sin pausa (código 16). Turno 2 = 8,5 h de reloj con 1 h de pausa (código 13). La hora extra empieza al pasar ese umbral.
- Verificado: octubre 2026, 613 de 613 filas de la hoja ADECCO coinciden en horas extra.
- El instructivo de la temporal dice 8 h / 9 h: Pedro lo resuelve directamente con la temporal.

## Reducción semanal (nuevo, 1 nov 2026) — igual a la columna "REDUCC EN HRAS" del Excel
- Se acumulan las horas de RELOJ de la persona en la semana (lunes a domingo). Cuando el acumulado pasa el límite legal de la semana, el exceso lo absorben los días cortos: reducción del día = MIN(exceso acumulado, faltante del día).
- Faltante del día = turno estándar de reloj (horas + pausa del esquema) − reloj trabajado, solo si el día cierra en múltiplos de 0,5 h (6, 6,5, 7…) y trabajó al menos 6 h (son las "JND x HR" de la temporal). Se cambia en Ajustes: "Reducción: horas mínimas" y "paso" (0 = cualquier duración).
- Misma regla para temporales (T1–T17, Turno 1/2) y directos (el estándar sale del horario SAP del día). Para otra empresa usa su propio esquema.
- Es informativo: no cambia las horas extra diarias. Sale en el Calendario ("Reducc. X h") y en el detalle exportado (REDUCC EN HRAS, Faltante vs turno, Reloj acum. semana).
- Verificado contra el Excel con límite 44 h: 613 de 613 filas iguales (15 días con reducción, 14,5 h). Con el límite legal de 42 h (vigente desde 15-jul-2026): 18 h en 10 personas.
- El Excel usa 44 h en sus columnas semanales (y esas columnas tienen #REF! rotos); la app usa 42 h por la Ley 2101.
- En la hoja PERSONAL del Excel la columna Empresa dice "Directo" o "ADECCO": así se distinguen. El Excel no tiene fórmula de reducción propia para directos.

## Exceso semanal -> extras (nuevo, 1 nov 2026, decisión de Pedro)
- Respuesta de Pedro: los horarios/códigos ya traen la reducción diaria; lo que pase del código en el día es extra (sin cambio). Y lo que supere las 42 h de la semana se LIQUIDA como extra con sus recargos.
- Cómo funciona: se suman las horas ORDINARIAS trabajadas (sin pausa, sin las extras diarias) de cada persona por semana (lunes a domingo), en orden cronológico. Al pasar el límite (42 h desde 15-jul-2026, 44 h antes), esas horas dejan de ser ordinarias y pasan a extra con el recargo de la hora en que caen (diurna, nocturna, dominical o festiva). No duplica las extras diarias.
- Interruptor en Ajustes: "Lo que pase de la jornada semanal (42 h) se liquida como extra" (Sí/No). En No vuelve a como estaba (613/613 contra el Excel).
- Se ve en el Calendario (etiqueta roja "Exc. sem. X h → extra") y en el detalle exportado (Extra por exceso semanal (h), Ordinarias acum. semana (h)).
- Verificado: pruebas de 45 h (3 h al sábado), domingo completo (dominical), exceso con parte nocturna (0,5 h diurna + 2,5 h nocturna), directo 9H06 (44 h -> 2 h), semana con extras diarias (sin duplicar), límite 44 h en junio. Con datos reales (ago-oct 2026, 613 turnos): 58 de 124 personas-semana superaban 42 h ordinarias; tras la regla ninguna; extras 1.208,6 h -> 1.390,0 h (+181,4 h); ordinarias+extras se conservan turno a turno.
- Ojo para validar con la temporal: esta regla es independiente de la "Reducción semanal" (que sigue informativa). Si la temporal ya netea esas horas con la reducción, el total cambia.

## Códigos (nuevo, 1 nov 2026) — un solo campo "Código"
- Se escribe el código y la app decide sola la categoría: TEMPORALES = 1 (Turno 1, código 16), 2 (Turno 2, código 13), 13, 16, T1–T17 (o 3–17 sin la T) · DIRECTOS = cualquier código del horario SAP (183, ej. 8H06; el horario cambia según el día de la semana).
- Ojo: "1" y "2" sin T son Turno 1 y Turno 2 (como en el Excel); "T1" y "T2" son los códigos 1 y 2 de la tabla (5 h y 5 h de reloj).
- El código manda sobre cómo figure la persona: un directo con código T7 se liquida como temporal; un temporal con código 8H06 se liquida con el horario SAP. La app avisa cuando no coincide.
- Dónde se escribe: Digitar (campo "Código del turno", llena horas y turno) y Conciliar (columna "Código", azul = temporales, verde = directos). Muestra "Ley aplicada" (42 h/semana, noche 19:00, dominical 90 % desde 1-jul-2026, hora ordinaria ÷ 210 desde 15-jul-2026; antes 44 h, 80 %, ÷ 220).
- Verificado: los 17 códigos T y los 183 SAP se clasifican bien; las extras cambian según el código (misma jornada 06:00–15:00: 1→1,5 h · 2→0,5 · T4→3 · T7→2,5 · T17→0).

## Modo marcación (reforzado el 1 nov 2026)
- Turno asumido: si la persona no tiene turno habitual ni horario SAP, la app usa su turno más frecuente, o por duración (menos de 8 h → Turno 1; 8 h o más → Turno 2) y lo marca "≈ asumido" en el Calendario. Antes quedaba "Personalizado" y NO calculaba extras (pagaba de menos sin avisar). Aplica también al subir marcaciones de un archivo.
- Olvido de salida: una entrada abierta más de 16 h (se cambia en Ajustes) se da por olvidada; la siguiente marca es ENTRADA y la anterior queda pendiente "Falta marcar SALIDA". El panel del modo marcación cuenta quién está adentro y quién olvidó marcar.
- Fotos de evidencia en un almacén aparte (el guardado ya no se vuelve pesado) y se borran solas a los 60 días (Ajustes).
- Hora del equipo atrasada: se rechaza la marca. PIN: la primera vez pide uno nuevo (no 1234).
- Botón "Descargar las marcas (CSV)" para llevarlas al computador principal con Subir archivo; subir el mismo CSV dos veces no duplica.
- Pendiente de prueba real: cámara y lectura de QR en una tablet; carnés impresos.

## Qué NO se toca
- El significado de Turno 1 y Turno 2 (el Excel de Pedro liquida con ellos y le costó mucho corregir cada fórmula condicional).
- La columna "TIPO DE TURNO (1 O 2)" del Excel que exporta la app, ni su columna "REDUCCIÓN DE JORNADA" (formato de la temporal).
- Lectura de Excel con cellDates:false (con fechas reales, en zona horaria de Colombia las horas salían corridas 4 h 56 min) y con dense:true (carga 15 veces más rápida).
- Las claves T1–T17 son texto con prefijo "T" para no chocar con 1 y 2.
- El sugerido de horario SAP elige siempre el mismo código cuando varios comparten ventana (el más natural, a igualdad el de menor código).

## Verificado el 1 nov 2026
- Sintaxis de los bloques de código OK; sin errores JS al cargar.
- Archivo real completo de octubre (hoja ADECCO de ~1 millón de filas): 613 turnos, 834 filas incompletas, ~7 s.
- Importación de la hoja BASE de marcaciones crudas (fecha y hora en columnas separadas): 616 turnos.
- Conciliar con datos reales: aprobar los que cuadran (13) y todas las cédulas listas (337 días de 613), sin errores.
- Reducción: 613/613 contra el Excel (44 h); pruebas con un directo SAP y un temporal Turno 1 dan la reducción esperada.
- Exceso semanal: 11 pruebas OK; con el interruptor en No, 613/613 extras contra el Excel.
- Sugerido de horario SAP: 06:00–14:00 → 8H06, 14:00–22:00 → 8H14, 22:00–06:00 → 8H22.
- NO probado a fondo: modo marcación (kiosco/QR/foto) y carnés QR.

## Pendientes
1. RESUELTO 1-nov: el horario/código SAP es el estándar del día; lo que lo supere es extra. El exceso sobre 42 h semanales se liquida como extra (ver sección arriba).
1b. Validar con la temporal si la reducción semanal debe restarse del exceso semanal (hoy NO se resta).
2. Ejemplo que Pedro dejó a medias sobre subir Excel/CSV y que la app genere sola las vistas para corregir y liquidar (el flujo base ya funciona: sube → Conciliar con el mes elegido).
3. Paso 3 "Pagar": pago en dinero y recibo (después de cerrar horas).
4. Subir marcaciones conciliadas a SAP (transacción PTMW) — por evaluar.
5. Probar a fondo modo marcación y carnés QR.
