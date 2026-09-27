"""Límite de intentos por ventana deslizante, en memoria del proceso.

Chispa se despliega como un único proceso de uvicorn (ver `docker-entrypoint.sh`),
así que un contador en memoria es suficiente y evita añadir Redis al compose. La
contrapartida está documentada en ADR-008: los contadores mueren al reiniciar el
contenedor y dejan de ser un control válido si algún día hay varios procesos.
"""

import threading
import time
from collections import OrderedDict, deque
from collections.abc import Callable

# Tope de claves vivas. Sin él, un atacante que rote identificadores haría crecer
# el diccionario sin freno hasta agotar la memoria del contenedor.
MAX_CLAVES = 10_000


class Limitador:
    def __init__(self, reloj: Callable[[], float] = time.monotonic) -> None:
        self._reloj = reloj
        # OrderedDict para poder desalojar la clave menos usada recientemente.
        self._intentos: OrderedDict[str, deque[float]] = OrderedDict()
        # Los endpoints son `def`, luego uvicorn los ejecuta en su threadpool:
        # hay concurrencia real entre hilos sobre este diccionario.
        self._cerrojo = threading.Lock()

    def consumir(self, clave: str, limite: int, ventana: float) -> float | None:
        """Registra un intento. Devuelve los segundos de espera si toca cortar."""
        ahora = self._reloj()
        with self._cerrojo:
            marcas = self._intentos.get(clave)
            if marcas is None:
                marcas = deque()
                self._intentos[clave] = marcas
            self._intentos.move_to_end(clave)
            while marcas and ahora - marcas[0] >= ventana:
                marcas.popleft()
            if len(marcas) >= limite:
                return ventana - (ahora - marcas[0])
            marcas.append(ahora)
            self._desalojar_si_hace_falta()
            return None

    def olvidar(self, clave: str) -> None:
        """Borra el contador de una clave (credenciales demostradas válidas)."""
        with self._cerrojo:
            self._intentos.pop(clave, None)

    def limpiar(self) -> None:
        with self._cerrojo:
            self._intentos.clear()

    def _desalojar_si_hace_falta(self) -> None:
        while len(self._intentos) > MAX_CLAVES:
            self._intentos.popitem(last=False)


limitador = Limitador()
