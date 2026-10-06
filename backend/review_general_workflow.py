from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def ok(label, resp):
    print(f'{label}: {resp.status_code}')
    if resp.status_code >= 400:
        raise AssertionError(f'{label} falhou: {resp.text}')
    return resp.json()


# 1) Health and login
root = ok('ROOT', client.get('/'))
assert root.get('status') == 'EduCollab IA Microservice Operacional'

login = ok('LOGIN_ADMIN', client.post('/api/v1/auth/login', json={'email': 'admin@educollab.demo', 'senha': 'admin123'}))
assert login.get('status') == 'sucesso'

# 2) Admin flows
admin_headers = {'x-tipo-usuario': 'administrador'}
resumo = ok('ADMIN_RESUMO', client.get('/api/v1/admin/resumo', headers=admin_headers))
assert 'total_escolas' in resumo

escolas_before = ok('ADMIN_ESCOLAS', client.get('/api/v1/admin/escolas', headers=admin_headers))
assert 'escolas' in escolas_before

school = ok('ADMIN_CREATE_SCHOOL', client.post('/api/v1/admin/escolas', json={
    'nome': 'Escola QA Completa',
    'cidade': 'São Paulo',
    'estado': 'SP',
    'diretor': 'Diretora QA',
    'provedor_ia': 'grok',
    'modelo_ia': 'grok-2-latest',
    'api_key_ia': 'sk-demo-qa-key',
}, headers=admin_headers))
assert school['status'] == 'sucesso'
school_id = school['escola']['id']

config_ia = ok('ADMIN_CONFIG_IA', client.post(f'/api/v1/admin/escolas/{school_id}/configuracao-ia', json={
    'provedor_ia': 'grok',
    'modelo_ia': 'grok-2-latest',
    'api_key_ia': 'sk-demo-qa-key'
}, headers=admin_headers))
assert config_ia['status'] == 'sucesso'

professor = ok('ADMIN_CREATE_PROF', client.post('/api/v1/admin/professores', json={
    'nome': 'Prof. QA Auto',
    'email': 'qa.professor@demo.com',
    'disciplina': 'Matemática',
    'escola_id': school_id,
}, headers=admin_headers))
assert professor['status'] == 'sucesso'
professor_id = professor['professor']['id']

# 3) Professor flows
prof_headers = {'x-tipo-usuario': 'professor'}
prof_dashboard = ok('PROF_DASHBOARD', client.get('/api/v1/professor/dashboard', headers=prof_headers))
assert 'total_turmas' in prof_dashboard

class_resp = ok('PROF_CREATE_CLASS', client.post('/api/v1/professor/criar-turma', json={
    'nome': 'Turma QA Final',
    'ano': '7º Ano',
    'codigo': 'QA7A',
    'cor': 'bg-violet-500',
    'escola_id': school_id,
    'professor_id': professor_id,
}, headers=prof_headers))
assert class_resp['status'] == 'sucesso'
class_id = class_resp['turma']['id']

student = ok('PROF_CREATE_STUDENT', client.post('/api/v1/professor/alunos', json={
    'nome': 'Aluno QA',
    'email': 'aluno.qa@demo.com',
    'turma_id': class_id,
}, headers=prof_headers))
assert student['status'] == 'sucesso'

plan = ok('PROF_GENERATE_PLAN', client.post('/api/v1/professor/gerar-plano', json={
    'tema_aula': 'Frações',
    'objetivos': ['Reconhecer frações equivalentes', 'Aplicar a simplificação'],
    'ano': '7º Ano',
    'nivel': 'Básico',
    'duracao': '40 min',
    'turma_id': class_id,
}, headers=prof_headers))
assert plan['status'] == 'sucesso'

quiz = ok('PROF_GENERATE_QUIZ', client.post('/api/v1/professor/gerar-quiz', json={
    'tema': 'Frações',
    'objetivo': 'Verificar compreensão de frações equivalentes',
    'quantidade': 3,
    'nivel': 'Básico',
    'turma_id': class_id,
}, headers=prof_headers))
assert quiz['status'] == 'sucesso'

# 4) Student flow
student_headers = {'x-tipo-usuario': 'aluno'}
student_feedback = ok('STUDENT_FEEDBACK', client.post('/api/v1/aluno/feedback-quiz', json={
    'id_exercicio': 'fractions-qa',
    'email_aluno': 'aluno.qa@demo.com',
    'nota_final': 8.5,
    'respostas_aluno': ['A', 'B', 'A'],
    'gabarito_oficial': ['A', 'B', 'C'],
}, headers=student_headers))
assert student_feedback['status'] == 'sucesso'
assert 'feedback_ia' in student_feedback

# 5) Cleanup of IA config
remove_ia = ok('ADMIN_REMOVE_IA_CONFIG', client.delete(f'/api/v1/admin/escolas/{school_id}/configuracao-ia', headers=admin_headers))
assert remove_ia['status'] == 'sucesso'

print('ALL_FLOWS_VERIFIED: PASS')
