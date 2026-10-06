import uuid

from fastapi.testclient import TestClient
from app.main import app


def main():
    client = TestClient(app)
    suffix = uuid.uuid4().hex[:8]

    escola_r = client.post(
        '/api/v1/admin/escolas',
        json={'nome': f'Escola Municipal {suffix}', 'cidade': 'São Paulo', 'estado': 'SP', 'diretor': 'Ana Souza'},
        headers={'x-tipo-usuario': 'administrador'},
    )
    print('SCHOOL', escola_r.status_code, escola_r.json())
    assert escola_r.status_code == 200
    escola_id = escola_r.json()['escola']['id']

    professor_email = f'silva_{suffix}@escola.com'
    professor_r = client.post(
        '/api/v1/admin/professores',
        json={'nome': 'Prof. Silva', 'email': professor_email, 'disciplina': 'Matemática', 'escola_id': escola_id},
        headers={'x-tipo-usuario': 'administrador'},
    )
    print('TEACHER', professor_r.status_code, professor_r.json())
    assert professor_r.status_code == 200
    professor_id = professor_r.json()['professor']['id']

    turma_r = client.post(
        '/api/v1/professor/criar-turma',
        json={'nome': f'Turma 7A {suffix}', 'ano': '7º Ano', 'codigo': f'MAT7A{suffix.upper()}', 'escola_id': escola_id, 'professor_id': professor_id},
        headers={'x-tipo-usuario': 'professor'},
    )
    print('CLASS', turma_r.status_code, turma_r.json())
    assert turma_r.status_code == 200
    turma_id = turma_r.json()['turma']['id']

    aluno_email = f'joao_{suffix}@escola.com'
    aluno_r = client.post(
        '/api/v1/professor/alunos',
        json={'nome': 'João', 'email': aluno_email, 'turma_id': turma_id},
        headers={'x-tipo-usuario': 'professor'},
    )
    print('STUDENT', aluno_r.status_code, aluno_r.json())
    assert aluno_r.status_code == 200

    plano_r = client.post(
        '/api/v1/professor/gerar-plano',
        json={'tema_aula': 'Frações', 'objetivos': ['Reconhecer frações equivalentes', 'Aplicar simplificação'], 'ano': '7º Ano', 'nivel': 'Básico', 'duracao': '40 min', 'turma_id': turma_id},
        headers={'x-tipo-usuario': 'professor'},
    )
    print('PLAN', plano_r.status_code, plano_r.json())
    assert plano_r.status_code == 200 and 'plano' in plano_r.json() and plano_r.json()['plano'].get('turma_id') == turma_id

    quiz_r = client.post(
        '/api/v1/professor/gerar-quiz',
        json={'tema': 'Frações', 'objetivo': 'Identificar frações equivalentes', 'quantidade': 3, 'nivel': 'Básico', 'turma_id': turma_id},
        headers={'x-tipo-usuario': 'professor'},
    )
    print('QUIZ', quiz_r.status_code, quiz_r.json())
    assert quiz_r.status_code == 200 and 'quiz' in quiz_r.json() and quiz_r.json()['quiz'].get('turma_id') == turma_id

    aprovacao_r = client.post(
        '/api/v1/professor/aprovar-quiz',
        json={'tema': 'Frações', 'objetivo': 'Identificar frações equivalentes', 'quantidade': 3, 'turma_id': turma_id, 'aprovado': True},
        headers={'x-tipo-usuario': 'professor'},
    )
    print('APPROVAL', aprovacao_r.status_code, aprovacao_r.json())
    assert aprovacao_r.status_code == 200
    assert aprovacao_r.json()['status'] == 'aprovado'
    assert aprovacao_r.json()['turma_id'] == turma_id
    assert aprovacao_r.json()['alunos_na_turma'] >= 1

    configuracao_r = client.post(
        f'/api/v1/admin/escolas/{escola_id}/configuracao-ia',
        json={'api_key_ia': 'sk-demo-123', 'provedor_ia': 'grok', 'modelo_ia': 'grok-2-latest'},
        headers={'x-tipo-usuario': 'administrador'},
    )
    print('API_CONFIG', configuracao_r.status_code, configuracao_r.json())
    assert configuracao_r.status_code == 200
    assert configuracao_r.json()['escola']['api_key_ia'] == 'sk-demo-123'

    uso_r = client.get(f'/api/v1/admin/escolas/{escola_id}/uso-ia', headers={'x-tipo-usuario': 'administrador'})
    print('USO_API', uso_r.status_code, uso_r.json())
    assert uso_r.status_code == 200
    assert 'totais' in uso_r.json()

    print('ALL_OK')


if __name__ == '__main__':
    main()
