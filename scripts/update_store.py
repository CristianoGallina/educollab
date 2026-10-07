import re

with open('backend/app/store.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Update get_conteudo_por_turma signature
content = content.replace(
    'def get_conteudo_por_turma(turma_id: int) -> dict:',
    'def get_conteudo_por_turma(turma_id: int, somente_publicados: bool = False) -> dict:'
)

# Update get_conteudo_por_turma body
old_quizzes = '''        quizzes = [
            _serialize_quiz(item)
            for item in session.query(Quiz).filter(Quiz.turma_id == int(turma_id)).order_by(Quiz.id.desc()).all()
        ]'''
new_quizzes = '''        quiz_query = session.query(Quiz).filter(Quiz.turma_id == int(turma_id))
        if somente_publicados:
            quiz_query = quiz_query.filter(Quiz.status == 'publicado')
        quizzes = [_serialize_quiz(item) for item in quiz_query.order_by(Quiz.id.desc()).all()]'''
content = content.replace(old_quizzes, new_quizzes)

# Update get_conteudo_por_aluno
content = content.replace(
    'conteudo_turma = get_conteudo_por_turma(turma_id)',
    'conteudo_turma = get_conteudo_por_turma(turma_id, somente_publicados=True)'
)

# Update _serialize_quiz
old_serialize = '''        "quantidade": item.quantidade,
        "turma_id": item.turma_id,
        "conteudo": item.conteudo,
    }'''
new_serialize = '''        "quantidade": item.quantidade,
        "turma_id": item.turma_id,
        "status": item.status,
        "conteudo": item.conteudo,
    }'''
content = content.replace(old_serialize, new_serialize)

with open('backend/app/store.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("store.py atualizado!")
