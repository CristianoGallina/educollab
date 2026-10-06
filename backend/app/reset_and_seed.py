import logging
from datetime import datetime
from sqlalchemy import text
from .database import (
    Base,
    engine,
    SessionLocal,
    School,
    Teacher,
    ClassRoom,
    Subject,
    Student,
    Plan,
    Quiz,
    QuizSubmission,
    ApiUsage,
    User,
)
from .security import encrypt_secret
from .store import _sync_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")


def reset_and_populate_db():
    logger.info("=== REINICIANDO E LIMPANDO BANCO DE DADOS ===")

    # 1. Truncate ou Drop / Recreate de tabelas
    with SessionLocal() as session:
        # Se for Postgres, podemos truncar em cascata com RESTART IDENTITY
        try:
            session.execute(text("TRUNCATE TABLE quiz_submissions, api_usage, quizzes, plans, class_subjects, students, classes, teachers, schools, users RESTART IDENTITY CASCADE;"))
            session.commit()
            logger.info("Tabelas truncadas com sucesso via TRUNCATE CASCADE.")
        except Exception as e:
            session.rollback()
            logger.warning(f"Truncate falhou ou não suportado ({e}), recriando com Base.metadata...")
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
            logger.info("Tabelas recriadas via metadata.")

    with SessionLocal() as session:
        # 2. ESCOLAS DA REDE
        escola1 = School(
            nome="Escola Municipal Santos Dumont",
            cidade="São Paulo",
            estado="SP",
            diretor="Prof. Marcos Silveira",
            api_key_ia=encrypt_secret("xai-demo-key-santos-dumont-prod"),
            provedor_ia="grok",
            modelo_ia="grok-2-latest",
            tokens_usados=28500,
            custo_total=0.5700,
            uso_ia_ultima_data=datetime.utcnow(),
        )
        escola2 = School(
            nome="Colégio Inovação Integrada",
            cidade="Curitiba",
            estado="PR",
            diretor="Dra. Helena Vasconcelos",
            api_key_ia=encrypt_secret("gsk-demo-key-colegio-inovacao-prod"),
            provedor_ia="groq",
            modelo_ia="openai/gpt-oss-20b",
            tokens_usados=19200,
            custo_total=0.3840,
            uso_ia_ultima_data=datetime.utcnow(),
        )
        escola3 = School(
            nome="Instituto Educacional Alpha",
            cidade="Belo Horizonte",
            estado="MG",
            diretor="Prof. Roberto Andrade",
            api_key_ia=None,  # Chave Pendente para demonstrar o alerta no Admin Dashboard
            provedor_ia="grok",
            modelo_ia="grok-3-mini",
            tokens_usados=0,
            custo_total=0.0,
            uso_ia_ultima_data=None,
        )
        session.add_all([escola1, escola2, escola3])
        session.flush()

        # 3. CORPO DOCENTE
        prof1 = Teacher(
            nome="Prof. Lucas Mendes",
            email="lucas.mendes@santosdumont.edu.br",
            disciplina="Matemática",
            escola_id=escola1.id,
        )
        prof2 = Teacher(
            nome="Profa. Camila Duarte",
            email="camila.duarte@santosdumont.edu.br",
            disciplina="Ciências da Natureza",
            escola_id=escola1.id,
        )
        prof3 = Teacher(
            nome="Prof. André Valente",
            email="andre.valente@colegioinovacao.edu.br",
            disciplina="Língua Portuguesa",
            escola_id=escola2.id,
        )
        session.add_all([prof1, prof2, prof3])
        session.flush()

        # 4. TURMAS
        turma1 = ClassRoom(
            nome="7º Ano A - Fundamental",
            ano="7º Ano",
            codigo="7ANO-A",
            cor="bg-blue-600",
            escola_id=escola1.id,
            professor_id=prof1.id,
        )
        turma2 = ClassRoom(
            nome="8º Ano B - Fundamental",
            ano="8º Ano",
            codigo="8ANO-B",
            cor="bg-emerald-600",
            escola_id=escola1.id,
            professor_id=prof2.id,
        )
        turma3 = ClassRoom(
            nome="9º Ano C - Fundamental",
            ano="9º Ano",
            codigo="9ANO-C",
            cor="bg-violet-600",
            escola_id=escola2.id,
            professor_id=prof3.id,
        )
        session.add_all([turma1, turma2, turma3])
        session.flush()

        # 5. DISCIPLINAS POR TURMA
        disciplinas = [
            # Turma 1
            Subject(nome="Matemática", turma_id=turma1.id),
            Subject(nome="Geometria Plana", turma_id=turma1.id),
            Subject(nome="Raciocínio Lógico", turma_id=turma1.id),
            # Turma 2
            Subject(nome="Ciências Naturais", turma_id=turma2.id),
            Subject(nome="Ecologia e Sustentabilidade", turma_id=turma2.id),
            # Turma 3
            Subject(nome="Língua Portuguesa", turma_id=turma3.id),
            Subject(nome="Literatura e Redação", turma_id=turma3.id),
        ]
        session.add_all(disciplinas)

        # 6. ESTUDANTES
        alunos = [
            # Turma 1 (onde o usuário faz o teste principal)
            Student(nome="Cristiano Santos (Aluno Demo)", email="aluno@educollab.demo", turma_id=turma1.id),
            Student(nome="Beatriz Lima", email="beatriz.lima@santosdumont.demo", turma_id=turma1.id),
            Student(nome="Carlos Eduardo Souza", email="carlos.eduardo@santosdumont.demo", turma_id=turma1.id),
            Student(nome="Mariana Silva", email="mariana.silva@santosdumont.demo", turma_id=turma1.id),
            Student(nome="Gabriel Ribeiro", email="gabriel.ribeiro@santosdumont.demo", turma_id=turma1.id),
            # Turma 2
            Student(nome="Fernanda Rocha", email="fernanda.rocha@santosdumont.demo", turma_id=turma2.id),
            Student(nome="Thiago Martins", email="thiago.martins@santosdumont.demo", turma_id=turma2.id),
            Student(nome="Larissa Nogueira", email="larissa.nogueira@santosdumont.demo", turma_id=turma2.id),
            # Turma 3
            Student(nome="Lucas Ferreira", email="lucas.ferreira@colegioinovacao.demo", turma_id=turma3.id),
            Student(nome="Julia Mendonça", email="julia.mendonca@colegioinovacao.demo", turma_id=turma3.id),
        ]
        session.add_all(alunos)
        session.flush()

        # 7. PLANOS DE AULA (BNCC)
        plano_mat = {
            "titulo": "Plano de Aula: Frações Equivalentes no Cotidiano",
            "tema": "Frações Equivalentes e Operações Básicas",
            "disciplina": "Matemática",
            "ano": "7º Ano",
            "duracao": "50 min",
            "habilidades_bncc": [
                {"codigo": "EF07MA08", "descricao": "Comparar e ordenar frações associadas às ideias de partes de inteiros."},
                {"codigo": "EF07MA09", "descricao": "Utilizar a equivalência de frações para resolver problemas práticos."}
            ],
            "objetivos": [
                "Identificar frações irredutíveis e encontrar equivalências multiplicando numerador e denominador.",
                "Aplicar frações em situações concretas de divisões de recursos e receitas."
            ],
            "sequencia_pedagogica": [
                {"etapa": "Acolhida e Sondagem (10 min)", "descricao": "Apresentação de problema disparador: divisão de pizzas e barras de chocolate entre amigos."},
                {"etapa": "Desenvolvimento Teórico-Prático (25 min)", "descricao": "Conceituação de frações equivalentes com tiras de papel fracionárias e cálculo do MDC."},
                {"etapa": "Aplicação em Duplas (10 min)", "descricao": "Resolução de 3 desafios em duplas com verificação mediada pelo professor."},
                {"etapa": "Fechamento e Síntese (5 min)", "descricao": "Registro da regra fundamental: multiplicar ou dividir numerador e denominador pelo mesmo número natural não nulo."}
            ],
            "metodologia": "Aprendizagem baseada em problemas com apoio de materiais manipuláveis.",
            "recursos": ["Projetor ou lousa", "Fichas de exercícios", "Tiras de frações coloridas"],
            "avaliacao": "Avaliação formativa contínua através do Quiz Diagnóstico na plataforma EduCollab."
        }

        plano_ciencias = {
            "titulo": "Plano de Aula: Cadeias Alimentares e Níveis Tróficos",
            "tema": "Cadeias Alimentares e Fluxo de Energia nos Ecossistemas",
            "disciplina": "Ciências da Natureza",
            "ano": "8º Ano",
            "duracao": "50 min",
            "habilidades_bncc": [
                {"codigo": "EF08CI07", "descricao": "Identificar e comparar diferentes processos reprodutivos e níveis tróficos nos ecossistemas."},
                {"codigo": "EF08CI08", "descricao": "Analisar transformações de matéria e energia por meio de cadeias e teias alimentares."}
            ],
            "objetivos": [
                "Compreender a diferença funcional entre produtores, consumidores e decompositores.",
                "Modelar uma teia trófica de bioma brasileiro identificando o sentido unidirecional da energia."
            ],
            "sequencia_pedagogica": [
                {"etapa": "Sensibilização (10 min)", "descricao": "Vídeo curto sobre o bioma Cerrado e debate sobre o desaparecimento de um predador de topo."},
                {"etapa": "Trabalho em Grupos (25 min)", "descricao": "Construção de teias alimentares com cartões ilustrativos de espécies nativas."},
                {"etapa": "Apresentação e Síntese (15 min)", "descricao": "Conexão entre biomassa, transferência energética e conservação ambiental."}
            ],
            "metodologia": "Metodologia ativa investigativa.",
            "recursos": ["Cartões de espécies tróficas", "Painel interativo"],
            "avaliacao": "Quiz diagnóstico digital e mapa conceitual de ecologia."
        }

        p1 = Plan(tema=plano_mat["tema"], turma_id=turma1.id, conteudo=plano_mat)
        p2 = Plan(tema=plano_ciencias["tema"], turma_id=turma2.id, conteudo=plano_ciencias)
        session.add_all([p1, p2])
        session.flush()

        # 8. QUIZZES E AVALIAÇÕES FORMATIVAS
        quiz_mat_data = {
            "tema": "Frações e Equivalências Práticas",
            "objetivo": "Avaliar simplificação de frações ordinárias e identificação de frações equivalentes no cotidiano.",
            "perguntas": [
                {
                    "pergunta": "Qual é a forma irredutível da fração 12/18?",
                    "opcoes": ["2/3", "3/4", "1/2", "6/9"],
                    "resposta_correta": "2/3",
                    "explicacao": "Dividindo numerador e denominador por 6 (MDC), temos 12÷6=2 e 18÷6=3, logo 2/3."
                },
                {
                    "pergunta": "Uma sala tem 30 alunos, dos quais 18 são meninas. Qual fração irredutível representa a proporção de meninas na turma?",
                    "opcoes": ["3/5", "2/5", "18/30", "9/15"],
                    "resposta_correta": "3/5",
                    "explicacao": "18 de 30 simplificado dividindo ambos por 6 resulta na fração irredutível 3/5."
                },
                {
                    "pergunta": "Qual das opções a seguir NÃO é uma fração equivalente a 3/4?",
                    "opcoes": ["9/12", "15/20", "6/10", "75/100"],
                    "resposta_correta": "6/10",
                    "explicacao": "6/10 simplificado é igual a 3/5 (0,6), que é diferente de 3/4 (0,75). Todas as outras opções equivalem a 3/4."
                },
                {
                    "pergunta": "Se você comeu 4 fatias de uma pizza de 8 pedaços e seu amigo comeu 3 fatias de uma pizza de 6 pedaços, quem comeu mais pizza?",
                    "opcoes": ["Comeram a mesma quantidade (1/2)", "Você comeu mais", "Seu amigo comeu mais", "Não é possível comparar"],
                    "resposta_correta": "Comeram a mesma quantidade (1/2)",
                    "explicacao": "4/8 simplificado é 1/2 e 3/6 simplificado também é 1/2. Portanto, ambos comeram exatamente metade de suas pizzas."
                }
            ]
        }

        quiz_ciencias_data = {
            "tema": "Níveis Tróficos e Fluxo de Energia",
            "objetivo": "Verificar o reconhecimento dos produtores, consumidores e decompositores nos ecossistemas.",
            "perguntas": [
                {
                    "pergunta": "Qual grupo de organismos é responsável por converter energia solar em energia química na base de uma cadeia alimentar?",
                    "opcoes": ["Produtores (autótrofos)", "Consumidores primários", "Decompositores", "Consumidores secundários"],
                    "resposta_correta": "Produtores (autótrofos)",
                    "explicacao": "Plantas e algas realizam a fotossíntese, convertendo a energia solar em compostos orgânicos para toda a teia trófica."
                },
                {
                    "pergunta": "O que acontece com a quantidade de energia útil disponível à medida que se sobe de um nível trófico para o próximo?",
                    "opcoes": ["Diminui progressivamente (cerca de 90% é perdida)", "Aumenta progressivamente", "Permanece exatamente constante", "Dobra a cada nível"],
                    "resposta_correta": "Diminui progressivamente (cerca de 90% é perdida)",
                    "explicacao": "Apenas cerca de 10% da energia é transferida ao nível seguinte; o restante é liberado como calor e utilizado no metabolismo."
                },
                {
                    "pergunta": "Qual é a função ecológica essencial dos decompositores (fungos e bactérias)?",
                    "opcoes": ["Reciclar matéria orgânica em nutrientes minerais", "Produzir oxigênio por fotossíntese", "Caçar herbívoros", "Filtrar a água dos rios"],
                    "resposta_correta": "Reciclar matéria orgânica em nutrientes minerais",
                    "explicacao": "Os decompositores degradam a matéria morta e reinserem nutrientes minerais no solo para serem reutilizados pelos produtores."
                }
            ]
        }

        q1 = Quiz(
            tema=quiz_mat_data["tema"],
            objetivo=quiz_mat_data["objetivo"],
            quantidade=4,
            turma_id=turma1.id,
            conteudo=quiz_mat_data,
            status="publicado",
            created_at=datetime.utcnow(),
        )
        q2 = Quiz(
            tema=quiz_ciencias_data["tema"],
            objetivo=quiz_ciencias_data["objetivo"],
            quantidade=3,
            turma_id=turma2.id,
            conteudo=quiz_ciencias_data,
            status="publicado",
            created_at=datetime.utcnow(),
        )
        session.add_all([q1, q2])
        session.flush()

        # 9. SUBMISSÕES REAIS DOS ALUNOS (ALIMENTANDO O RAIO-X E O HISTÓRICO)
        gabarito_q1 = ["2/3", "3/5", "6/10", "Comeram a mesma quantidade (1/2)"]

        submissoes = [
            # Aluno Demo (nosso usuário de teste)
            QuizSubmission(
                quiz_id=q1.id,
                turma_id=turma1.id,
                email_aluno="aluno@educollab.demo",
                nota_final=7.5,
                respostas_aluno=["2/3", "3/5", "6/10", "Você comeu mais"],  # Errou a 4
                gabarito_oficial=gabarito_q1,
                feedback_ia={
                    "pontos_fortes": ["Excelente domínio de frações irredutíveis e identificação de frações não equivalentes."],
                    "pontos_atencao": ["Atenção à comparação de frações com denominadores distintos: 4/8 e 3/6 são ambas iguais à metade."],
                    "recomendacao_estudo": "Parabéns pelo bom desempenho! Revise a visualização geométrica de frações para fixar grandezas relativas."
                },
                created_at=datetime.utcnow(),
            ),
            # Beatriz Lima (aluna com desempenho excelente)
            QuizSubmission(
                quiz_id=q1.id,
                turma_id=turma1.id,
                email_aluno="beatriz.lima@santosdumont.demo",
                nota_final=10.0,
                respostas_aluno=["2/3", "3/5", "6/10", "Comeram a mesma quantidade (1/2)"],
                gabarito_oficial=gabarito_q1,
                feedback_ia={
                    "pontos_fortes": ["Acerto pleno em todas as questões!", "Raciocínio proporcional apurado."],
                    "pontos_atencao": [],
                    "recomendacao_estudo": "Desempenho exemplar! Pronta para avançar para operações de adição e subtração com denominadores diferentes."
                },
                created_at=datetime.utcnow(),
            ),
            # Carlos Eduardo (aluno que errou 2 itens - entra em alerta pedagógico)
            QuizSubmission(
                quiz_id=q1.id,
                turma_id=turma1.id,
                email_aluno="carlos.eduardo@santosdumont.demo",
                nota_final=5.0,
                respostas_aluno=["6/9", "3/5", "15/20", "Comeram a mesma quantidade (1/2)"],  # Errou q1 e q3
                gabarito_oficial=gabarito_q1,
                feedback_ia={
                    "pontos_fortes": ["Acertou problemas contextuais com aplicação prática."],
                    "pontos_atencao": ["Dificuldade em simplificar frações até a forma irredutível: 6/9 ainda pode ser dividida por 3."],
                    "recomendacao_estudo": "Revisar divisão sucessiva e o uso do MDC para simplificação rápida de frações."
                },
                created_at=datetime.utcnow(),
            ),
            # Mariana Silva
            QuizSubmission(
                quiz_id=q1.id,
                turma_id=turma1.id,
                email_aluno="mariana.silva@santosdumont.demo",
                nota_final=10.0,
                respostas_aluno=["2/3", "3/5", "6/10", "Comeram a mesma quantidade (1/2)"],
                gabarito_oficial=gabarito_q1,
                feedback_ia={
                    "pontos_fortes": ["Precisão e consistência matemática."],
                    "pontos_atencao": [],
                    "recomendacao_estudo": "Exercícios de aprofundamento com frações mistas."
                },
                created_at=datetime.utcnow(),
            ),
            # Gabriel Ribeiro (aluno que errou 3 questões - alerta de risco de aprendizagem)
            QuizSubmission(
                quiz_id=q1.id,
                turma_id=turma1.id,
                email_aluno="gabriel.ribeiro@santosdumont.demo",
                nota_final=2.5,
                respostas_aluno=["1/2", "9/15", "15/20", "Seu amigo comeu mais"],  # Errou q1, q2, q4
                gabarito_oficial=gabarito_q1,
                feedback_ia={
                    "pontos_fortes": ["Engajamento em concluir todas as tentativas."],
                    "pontos_atencao": ["Confusão frequente na identificação de partes equivalentes e MDC."],
                    "recomendacao_estudo": "Recomendada intervenção presencial com material concreto e reforço guiado com o Tutor Socrático."
                },
                created_at=datetime.utcnow(),
            ),
        ]
        session.add_all(submissoes)

        # 10. REGISTROS DE USO DE IA (AUDITORIA NO ADMIN)
        usos = [
            ApiUsage(
                school_id=escola1.id,
                provider="grok",
                model="grok-2-latest",
                tokens_usados=14200,
                custo=0.284,
                descricao="Geração de Plano de Aula BNCC: Frações Equivalentes",
                created_at=datetime.utcnow(),
            ),
            ApiUsage(
                school_id=escola1.id,
                provider="grok",
                model="grok-2-latest",
                tokens_usados=8300,
                custo=0.166,
                descricao="Geração de Quiz Diagnóstico: Frações e Proporcionalidade",
                created_at=datetime.utcnow(),
            ),
            ApiUsage(
                school_id=escola1.id,
                provider="grok",
                model="grok-2-latest",
                tokens_usados=6000,
                custo=0.120,
                descricao="Correção pedagógica de 5 submissões com feedback formativo",
                created_at=datetime.utcnow(),
            ),
            ApiUsage(
                school_id=escola2.id,
                provider="groq",
                model="openai/gpt-oss-20b",
                tokens_usados=19200,
                custo=0.384,
                descricao="Plano e Avaliação de Língua Portuguesa",
                created_at=datetime.utcnow(),
            ),
        ]
        session.add_all(usos)

        # 11. USUÁRIOS DO SISTEMA
        from .auth import hash_password
        usuarios_demo = [
            User(nome="Admin Demo", email="admin@educollab.demo", senha_hash=hash_password("admin123"), tipo="administrador"),
            User(nome="Prof. Lucas Mendes", email="lucas.mendes@santosdumont.edu.br", senha_hash=hash_password("prof123"), tipo="professor"),
            User(nome="Professor Demo", email="professor@educollab.demo", senha_hash=hash_password("prof123"), tipo="professor"),
            User(nome="Cristiano Santos (Aluno Demo)", email="aluno@educollab.demo", senha_hash=hash_password("aluno123"), tipo="aluno"),
        ]
        session.add_all(usuarios_demo)

        session.commit()
        logger.info("=== BANCO DE DADOS POPULADO COM DADOS COERENTES E HOMOGÊNEOS COM SUCESSO! ===")

    _sync_store()


if __name__ == "__main__":
    reset_and_populate_db()
