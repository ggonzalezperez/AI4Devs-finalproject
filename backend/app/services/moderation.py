import re
import unicodedata


class ModerationError(Exception):
    pass


# Lista mínima de bloqueo (placeholder). Un servicio real de moderación
# implementará esta misma función con más cobertura.
#
# Dos listas, porque ninguna estrategia sola sirve:
#
# - Buscar por SUBCADENA bloqueaba curiosidades legítimas de un niño:
#   "arma" cortaba "armadura", "armario", "armazón" y "Armada Invencible".
# - Buscar solo PALABRA EXACTA abría el hueco contrario: se colaban "matarte",
#   "drogadicto", "suicidar" o "pornográficos", que la versión anterior sí
#   paraba.
#
# Así que las raíces cuyas derivadas son todas problemáticas se comparan por
# PREFIJO, y las que colisionan con palabras inocentes, por palabra COMPLETA.

# Prefijos: ninguna palabra castellana inocente empieza por estas raíces.
_RAICES = (
    "suicid",    # suicidio, suicida, suicidarse, suicidas
    "drog",      # droga, drogas, drogar, drogadicto
    "porno",     # porno, pornografía, pornográfico
    "matar",     # matar, matarte, matarnos, matarlos
    "asesin",    # asesinar, asesinato, asesino
    "violen",    # violencia, violento, violentos
    "sexual",    # sexual, sexuales, sexualidad
)

# Palabra completa: su raíz colisiona con vocabulario inocente.
_EXACTAS = frozenset({"arma", "armas", "armamento", "sexo"})

_PALABRA = re.compile(r"[a-z0-9]+")


def _normalize(text: str) -> str:
    """Minúsculas y sin tildes, para que «PORNOGRAFÍA» iguale a «pornografia»."""
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def check_curiosity(text: str) -> None:
    palabras = _PALABRA.findall(_normalize(text))
    for palabra in palabras:
        if palabra in _EXACTAS or palabra.startswith(_RAICES):
            raise ModerationError("Esta pregunta es mejor verla con un adulto.")
