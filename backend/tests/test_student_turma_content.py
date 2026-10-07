import uuid

from fastapi.testclient import TestClient
from app.main import app


def test_aluno_recebe_conteudo_da_turma():
    client = TestClient(app)
    suffix = uuid.uuid4().hex[:8]

    escola = client.post(
        '/api/v1/admin/escolas',
        json={'nome': f'Escola Conteúdo {suffix}', 'cidade': 'São Paulo', 'estado': 'SP', 'diretor': 'Diretora Teste'},
        headers={'x-tipo-usuario': 'administrador'},
    )
    assert escola.status_code == 200
    escola_id = escola.json()['escola']['id']

    professor = client.post(
        '/api/v1/admin/professores',
        json={'nome': 'Prof. Conteúdo', 'email': f'prof_{suffix}@escola.com', 'disciplina': 'Matemática', 'escola_id': escola_id},
        headers={'x-tipo-usuario': 'administrador'},
    )
    assert professor.status_code == 200
    professor_id = professor.json()['professor']['id']

    turma = client.post(
        '/api/v1/professor/criar-turma',
        json={'nome': f'Turma Conteúdo {suffix}', 'ano': '8º Ano', 'codigo': f'CON{suffix[:5].upper()}', 'escola_id': escola_id, 'professor_id': professor_id},
        headers={'x-tipo-usuario': 'professor'},
    )
    assert turma.status_code == 200
    turma_id = turma.json()['turma']['id']

    aluno = client.post(
        '/api/v1/professor/alunos',
        json={'nome': 'Maria', 'email': f'maria_{suffix}@escola.com', 'turma_id': turma_id},
        headers={'x-tipo-usuario': 'professor'},
    )
    assert aluno.status_code == 200

    plano = client.post(
        '/api/v1/professor/gerar-plano',
        json={'tema_aula': 'Frações', 'objetivos': ['Comparar frações', 'Aplicar simplificação'], 'ano': '8º Ano', 'nivel': 'Básico', 'duracao': '40 min', 'turma_id': turma_id},
        headers={'x-tipo-usuario': 'professor'},
    )
    assert plano.status_code == 200

    quiz = client.post(
        '/api/v1/professor/gerar-quiz',
        json={'tema': 'Frações', 'objetivo': 'Identificar frações equivalentes', 'quantidade': 3, 'nivel': 'Básico', 'turma_id': turma_id},
        headers={'x-tipo-usuario': 'professor'},
    )
    assert quiz.status_code == 200

    conteudo = client.get(
        '/api/v1/aluno/conteudo-turma',
        params={'email_aluno': f'maria_{suffix}@escola.com'},
        headers={'x-tipo-usuario': 'aluno'},
    )
    assert conteudo.status_code == 200
    payload = conteudo.json()
    assert payload['turma_id'] == turma_id
    assert len(payload['planos']) >= 1
    assert len(payload['quizzes']) >= 1
