# App de inventario con escaneo de código de barras

- Conversación: https://claude.ai/chat/73886556-80fa-4259-9a90-51bd21c4aa52
- Última actualización: 2026-10-31

## Resumen (tal como lo guarda el historial; el sistema lo entregó cortado al final)

**Conversation overview**

Pedro Mesa (CEDI Entrerríos, Alpina, centro 4803) directs development of "ALPINA OpsFlow," a PWA inventory app with 7 processes, published on GitHub Pages. Source code lives in `/home/claude/work/inventario-alpina/` (app.js, head.html, build.py, assets/, tests/); outputs go to `/mnt/attach/outputs/`. Pedro communicates in Spanish, prefers surgical responses, and uses "arregla" to mean "just deliver the file without explaining."

**[DECISION] Proceso 7 ciego-primero (26/10):** All recibo (by placa, plus sobrante returns) happens blind during the day; the Amovil Excel is loaded only at jornada close to cross-reference. This replaced the prior "load Excel first" flow. Infografía and manual updated accordingly; new end-to-end test `test_p7_ciego_primero.js` added (all passing).

**[TOOL USE] Debugging and new features (26/10):** Fixed dead `btnIrIsla` button error; made Cíclico por familia (proceso 3) and Isla (proceso 4) panels appear automatically in ESCANEO without tabs/buttons (`panelesAuto()`). Fixed real bug: "corta fecha · seco" threshold showed 40 instead of 60. Added small-text cubeta/embalaje line below SKU/description (`embLinea()`). Test suite grew from 52→56→57→58 tests, all passing.

**[DOCUMENT] Mind maps (7 procesos):** Generated via `/home/claude/work/mapas/build_mapas.py` + Playwright rendering. Combined PDF `OPSFLOW_MAPAS_MENTALES_LOS_7_PROCESOS.pdf`.

**[CRITICAL CORRECTION] Proceso 6 (27/10):** Pedro flagged that the video/mapa wrongly merged proceso 6 (cíclico por ubicación, whose essence is the hablador with photo/QR) with WhatsApp task-confirmation features (a separate facturación development). Corrected across video, mapa 6, manual, and guía: new rama "LA FOTO Y SU LÍMITE" explains photo-based lote/fecha reading wasn't achievable (resolution), hence the QR-on-hablador pilot; WhatsApp confirmation rama removed. **[DECISION]** Entire "tablero de tareas" scene also removed from video per Pedro's follow-up complaint that it left presentation looking "incomplete."

**[CODE] Presentation video (OPSFLOW_VIDEO_PRESENTACION.mp4, 12:00, no audio):** Built in `/home/claude/work/video/motor/index.html` using scene-based HTML/JS with deterministic clock, phone mockup with real app screenshots, zoomable report images. Content: portada, qué es, cómo se entra, 7 procesos, QR install, each proceso demo'd with real screenshots, each proceso's actual generated reports (Excel/PDF) shown large with zoom to key areas, ayudas comunes, cómo se comparte, lo positivo, cifras, hoja de ruta (propuesta vs decisión table), cierre. Went through multiple corrected versions as Pedro caught errors.

**[DOCUMENT] Guía del orador** (Claude Docs, https://claude.ai/artifact/FUmJpLKAW8SdQDSypdvwVf): checklist, minute-by-minute 30-min plan, scene-by-scene talking points with video timestamps, live demo script with plan B, tough Q&amp;A with honest answers, decisión-Alpina vs propuesta table, qué no mostrar. Updated multiple times to match video corrections (durations, removed tareas references).

**[DOCUMENT] Libreto para grabar voz** (Claude Docs, https://claude.ai/artifact/HYVNQeNoJfMkD6Yy9iS7hr): Pedro requested a script so he could record his own voice over the video (via Claude or another tool). Built with exact video timestamps, "en pantalla" / "tú dices" columns per scene, 1,338 words paced to video duration. Companion file `OPSFLOW_VIDEO_GUIA_PARA_GRABAR.mp4` overlays the script text at the bottom with a clock (recording aid only, not for delivery) plus `OPSFLOW_LIBRETO.srt`.

**[DOCUMENT] Micro presentación
