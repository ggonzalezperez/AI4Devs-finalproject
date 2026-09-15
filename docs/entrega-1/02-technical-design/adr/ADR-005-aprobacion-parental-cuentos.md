# ADR-005 — Aprobación parental de cuentos (máquina de estados)

**Estado:** Aceptada (fase de diseño)

## Contexto

Chispa puede generar cuentos personalizados para el niño (funcionalidad D17). Como el contenido lo produce una IA y lo consume un menor, **ningún cuento debe llegar al niño sin revisión de un adulto**. Además, cada familia solo debe ver sus propios cuentos.

## Decisión

Modelar cada cuento como una **máquina de estados** `pending → approved | rejected`:

- El **niño solo leerá** cuentos en estado `approved`.
- La **familia podrá editar el texto al aprobar** (corregir o afinar el cuento).
- El **rechazo conservará el texto original** (no se perderá lo generado; quedará como `rejected`).
- **Aislamiento entre familias**: acceder a un cuento de otra familia devolverá **404** (no se filtrará ni su existencia).

## Alternativas consideradas

- **Publicar directo** el cuento generado por IA: inseguro para un menor; salta la supervisión parental que es un requisito del producto.

## Consecuencias

- Supervisión parental garantizada: el contenido para el niño estará siempre revisado por un adulto.
- Trazabilidad: los estados `pending`/`approved`/`rejected` documentarán la decisión y conservarán el original en caso de rechazo.
- Privacidad entre familias mediante respuestas 404 en accesos cruzados.

## Componentes de diseño

- Modelo `Story` (con estado y texto original).
- Servicio de historias (`story_service`): transiciones `pending → approved | rejected`, edición al aprobar.
- Routers `/me/stories` (lectura del niño, solo `approved`) y `/family/stories` (aprobación/rechazo, aislamiento 404).
- Corresponde al requisito D17.
