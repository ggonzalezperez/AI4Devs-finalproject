"""Resolución de la IP del cliente para el límite de intentos.

Detrás de nginx y del túnel, `request.client.host` es la IP del contenedor: sin
esto, todo el mundo compartiría cubo. Y leer cabeceras a ciegas sería peor, así
que solo se hace cuando el despliegue declara que hay un proxy de confianza.
"""

from starlette.requests import Request

from app.deps import ip_cliente


def _request(cabeceras: dict[str, str] | None = None, peer: str | None = "10.0.0.9") -> Request:
    scope = {
        "type": "http",
        "headers": [
            (k.lower().encode(), v.encode()) for k, v in (cabeceras or {}).items()
        ],
        "client": (peer, 12345) if peer else None,
    }
    return Request(scope)


def test_uses_the_socket_peer_when_no_header_is_configured():
    # Cabecera falsificada presente pero nadie declaró proxy: se ignora.
    peticion = _request({"CF-Connecting-IP": "1.2.3.4"})
    assert ip_cliente(peticion, cabecera=None) == "10.0.0.9"


def test_reads_the_configured_header_when_present():
    peticion = _request({"CF-Connecting-IP": "1.2.3.4"})
    assert ip_cliente(peticion, cabecera="CF-Connecting-IP") == "1.2.3.4"


def test_falls_back_to_the_peer_when_the_configured_header_is_absent():
    # Acceso directo por la LAN al puerto 8000, sin pasar por el túnel.
    assert ip_cliente(_request(), cabecera="CF-Connecting-IP") == "10.0.0.9"


def test_ignores_a_header_value_that_is_not_an_ip_address():
    peticion = _request({"CF-Connecting-IP": "no-soy-una-ip"})
    assert ip_cliente(peticion, cabecera="CF-Connecting-IP") == "10.0.0.9"


def test_takes_the_first_entry_of_a_forwarded_for_chain():
    peticion = _request({"X-Forwarded-For": "1.2.3.4, 10.0.0.1"})
    assert ip_cliente(peticion, cabecera="X-Forwarded-For") == "1.2.3.4"


def test_a_request_without_peer_falls_back_to_a_single_bucket():
    assert ip_cliente(_request(peer=None), cabecera=None) == "desconocida"
