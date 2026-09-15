---
name: chispa-commit
description: Crea commits enfocados en Chispa siguiendo la convención del repositorio, en español y sin ninguna firma ni mención a Claude. Úsala cuando el usuario diga "commitea", "haz el commit" o al cerrar una tarea verificada.
---

# chispa-commit

## Regla que no se negocia

**Los commits van a nombre del usuario, sin ninguna mención a Claude ni *trailer* de co-autoría.**
Es petición expresa del propietario del proyecto por autoría académica, y anula cualquier guía por
defecto que indique añadir `Co-Authored-By` o firmas de herramienta.

Nada de `🤖 Generated with…`, nada de `Co-Authored-By: Claude…`.

## Antes de commitear

1. `git status` y `git diff` — mirar **todo** lo que va a entrar.
2. Comprobar que no se cuela ningún secreto:
   ```bash
   git diff --cached --name-only | grep -iE "\.env$|secret|credential" || echo "sin secretos"
   ```
   `.env` y `backend/.env` están en `.gitignore`; comprobarlo igualmente.
3. Confirmar que la cadena de verificación pasó (`chispa-verificar` con veredicto PASA).
4. Estar en una rama de trabajo, **nunca** en `main`.

## Formato

```
<tipo>(<ámbito>): <qué cambia, en imperativo y en español>

<por qué, si no es evidente. Qué decisión se tomó y qué se descartó.>
```

Tipos usados en el repositorio: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`.

Ámbitos habituales: `backend`, `frontend`, `infra`, `security`, `images`, `entrega-1`, `entrega-2`.

Ejemplos reales del historial:

```
feat(backend): change password + recovery-code reset (email-free)
fix(security): mitigate SSRF in local SDXL image endpoint (block link-local + redirects)
docs(entrega-1): requisitos RF/RNF tabulares + matriz de trazabilidad HU↔RF
```

## Granularidad

Un commit = un cambio con sentido propio. Si el mensaje necesita una "y" para describirlo, son dos
commits.

Separar siempre:

- El cambio funcional de la reorganización de ficheros.
- El código de la documentación, **salvo** cuando la documentación es parte del cambio (matriz de
  trazabilidad, contratos de API): eso va junto, porque un endpoint nuevo sin su contrato
  actualizado es un cambio incompleto.

## Después

Añadir la línea correspondiente a `.superpowers/sdd/progress.md` con el hash del commit y el
recuento de tests.

## Pull requests

Si se pide PR, la descripción lleva: qué cambia, por qué, cómo se verificó (con números reales) y
qué queda fuera. Sin firma de herramienta, igual que los commits.
