import uuid

from fastapi.testclient import TestClient
from app.main import app


def main():
    client = TestClient(app)
    suffix = uuid.uuid4().hex[:8]
    admin_email = f'admin_{suffix}@edu.com'
    professor_email = f'paula_{suffix}@escola.com'

    r = client.post(
        '/api/v1/auth/registrar',
        json={'nome': 'Ana Admin', 'email': admin_email, 'senha': '123456', 'tipo': 'administrador'}
    )
    print('REGISTER_ADMIN', r.status_code, r.json())
    assert r.status_code == 200

    login = client.post(
        '/api/v1/auth/login',
        json={'email': admin_email, 'senha': '123456'}
    )
    print('LOGIN_ADMIN', login.status_code, login.json())
    assert login.status_code == 200 and 'access_token' in login.json()

    token = login.json()['access_token']
    r = client.post(
        '/api/v1/admin/escolas',
        json={'nome': f'Escola {suffix}', 'cidade': 'São Paulo', 'estado': 'SP', 'diretor': 'Diretora'},
        headers={'Authorization': f'Bearer {token}'}
    )
    print('ADMIN_ESCUELA', r.status_code, r.json())
    assert r.status_code == 200
    escola_id = r.json()['escola']['id']

    r = client.post(
        '/api/v1/auth/registrar',
        json={'nome': 'Prof. Paula', 'email': professor_email, 'senha': 'abcdef', 'tipo': 'professor'}
    )
    print('REGISTER_PROF', r.status_code, r.json())
    assert r.status_code == 200

    login_prof = client.post('/api/v1/auth/login', json={'email': professor_email, 'senha': 'abcdef'})
    token_prof = login_prof.json()['access_token']

    r = client.post(
        '/api/v1/professor/criar-turma',
        json={'nome': f'Turma Auth {suffix}', 'ano': '8º Ano', 'codigo': f'AUTH{suffix.upper()}', 'escola_id': escola_id, 'professor_id': 1},
        headers={'Authorization': f'Bearer {token_prof}'}
    )
    print('PROF_CREATE_CLASS', r.status_code, r.json())
    assert r.status_code == 200

    print('AUTH_OK')


if __name__ == '__main__':
    main()
