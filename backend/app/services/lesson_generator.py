from dataclasses import dataclass, field
from typing import Protocol

SUBJECTS = ["ciencia", "matematicas", "lenguaje", "arte", "cultura"]


@dataclass
class GeneratedLesson:
    subject: str
    concept: str
    title: str
    body: str
    fun_fact: str
    quiz_question: str
    quiz_options: list[str]
    quiz_correct_index: int
    quiz_explanation: str
    follow_ups: list[str] = field(default_factory=list)


class LessonGenerator(Protocol):
    def generate(
        self, curiosity: str, age: int, subject: str | None,
        history: list[tuple[str, str]] | None = None,
    ) -> GeneratedLesson: ...


def _stub_body(clean: str, age: int) -> str:
    """Cuerpo del stub adaptado a la banda de edad (RF-APR-03).

    Las bandas y su extensión salen de docs/entrega-1: 2-3 frases muy simples
    para 3-5, 4-6 frases con una analogía para 6-8, y 6-9 frases con una palabra
    nueva y una cadena causa-efecto para 9-12. Sin esto, el modo demo daba el
    mismo texto a un niño de 4 años y a uno de 11.
    """
    if age <= 5:
        return (
            f"¡Ooooh, «{clean}»! Qué buena pregunta. Mira a tu alrededor y verás "
            f"pistas por todas partes. ¡Vamos a descubrirlo juntos!"
        )
    if age <= 8:
        return (
            f"¡Buena pregunta! Vamos a descubrir «{clean}» juntos. Piensa en ello como "
            f"en un rompecabezas: cada pieza que encuentras encaja con otra y, poco a "
            f"poco, se ve el dibujo entero. Lo importante es observar y atreverte a "
            f"preguntar. Cada cosa que te sorprende esconde un porqué. Y cada porqué "
            f"que descubres se convierte en una isla nueva de tu archipiélago."
        )
    return (
        f"¡Buena pregunta! Vamos a descubrir «{clean}» juntos. Para entenderlo bien "
        f"conviene ir por partes, porque casi nada ocurre por una sola causa. "
        f"A esa forma de mirar se le llama «indagar»: hacerse preguntas cada vez más "
        f"precisas hasta dar con el porqué de verdad. Primero observas algo que te "
        f"sorprende. Luego te preguntas qué lo ha provocado. Después buscas si eso "
        f"mismo pasa en otros sitios. Y cuando encuentras el patrón, ya no lo olvidas. "
        f"Cada porqué que descubres se convierte en una isla nueva de tu archipiélago."
    )


class StubLessonGenerator:
    """Generador determinista de marcador de posición (sin IA externa).

    Costura para un adaptador real (LLM) que implementará la misma interfaz.
    """

    def generate(self, curiosity: str, age: int, subject: str | None, history: list[tuple[str, str]] | None = None) -> GeneratedLesson:
        clean = curiosity.strip()
        chosen = subject if subject in SUBJECTS else SUBJECTS[len(clean) % len(SUBJECTS)]
        concept = clean.rstrip("?¿! ").lower()[:120] or "descubrimiento"
        title = clean[:1].upper() + clean[1:] if clean else "Tu curiosidad"
        body = _stub_body(clean, age)
        if history:
            body = "Sigamos con nuestra conversación. " + body
        fun_fact = f"¿Sabías que casi nadie se detiene a pensar en «{clean}»? ¡Tú sí, y eso es de exploradores!"
        return GeneratedLesson(
            subject=chosen,
            concept=concept,
            title=title,
            body=body,
            fun_fact=fun_fact,
            quiz_question=f"¿Qué es lo mejor para descubrir sobre «{clean}»?",
            quiz_options=["Adivinar sin mirar", "Observar y preguntar", "Quedarme quieto"],
            quiz_correct_index=1,
            quiz_explanation="Observar y preguntar es la mejor forma de descubrir.",
            follow_ups=[
                f"¿Por qué ocurre «{clean}»?",
                "¿Me das un ejemplo divertido?",
                "¿Qué más puedo descubrir de esto?",
            ],
        )
