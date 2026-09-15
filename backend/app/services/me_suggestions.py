"""Repertorio de curiosidades para arrancar («Islas para empezar»).

Eran cinco fijas, así que la pantalla de inicio del niño era idéntica en cada
visita. Ahora se sirve una muestra distinta cada vez: el repertorio es amplio y
abarca las cinco materias, para que ningún día parezca el anterior.
"""
import random

CUANTAS = 5

POOL: list[dict[str, str]] = [
    # Ciencia y naturaleza
    {"curiosity": "¿Por qué flotan los barcos?", "emoji": "⛵"},
    {"curiosity": "¿Por qué llueve?", "emoji": "🌧️"},
    {"curiosity": "¿Cómo vuelan los aviones?", "emoji": "✈️"},
    {"curiosity": "¿Por qué brillan las estrellas?", "emoji": "⭐"},
    {"curiosity": "¿Cómo nacen los volcanes?", "emoji": "🌋"},
    {"curiosity": "¿Por qué el cielo es azul?", "emoji": "🌤️"},
    {"curiosity": "¿Cómo hacen miel las abejas?", "emoji": "🐝"},
    {"curiosity": "¿Por qué los gatos ronronean?", "emoji": "🐱"},
    {"curiosity": "¿Dónde va el agua cuando se seca un charco?", "emoji": "💧"},
    {"curiosity": "¿Por qué tenemos hipo?", "emoji": "😮"},
    {"curiosity": "¿Cómo duermen los delfines?", "emoji": "🐬"},
    {"curiosity": "¿Por qué las hojas se vuelven naranjas?", "emoji": "🍂"},
    # Espacio
    {"curiosity": "¿Por qué la Luna cambia de forma?", "emoji": "🌙"},
    {"curiosity": "¿Qué hay dentro de un agujero negro?", "emoji": "🕳️"},
    {"curiosity": "¿Se puede saltar en la Luna?", "emoji": "🚀"},
    # Historia y cultura
    {"curiosity": "¿Cómo se construyeron las pirámides?", "emoji": "🔺"},
    {"curiosity": "¿Quién inventó la escritura?", "emoji": "📜"},
    {"curiosity": "¿Cómo era la vida de un caballero?", "emoji": "🏰"},
    {"curiosity": "¿Por qué hay países con idiomas distintos?", "emoji": "🗺️"},
    # Matemáticas
    {"curiosity": "¿Por qué el cero es tan importante?", "emoji": "0️⃣"},
    {"curiosity": "¿Existe el número más grande del mundo?", "emoji": "🔢"},
    {"curiosity": "¿Por qué la pizza se corta en triángulos?", "emoji": "🍕"},
    # Arte y música
    {"curiosity": "¿Por qué la música nos pone contentos?", "emoji": "🎵"},
    {"curiosity": "¿Cómo se mezclan los colores?", "emoji": "🎨"},
    {"curiosity": "¿Quién decidió cómo suena cada instrumento?", "emoji": "🎻"},
]


def sample(cuantas: int = CUANTAS) -> list[dict[str, str]]:
    """Una muestra distinta en cada visita, sin repetidas dentro del lote."""
    return random.sample(POOL, min(cuantas, len(POOL)))
