from fastapi.testclient import TestClient

from app.main import app
from app.store import reset_store


def main():
    reset_store()
    client = TestClient(app)
    suffix = 'workflow-relations'

    escola = client.post(
        '/api/v1/admin/escolas',
        json={'nome': 'Escola Relacionamentos', 'cidade': 'São Paulo', 'estado': 'SP', 'diretor': 'Diretora'},
        headers={'x-tipo-usuario': 'administrador'},
    )
    assert escola.status_code == 200, escola.json()
    escola_id = escola.json()['escola']['id']

    professor_email = f'prof.{suffix}@escola.com'
    professor = client.post(
        '/api/v1/admin/professores',
        json={'nome': 'Prof. Relação', 'email': professor_email, 'disciplina': 'História', 'escola_id': escola_id},
        headers={'x-tipo-usuario': 'administrador'},
    )
    assert professor.status_code == 200, professor.json()
    professor_id = professor.json()['professor']['id']

    turma_ok = client.post(
        '/api/v1/professor/criar-turma',
        json={'nome': 'Turma Interna', 'ano': '7º Ano', 'codigo': 'INT7A', 'escola_id': escola_id, 'professor_id': professor_id},
        headers={'x-tipo-usuario': 'professor'},
    )
    assert turma_ok.status_code == 200, turma_ok.json()

    turma_errada = client.post(
        '/api/v1/professor/criar-turma',
        json={'nome': 'Turma Fora do Contexto', 'ano': '8º Ano', 'codigo': 'ERR8A', 'escola_id': escola_id, 'professor_id': 999999},
        headers={'x-tipo-usuario': 'professor'},
    )
    assert turma_errada.status_code == 400, turma_errada.json()

    aluno = client.post(
        '/api/v1/professor/alunos',
        json={'nome': 'Aluno Interno', 'email': f'aluno.{suffix}@escola.com', 'turma_id': turma_ok.json()['turma']['id']},
        headers={'x-tipo-usuario': 'professor'},
    )
    assert aluno.status_code == 200, aluno.json()

    print('WORKFLOW_RELATIONS_OK')


if __name__ == '__main__':
    main()
