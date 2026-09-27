"""Contador de intentos: ventana deslizante en memoria del proceso.

Se prueba con un reloj falso para que el deslizamiento de la ventana no dependa
de esperas reales: un test que duerme 15 minutos no lo ejecuta nadie.
"""

import threading

from app.services import rate_limit
from app.services.rate_limit import Limitador


class RelojFalso:
    def __init__(self) -> None:
        self.ahora = 1000.0

    def __call__(self) -> float:
        return self.ahora

    def avanza(self, segundos: float) -> None:
        self.ahora += segundos


def test_allows_attempts_below_the_limit():
    limitador = Limitador(reloj=RelojFalso())
    assert limitador.consumir("ip:1.2.3.4", limite=3, ventana=60) is None
    assert limitador.consumir("ip:1.2.3.4", limite=3, ventana=60) is None
    assert limitador.consumir("ip:1.2.3.4", limite=3, ventana=60) is None


def test_blocks_the_attempt_that_exceeds_the_limit():
    limitador = Limitador(reloj=RelojFalso())
    for _ in range(3):
        limitador.consumir("ip:1.2.3.4", limite=3, ventana=60)
    espera = limitador.consumir("ip:1.2.3.4", limite=3, ventana=60)
    assert espera is not None and espera > 0


def test_window_slides_and_frees_slots():
    reloj = RelojFalso()
    limitador = Limitador(reloj=reloj)
    for _ in range(3):
        limitador.consumir("ip:1.2.3.4", limite=3, ventana=60)
    reloj.avanza(61)
    assert limitador.consumir("ip:1.2.3.4", limite=3, ventana=60) is None


def test_retry_after_counts_down_as_the_window_advances():
    reloj = RelojFalso()
    limitador = Limitador(reloj=reloj)
    for _ in range(2):
        limitador.consumir("k", limite=2, ventana=60)
    primera = limitador.consumir("k", limite=2, ventana=60)
    reloj.avanza(20)
    segunda = limitador.consumir("k", limite=2, ventana=60)
    assert primera is not None and segunda is not None
    assert segunda < primera


def test_keys_are_independent():
    limitador = Limitador(reloj=RelojFalso())
    for _ in range(2):
        limitador.consumir("ip:1.1.1.1", limite=2, ventana=60)
    assert limitador.consumir("ip:2.2.2.2", limite=2, ventana=60) is None


def test_forgetting_a_key_resets_its_counter():
    # Base del reset tras un login correcto: unas credenciales demostradas
    # válidas no son fuerza bruta, y una familia con varios dispositivos no
    # debe autobloquearse.
    limitador = Limitador(reloj=RelojFalso())
    for _ in range(2):
        limitador.consumir("cuenta:ana@x.com", limite=2, ventana=60)
    limitador.olvidar("cuenta:ana@x.com")
    assert limitador.consumir("cuenta:ana@x.com", limite=2, ventana=60) is None


def test_clearing_the_store_removes_every_counter():
    # Es lo que usa el fixture autouse de la suite: sin esto, los contadores
    # se acumularían entre tests y habría fallos según el orden de ejecución.
    limitador = Limitador(reloj=RelojFalso())
    for _ in range(2):
        limitador.consumir("k", limite=2, ventana=60)
    limitador.limpiar()
    assert limitador.consumir("k", limite=2, ventana=60) is None


def test_counter_is_consistent_under_concurrent_threads():
    # Los endpoints son `def`, así que uvicorn los corre en su threadpool: hay
    # concurrencia real sobre el diccionario. Sin cerrojo, se cuela alguno.
    limitador = Limitador(reloj=RelojFalso())
    aceptados = []
    barrera = threading.Barrier(20)

    def intentar() -> None:
        barrera.wait()
        if limitador.consumir("k", limite=5, ventana=60) is None:
            aceptados.append(1)

    hilos = [threading.Thread(target=intentar) for _ in range(20)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    assert len(aceptados) == 5


def test_store_evicts_the_least_recently_used_key_when_full(monkeypatch):
    # Sin tope, quien rote identificadores haría crecer el diccionario hasta
    # agotar la memoria del contenedor.
    monkeypatch.setattr(rate_limit, "MAX_CLAVES", 3)
    limitador = Limitador(reloj=RelojFalso())
    for i in range(4):
        limitador.consumir(f"k{i}", limite=1, ventana=60)
    # La más antigua salió; las tres últimas conservan su contador agotado.
    assert limitador.consumir("k0", limite=1, ventana=60) is None
    assert limitador.consumir("k3", limite=1, ventana=60) is not None
