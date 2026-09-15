from dataclasses import dataclass


@dataclass
class GeneratedStory:
    title: str
    body: str


class StubStoryGenerator:
    """Cuento determinista a partir de los conceptos que el niño ha explorado.

    Costura para un generador real (LLM) que implementará la misma interfaz.
    """

    def generate(self, child_name: str, age: int, concepts: list[str]) -> GeneratedStory:
        if concepts:
            tema = ", ".join(concepts[:3])
            cuerpo = (
                f"Érase una vez {child_name}, un explorador muy curioso de {age} años. "
                f"En su archipiélago había descubierto islas mágicas sobre {tema}. "
                f"Una mañana, {child_name} montó en su barquito y navegó hacia la isla de "
                f"{concepts[0]}. Allí aprendió que cada pregunta abre una puerta nueva. "
                f"Al volver a casa, {child_name} se durmió feliz, soñando con la próxima aventura."
            )
            titulo = f"La aventura de {child_name} y {concepts[0]}"
        else:
            cuerpo = (
                f"Érase una vez {child_name}, un explorador de {age} años con muchas ganas "
                f"de descubrir el mundo. Su aventura no ha hecho más que empezar."
            )
            titulo = f"El comienzo de {child_name}"
        return GeneratedStory(title=titulo, body=cuerpo)
