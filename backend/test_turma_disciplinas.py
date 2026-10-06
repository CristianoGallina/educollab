from fastapi.testclient import TestClient

from app.main import app
from app.store import reset_store


def main():
    reset_store()
    client = TestClient(app)

    escola = client.post(
        '/api/v1/admin/escolas',
        json={'nome': 'Escola Disciplinas', 'cidade': 'São Paulo', 'estado': 'SP', 'diretor': 'Diretora'},
        headers={'x-tipo-usuario': 'administrador'},
    )
    assert escola.status_code == 200, escola.json()
    escola_id = escola.json()['escola']['id']

    professor = client.post(
        '/api/v1/admin/professores',
        json={'nome': 'Prof. Multi', 'email': 'prof.multi@escola.com', 'disciplina': 'Geral', 'escola_id': escola_id},
        headers={'x-tipo-usuario': 'administrador'},
    )
    assert professor.status_code == 200, professor.json()
    professor_id = professor.json()['professor']['id']

    turma = client.post(
        '/api/v1/professor/criar-turma',
        json={
            'nome': '7º Ano A',
            'ano': '7º Ano',
            'codigo': 'DISC7A',
            'escola_id': escola_id,
            'professor_id': professor_id,
            'disciplinas': ['Matematica', 'Portugues', 'Ciencias'],
        },
        headers={'x-tipo-usuario': 'professor'},
    )
    assert turma.status_code == 200, turma.json()
    turma_id = turma.json()['turma']['id']
    nomes = [item['nome'] for item in turma.json()['turma']['disciplinas']]
    assert nomes == ['Matematica', 'Portugues', 'Ciencias']

    extra = client.post(
        f'/api/v1/professor/turma/{turma_id}/disciplinas',
        json={'nome': 'Historia'},
        headers={'x-tipo-usuario': 'professor'},
    )
    assert extra.status_code == 200, extra.json()
    nomes_atualizados = [item['nome'] for item in extra.json()['turma']['disciplinas']]
    assert 'Historia' in nomes_atualizados

    aluno = client.post(
        '/api/v1/professor/alunos',
        json={'nome': 'Aluno Disciplina', 'email': 'aluno.disciplina@escola.com', 'turma_id': turma_id},
        headers={'x-tipo-usuario': 'professor'},
    )
    assert aluno.status_code == 200, aluno.json()

    dashboard = client.get('/api/v1/professor/dashboard', headers={'x-tipo-usuario': 'professor'})
    assert dashboard.status_code == 200, dashboard.json()
    turma_dashboard = next(item for item in dashboard.json()['turmas'] if item['id'] == turma_id)
    assert len(turma_dashboard['disciplinas']) == 4
    assert any(item['email'] == 'aluno.disciplina@escola.com' for item in turma_dashboard['alunos'])

    print('TURMA_DISCIPLINAS_OK')


if __name__ == '__main__':
    main()
