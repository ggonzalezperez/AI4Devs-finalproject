from app.services.lesson_generator import SUBJECTS, StubLessonGenerator


def test_stub_is_deterministic_and_well_formed():
    gen = StubLessonGenerator()
    a = gen.generate("¿por qué llueve?", age=7, subject=None)
    b = gen.generate("¿por qué llueve?", age=7, subject=None)
    assert a.subject == b.subject
    assert a.subject in SUBJECTS
    assert len(a.quiz_options) == 3
    assert 0 <= a.quiz_correct_index < 3
    assert a.concept
    assert "llueve" in a.body.lower() or "llueve" in a.title.lower()


def test_stub_respects_forced_subject():
    gen = StubLessonGenerator()
    g = gen.generate("dinosaurios", age=8, subject="arte")
    assert g.subject == "arte"


def test_stub_follow_ups_not_empty_and_bounded():
    gen = StubLessonGenerator()
    g = gen.generate("¿cómo vuelan los pájaros?", age=7, subject=None)
    assert len(g.follow_ups) > 0
    assert len(g.follow_ups) <= 3


def test_stub_adapts_body_to_age_band():
    """RF-APR-03: el contenido debe corresponder a la banda de edad.

    En modo demo (sin proveedor) el stub daba el mismo cuerpo a un niño de 4
    años y a uno de 11: la promesa del requisito no se cumplía.
    """
    gen = StubLessonGenerator()
    pequeno = gen.generate("¿por qué llueve?", age=4, subject=None)
    mediano = gen.generate("¿por qué llueve?", age=7, subject=None)
    mayor = gen.generate("¿por qué llueve?", age=11, subject=None)

    assert pequeno.body != mediano.body != mayor.body
    # Las bandas de docs/entrega-1: 2-3 frases (3-5) < 4-6 (6-8) < 6-9 (9-12).
    assert len(pequeno.body) < len(mediano.body) < len(mayor.body)
