from datetime import date

from app.models.child import Child
from app.models.family import Family
from app.models.knowledge import KnowledgeNode
from app.models.lesson import Lesson


def test_create_lesson_and_node(db_session):
    fam = Family(name="F")
    db_session.add(fam)
    db_session.flush()
    child = Child(family_id=fam.id, name="Leo", birthdate=date(2018, 1, 1), pin_hash="x")
    db_session.add(child)
    db_session.flush()

    lesson = Lesson(
        child_id=child.id, curiosity="¿por qué flotan los barcos?", subject="ciencia",
        concept="flotabilidad", title="Los barcos", body="...", fun_fact="...",
        quiz_question="¿Qué empuja al barco?", quiz_options=["viento", "agua", "sol"],
        quiz_correct_index=1, quiz_explanation="El agua empuja hacia arriba.",
    )
    node = KnowledgeNode(child_id=child.id, concept="flotabilidad", subject="ciencia")
    db_session.add_all([lesson, node])
    db_session.commit()

    assert lesson.id is not None
    assert lesson.answered is False
    assert lesson.quiz_options[1] == "agua"
    assert node.mastery == 1
