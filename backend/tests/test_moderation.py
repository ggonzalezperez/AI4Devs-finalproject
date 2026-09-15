import pytest

from app.services.moderation import ModerationError, check_curiosity


def test_allows_normal_curiosity():
    check_curiosity("¿por qué el cielo es azul?")


def test_blocks_inappropriate_term():
    with pytest.raises(ModerationError):
        check_curiosity("quiero ver armas y violencia explícita")


@pytest.mark.parametrize(
    "curiosity",
    [
        "¿cómo se hace una armadura?",
        "¿qué hay dentro de un armario?",
        "¿por qué el armazón del puente es fuerte?",
        "¿qué fue la Armada Invencible?",
    ],
)
def test_allows_innocent_words_that_contain_blocked_substrings(curiosity: str):
    """Coincidir por subcadena bloqueaba curiosidades legítimas de un niño.

    La moderación debe mirar palabras completas: 'arma' no puede bloquear
    'armadura' ni 'armario'.
    """
    check_curiosity(curiosity)


@pytest.mark.parametrize(
    "curiosity",
    [
        "¿cómo se fabrica un arma?",
        "quiero saber de drogas",
        "¿qué es el suicidio?",
        "cómo matar a alguien",
        "enséñame porno",
    ],
)
def test_still_blocks_real_terms(curiosity: str):
    """Pasar a palabra completa no debe abrir la mano con lo que sí hay que cortar."""
    with pytest.raises(ModerationError):
        check_curiosity(curiosity)


def test_blocks_ignoring_accents_and_case():
    with pytest.raises(ModerationError):
        check_curiosity("PORNOGRAFÍA")


@pytest.mark.parametrize(
    "curiosity",
    [
        "quiero matarte",
        "vamos a matarnos",
        "se quiere suicidar",
        "eran suicidas",
        "que es un drogadicto",
        "como drogar a alguien",
        "videos pornograficos",
        "que es la sexualidad",
        "armamento nuclear",
    ],
)
def test_blocks_conjugations_and_derived_forms(curiosity: str):
    """Regresión: pasar de subcadena a palabra completa abrió falsos negativos.

    La versión por subcadena bloqueaba estas formas derivadas; enumerarlas una a
    una se dejó fuera conjugaciones ("matarte") y derivados ("drogadicto").
    """
    with pytest.raises(ModerationError):
        check_curiosity(curiosity)
