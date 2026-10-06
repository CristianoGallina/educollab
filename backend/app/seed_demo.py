import os
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from .models import (
    User, School, Teacher, ClassRoom, Student, Plan, Quiz, QuizQuestion, 
    QuizSubmission, Content, SystemLog, class_teachers
)
import bcrypt
import json
from datetime import datetime, timedelta

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def seed():
    print("Iniciando popular DB com dados lógicos de demonstração...")
    with SessionLocal() as db:
        
        # 1. Obter a escola 1 (que o sistema já cria) ou criar
        escola = db.query(School).filter(School.id == 1).first()
        if not escola:
            escola = School(
                nome="Colégio Inovação Integrada",
                cidade="São Paulo",
                estado="SP",
                diretor="Marta Fernandes",
                api_key_ia="mocked_key",
                provedor_ia="grok",
                modelo_ia="grok-2-latest"
            )
            db.add(escola)
            db.commit()
            db.refresh(escola)
        else:
            escola.nome = "Colégio Inovação Integrada"
            escola.cidade = "São Paulo"
            db.commit()

        # 2. Usuários base (Garantir que existem)
        users_to_check = [
            ("admin@educollab.demo", "admin123", "administrador"),
            ("professor@educollab.demo", "prof123", "professor"),
            ("aluno@educollab.demo", "aluno123", "aluno")
        ]
        
        for email, pwd, role in users_to_check:
            u = db.query(User).filter(User.email == email).first()
            if not u:
                u = User(email=email, password_hash=get_password_hash(pwd), role=role)
                db.add(u)
        db.commit()

        # 3. Professor Principal
        prof_user = db.query(User).filter(User.email == "professor@educollab.demo").first()
        prof = db.query(Teacher).filter(Teacher.email == prof_user.email).first()
        if not prof:
            prof = Teacher(nome="Prof. Carlos Matemática", email=prof_user.email, disciplina="Matemática", escola_id=escola.id)
            db.add(prof)
            db.commit()
            db.refresh(prof)
            
        # Professor Secundário
        prof_sec_user = db.query(User).filter(User.email == "roberta@educollab.demo").first()
        if not prof_sec_user:
            prof_sec_user = User(email="roberta@educollab.demo", password_hash=get_password_hash("prof123"), role="professor")
            db.add(prof_sec_user)
            db.commit()
            prof2 = Teacher(nome="Profa. Roberta Ciências", email="roberta@educollab.demo", disciplina="Ciências", escola_id=escola.id)
            db.add(prof2)
            db.commit()

        # 4. Turmas Lógicas
        turma_8a = db.query(ClassRoom).filter(ClassRoom.codigo == "8A-MAT").first()
        if not turma_8a:
            turma_8a = ClassRoom(nome="8º Ano A - Matemática", ano="8º Ano", codigo="8A-MAT", cor="bg-blue-500", escola_id=escola.id, professor_id=prof.id)
            db.add(turma_8a)
            db.commit()
            db.refresh(turma_8a)
            # Vincular prof na tabela associativa
            turma_8a.teachers.append(prof)
            db.commit()

        turma_9b = db.query(ClassRoom).filter(ClassRoom.codigo == "9B-MAT").first()
        if not turma_9b:
            turma_9b = ClassRoom(nome="9º Ano B - Preparatório", ano="9º Ano", codigo="9B-MAT", cor="bg-indigo-600", escola_id=escola.id, professor_id=prof.id)
            db.add(turma_9b)
            db.commit()
            db.refresh(turma_9b)
            turma_9b.teachers.append(prof)
            db.commit()

        # 5. Alunos (Populando o 8º Ano A)
        # O Aluno da Demo:
        aluno_demo = db.query(Student).filter(Student.email == "aluno@educollab.demo").first()
        if not aluno_demo:
            aluno_demo = Student(nome="Cristiano (Aluno Demo)", email="aluno@educollab.demo", turma_id=turma_8a.id)
            db.add(aluno_demo)
        else:
            aluno_demo.turma_id = turma_8a.id
            aluno_demo.nome = "Cristiano (Aluno Demo)"

        # Alunos para gerar LÓGICA preditiva (os que estão mal)
        mock_students = [
            {"nome": "João Pedro Santos", "email": "joao@educollab.demo", "turma": turma_8a.id},
            {"nome": "Maria Clara Oliveira", "email": "maria@educollab.demo", "turma": turma_8a.id},
            {"nome": "Ana Sofia Silva", "email": "ana@educollab.demo", "turma": turma_8a.id},
            {"nome": "Lucas Martins", "email": "lucas@educollab.demo", "turma": turma_9b.id}
        ]
        
        for ms in mock_students:
            u = db.query(User).filter(User.email == ms["email"]).first()
            if not u:
                db.add(User(email=ms["email"], password_hash=get_password_hash("aluno123"), role="aluno"))
            stu = db.query(Student).filter(Student.email == ms["email"]).first()
            if not stu:
                db.add(Student(nome=ms["nome"], email=ms["email"], turma_id=ms["turma"]))
        db.commit()

        # 6. Planos de Aula Realistas
        planos_dados = [
            {
                "tema": "Introdução às Frações",
                "objetivos": '["Entender o conceito de parte e todo", "Soma de frações com mesmo denominador"]',
                "turma_id": turma_8a.id,
                "habilidades_bncc": '["EF06MA07", "EF06MA08"]',
                "status": "rascunho"
            },
            {
                "tema": "Equações de 1º Grau",
                "objetivos": '["Isolar a incógnita", "Resolver problemas do cotidiano"]',
                "turma_id": turma_8a.id,
                "habilidades_bncc": '["EF07MA18"]',
                "status": "pronto"
            }
        ]
        
        for pd in planos_dados:
            pl = db.query(Plan).filter(Plan.tema_aula == pd["tema"]).first()
            if not pl:
                db.add(Plan(
                    tema_aula=pd["tema"], 
                    objetivos=pd["objetivos"], 
                    ano="8º Ano", nivel="Básico", duracao="50 min", 
                    turma_id=pd["turma_id"], disciplina="Matemática", 
                    habilidades_bncc=pd["habilidades_bncc"], 
                    conteudo_gerado="Conteúdo rico gerado por IA sobre " + pd["tema"], 
                    status=pd["status"]
                ))
        db.commit()

        # 7. Quizzes Realistas e Submissões para LÓGICA PREDITIVA
        # Quiz: Frações
        quiz_fracao = db.query(Quiz).filter(Quiz.tema == "Operações com Frações Básicas").first()
        if not quiz_fracao:
            quiz_fracao = Quiz(
                tema="Operações com Frações Básicas", 
                objetivo="Avaliar soma e subtração de frações.", 
                quantidade=3, nivel="Básico", 
                turma_id=turma_8a.id, disciplina="Matemática", 
                status="publicado"
            )
            db.add(quiz_fracao)
            db.commit()
            db.refresh(quiz_fracao)
            
            # Adicionar perguntas
            db.add(QuizQuestion(quiz_id=quiz_fracao.id, tipo="multipla_escolha", pergunta="Quanto é 1/2 + 1/2?", opcoes=json.dumps(["1", "2", "1/4", "0"]), resposta_correta="1", justificativa="Meio mais meio dá um inteiro."))
            db.add(QuizQuestion(quiz_id=quiz_fracao.id, tipo="multipla_escolha", pergunta="Quanto é 3/4 - 1/4?", opcoes=json.dumps(["2/4", "4/4", "1/2", "Ambas 2/4 e 1/2"]), resposta_correta="Ambas 2/4 e 1/2", justificativa="2/4 simplificado é 1/2."))
            db.add(QuizQuestion(quiz_id=quiz_fracao.id, tipo="multipla_escolha", pergunta="O que é o numerador?", opcoes=json.dumps(["A parte de cima", "A parte de baixo", "O traço", "O resultado"]), resposta_correta="A parte de cima", justificativa="Numerador numera as partes."))
            db.commit()

            # SUBMISSÕES: Aqui está a LÓGICA!
            # Aluno Demo tira 7
            sub1 = QuizSubmission(
                quiz_id=quiz_fracao.id,
                email_aluno="aluno@educollab.demo",
                respostas=json.dumps([{"pergunta_id": 1, "resposta": "1"}, {"pergunta_id": 2, "resposta": "1/2"}, {"pergunta_id": 3, "resposta": "A parte de baixo"}]),
                nota_final=6.6,
                parecer_ia="Bom desempenho, mas confundiu o conceito de numerador. Recomenda-se revisão conceitual."
            )
            # João tira 3.3 (Risco alto)
            sub2 = QuizSubmission(
                quiz_id=quiz_fracao.id,
                email_aluno="joao@educollab.demo",
                respostas=json.dumps([{"pergunta_id": 1, "resposta": "1/4"}, {"pergunta_id": 2, "resposta": "4/4"}, {"pergunta_id": 3, "resposta": "A parte de cima"}]),
                nota_final=3.3,
                parecer_ia="O aluno João demonstra forte dificuldade em operações com frações. Identificamos lacunas graves no conceito de denominadores iguais. Sugiro Trilha Nível 1 urgente."
            )
            # Maria tira 3.3 (Risco alto)
            sub3 = QuizSubmission(
                quiz_id=quiz_fracao.id,
                email_aluno="maria@educollab.demo",
                respostas=json.dumps([{"pergunta_id": 1, "resposta": "2"}, {"pergunta_id": 2, "resposta": "2/4"}, {"pergunta_id": 3, "resposta": "O resultado"}]),
                nota_final=3.3,
                parecer_ia="A aluna apresenta dificuldade em visualizar proporções. Intervenção necessária."
            )
            # Ana tira 10 (Monitora)
            sub4 = QuizSubmission(
                quiz_id=quiz_fracao.id,
                email_aluno="ana@educollab.demo",
                respostas=json.dumps([{"pergunta_id": 1, "resposta": "1"}, {"pergunta_id": 2, "resposta": "Ambas 2/4 e 1/2"}, {"pergunta_id": 3, "resposta": "A parte de cima"}]),
                nota_final=10.0,
                parecer_ia="Domínio completo. A aluna pode atuar como tutora dos colegas neste tópico."
            )
            db.add_all([sub1, sub2, sub3, sub4])
            db.commit()

        # 8. Logs de Consumo Realistas para o Admin
        logs = db.query(SystemLog).filter(SystemLog.escola_id == escola.id).count()
        if logs < 10:
            for i in range(10):
                l = SystemLog(
                    escola_id=escola.id,
                    tipo_evento="uso_ia",
                    descricao=f"Geração de Quiz de Matemática {i}",
                    usuario_email="professor@educollab.demo",
                    tokens_usados=1500 + (i*100),
                    custo=0.03 + (i*0.005),
                    created_at=datetime.now() - timedelta(days=i)
                )
                db.add(l)
            db.commit()

    print("✅ Banco de dados populado com lógica demo completa!")

if __name__ == "__main__":
    seed()
