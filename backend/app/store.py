from __future__ import annotations

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from .database import SessionLocal, School, Teacher, ClassRoom, Student, Plan, Quiz, ApiUsage, Subject, QuizSubmission, User
from .security import decrypt_secret, encrypt_secret

STORE = {
    "schools": [],
    "teachers": [],
    "classes": [],
    "students": [],
    "plans": [],
    "quizzes": [],
}


def _safe_decrypt_secret(value: str | None) -> str | None:
    if value is None or not str(value).strip():
        return None
    try:
        return decrypt_secret(value)
    except Exception:
        return str(value).strip()


def _criar_conta_acesso(session, nome: str, email: str, tipo: str) -> str | None:
    """Cria o login do usuário com uma senha provisória e a retorna.
    Retorna None se já existir uma conta com esse e-mail (nada é alterado)."""
    import secrets
    from .auth import hash_password

    if session.query(User).filter(User.email == email).first() is not None:
        return None
    senha_provisoria = f"edu-{secrets.token_hex(3)}"
    session.add(User(nome=nome, email=email, senha_hash=hash_password(senha_provisoria), tipo=tipo))
    return senha_provisoria


def _mensagem_credenciais(email: str, senha_provisoria: str | None) -> str:
    if senha_provisoria:
        return f" Acesso criado: login {email} · senha provisória {senha_provisoria}"
    return " (este e-mail já possuía uma conta de acesso)."



def _serialize_school(school: School) -> dict:
    return {
        "id": school.id,
        "nome": school.nome,
        "cidade": school.cidade,
        "estado": school.estado,
        "diretor": school.diretor,
        "api_key_ia": None,
        "api_key_configurada": bool(_safe_decrypt_secret(school.api_key_ia)),
        "provedor_ia": school.provedor_ia,
        "modelo_ia": school.modelo_ia,
        "tokens_usados": school.tokens_usados,
        "custo_total": round(float(school.custo_total or 0.0), 4),
        "uso_ia_ultima_data": school.uso_ia_ultima_data.isoformat() if school.uso_ia_ultima_data else None,
    }


def get_school_credentials(escola_id: int) -> dict | None:
    with SessionLocal() as session:
        escola = session.query(School).filter(School.id == int(escola_id)).first()
        if escola is None:
            return None
        return {
            "provedor_ia": escola.provedor_ia,
            "modelo_ia": escola.modelo_ia,
            "api_key_ia": _safe_decrypt_secret(escola.api_key_ia),
        }


def _serialize_teacher(teacher: Teacher) -> dict:
    return {
        "id": teacher.id,
        "nome": teacher.nome,
        "email": teacher.email,
        "disciplina": teacher.disciplina,
        "escola_id": teacher.escola_id,
    }


def _serialize_student(student: Student) -> dict:
    return {
        "id": student.id,
        "nome": student.nome,
        "email": student.email,
        "turma_id": student.turma_id,
    }


def _serialize_subject(subject: Subject) -> dict:
    return {
        "id": subject.id,
        "nome": subject.nome,
        "turma_id": subject.turma_id,
    }


def _serialize_class(turma: ClassRoom) -> dict:
    alunos = [
        _serialize_student(aluno)
        for aluno in (turma.students or [])
    ]
    disciplinas = [
        _serialize_subject(disciplina)
        for disciplina in sorted(turma.subjects or [], key=lambda item: item.id)
    ]
    professores = []
    if hasattr(turma, 'teachers') and turma.teachers:
        professores = [{"id": p.id, "nome": p.nome, "email": p.email, "disciplina": p.disciplina} for p in turma.teachers]
    elif turma.professor_id:
        # Fallback to single professor if teachers association is empty
        professores = [{"id": turma.professor_id}]

    return {
        "id": turma.id,
        "nome": turma.nome,
        "ano": turma.ano,
        "codigo": turma.codigo,
        "cor": turma.cor or "bg-blue-500",
        "escola_id": turma.escola_id,
        "professor_id": turma.professor_id, # maintain retrocompatibility
        "professores": professores,
        "alunos": alunos,
        "disciplinas": disciplinas,
    }


def _turma_query(session):
    return session.query(ClassRoom).options(
        joinedload(ClassRoom.students),
        joinedload(ClassRoom.subjects),
    )


def _serialize_plan(plan: Plan) -> dict:
    return {
        "id": plan.id,
        "tema": plan.tema,
        "turma_id": plan.turma_id,
        "plano": plan.conteudo,
    }


def _serialize_quiz(quiz: Quiz) -> dict:
    return {
        "id": quiz.id,
        "tema": quiz.tema,
        "objetivo": quiz.objetivo,
        "quantidade": quiz.quantidade,
        "turma_id": quiz.turma_id,
        "status": getattr(quiz, "status", "publicado") or "publicado",
        "created_at": quiz.created_at.isoformat() if getattr(quiz, "created_at", None) else None,
        "quiz": quiz.conteudo,
    }


def _serialize_quiz_submission(item: QuizSubmission) -> dict:
    return {
        "id": item.id,
        "quiz_id": item.quiz_id,
        "turma_id": item.turma_id,
        "aluno_id": item.aluno_id,
        "email_aluno": item.email_aluno,
        "nota_final": round(float(item.nota_final or 0.0), 1),
        "respostas_aluno": item.respostas_aluno,
        "gabarito_oficial": item.gabarito_oficial,
        "feedback_ia": item.feedback_ia,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


def _sync_store():
    with SessionLocal() as session:
        STORE["schools"] = [_serialize_school(item) for item in session.query(School).all()]
        STORE["teachers"] = [_serialize_teacher(item) for item in session.query(Teacher).all()]
        STORE["classes"] = [_serialize_class(item) for item in session.query(ClassRoom).all()]
        STORE["students"] = [_serialize_student(item) for item in session.query(Student).all()]
        STORE["plans"] = [_serialize_plan(item) for item in session.query(Plan).all()]
        STORE["quizzes"] = [_serialize_quiz(item) for item in session.query(Quiz).all()]


def next_id(collection_name: str) -> int:
    with SessionLocal() as session:
        if collection_name == "schools":
            max_id = session.query(func.max(School.id)).scalar() or 0
        elif collection_name == "teachers":
            max_id = session.query(func.max(Teacher.id)).scalar() or 0
        elif collection_name == "classes":
            max_id = session.query(func.max(ClassRoom.id)).scalar() or 0
        elif collection_name == "students":
            max_id = session.query(func.max(Student.id)).scalar() or 0
        elif collection_name == "plans":
            max_id = session.query(func.max(Plan.id)).scalar() or 0
        elif collection_name == "quizzes":
            max_id = session.query(func.max(Quiz.id)).scalar() or 0
        else:
            max_id = 0
    return max_id + 1


def reset_store():
    with SessionLocal() as session:
        session.query(ApiUsage).delete()
        session.query(Quiz).delete()
        session.query(Plan).delete()
        session.query(Student).delete()
        session.query(Subject).delete()
        session.query(ClassRoom).delete()
        session.query(Teacher).delete()
        session.query(School).delete()
        session.commit()
    _sync_store()


def _get_school_or_raise(escola_id: int) -> School:
    with SessionLocal() as session:
        escola = session.query(School).filter(School.id == int(escola_id)).first()
    if escola is None:
        raise ValueError("Escola não encontrada.")
    return escola


def _get_professor_or_raise(professor_id: int) -> Teacher:
    with SessionLocal() as session:
        professor = session.query(Teacher).filter(Teacher.id == int(professor_id)).first()
    if professor is None:
        raise ValueError("Professor não encontrado.")
    return professor


def _get_turma_or_raise(turma_id: int) -> ClassRoom:
    with SessionLocal() as session:
        turma = _turma_query(session).filter(ClassRoom.id == int(turma_id)).first()
    if turma is None:
        raise ValueError("Turma não encontrada.")
    return turma


def _normalizar_disciplinas(valores) -> list[str]:
    if valores is None:
        return []
    if isinstance(valores, str):
        valores = [item.strip() for item in valores.replace(",", "\n").split("\n")]
    nomes: list[str] = []
    vistos: set[str] = set()
    for item in valores:
        nome = str(item or "").strip()
        chave = nome.lower()
        if not nome or chave in vistos:
            continue
        vistos.add(chave)
        nomes.append(nome)
    return nomes


def create_school(payload: dict) -> dict:
    with SessionLocal() as session:
        escola = School(
            nome=payload["nome"],
            cidade=payload["cidade"],
            estado=payload["estado"],
            diretor=payload.get("diretor") or "Não informado",
            api_key_ia=encrypt_secret((payload.get("api_key_ia") or "").strip()),
            provedor_ia=(payload.get("provedor_ia") or "grok").strip() or "grok",
            modelo_ia=(payload.get("modelo_ia") or "").strip() or None,
        )
        session.add(escola)
        session.commit()
        session.refresh(escola)
        item = _serialize_school(escola)
    _sync_store()
    return item


def create_teacher(payload: dict) -> dict:
    escola_id = int(payload["escola_id"])
    _get_school_or_raise(escola_id)
    email = str(payload["email"]).strip().lower()

    with SessionLocal() as session:
        professor_existente = session.query(Teacher).filter(Teacher.email == email).first()
        if professor_existente is not None:
            raise ValueError("Já existe um professor cadastrado com este e-mail.")

        professor = Teacher(
            nome=payload["nome"],
            email=email,
            disciplina=payload["disciplina"],
            escola_id=escola_id,
        )
        session.add(professor)
        senha_provisoria = _criar_conta_acesso(session, payload["nome"], email, "professor")
        session.commit()
        session.refresh(professor)
        item = _serialize_teacher(professor)
        item["senha_provisoria"] = senha_provisoria
    _sync_store()
    return item


def create_class(payload: dict) -> dict:
    escola_id = payload.get("escola_id")
    professor_id = payload.get("professor_id")

    if escola_id is not None:
        escola_id = int(escola_id)
        _get_school_or_raise(escola_id)
    if professor_id is not None:
        professor = _get_professor_or_raise(int(professor_id))
        if escola_id is None:
            escola_id = professor.escola_id
        if professor.escola_id != escola_id:
            raise ValueError("Professor não pertence à escola informada para a turma.")
    elif escola_id is not None:
        with SessionLocal() as session:
            professor = session.query(Teacher).filter(Teacher.escola_id == escola_id).first()
            if professor is None:
                professor = Teacher(
                    nome="Professor Demo",
                    email=f"professor.{escola_id}@educollab.demo",
                    disciplina="Geral",
                    escola_id=escola_id,
                )
                session.add(professor)
                session.commit()
                session.refresh(professor)
            professor_id = professor.id
    else:
        with SessionLocal() as session:
            escola = session.query(School).order_by(School.id.asc()).first()
            if escola is None:
                raise ValueError("Não há escola cadastrada para criar a turma.")
            escola_id = escola.id
            professor = session.query(Teacher).filter(Teacher.escola_id == escola_id).first()
            if professor is None:
                professor = Teacher(
                    nome="Professor Demo",
                    email=f"professor.{escola_id}@educollab.demo",
                    disciplina="Geral",
                    escola_id=escola_id,
                )
                session.add(professor)
                session.commit()
                session.refresh(professor)
            professor_id = professor.id

    disciplinas = _normalizar_disciplinas(payload.get("disciplinas"))

    with SessionLocal() as session:
        turma = ClassRoom(
            nome=payload["nome"],
            ano=payload["ano"],
            codigo=str(payload["codigo"]).upper(),
            cor=payload.get("cor") or "bg-blue-500",
            escola_id=escola_id,
            professor_id=professor_id,
        )
        if professor_id is not None:
            prof = session.query(Teacher).filter(Teacher.id == professor_id).first()
            if prof:
                turma.teachers.append(prof)
        session.add(turma)
        session.flush()
        for nome in disciplinas:
            session.add(Subject(nome=nome, turma_id=turma.id))
        session.commit()
        turma = _turma_query(session).filter(ClassRoom.id == turma.id).first()
        item = _serialize_class(turma)
    _sync_store()
    return item


def add_subject_to_class(turma_id: int, nome: str) -> dict:
    turma_id = int(turma_id)
    _get_turma_or_raise(turma_id)
    nomes = _normalizar_disciplinas([nome])
    if not nomes:
        raise ValueError("Informe o nome da disciplina.")
    nome_disciplina = nomes[0]

    with SessionLocal() as session:
        existente = (
            session.query(Subject)
            .filter(Subject.turma_id == turma_id, func.lower(Subject.nome) == nome_disciplina.lower())
            .first()
        )
        if existente is not None:
            raise ValueError("Esta disciplina já está cadastrada na turma.")
        session.add(Subject(nome=nome_disciplina, turma_id=turma_id))
        session.commit()
        turma = _turma_query(session).filter(ClassRoom.id == turma_id).first()
        item = _serialize_class(turma)
    _sync_store()
    return item


def create_student(payload: dict) -> dict:
    turma_id = int(payload["turma_id"])
    _get_turma_or_raise(turma_id)
    email = str(payload["email"]).strip().lower()

    with SessionLocal() as session:
        aluno_existente = (
            session.query(Student)
            .filter(Student.email == email, Student.turma_id == turma_id)
            .first()
        )
        if aluno_existente is not None:
            raise ValueError("Este aluno já está matriculado nesta turma.")

        aluno = Student(
            nome=payload["nome"],
            email=email,
            turma_id=turma_id,
        )
        session.add(aluno)
        senha_provisoria = _criar_conta_acesso(session, payload["nome"], email, "aluno")
        session.commit()
        session.refresh(aluno)
        item = _serialize_student(aluno)
        item["senha_provisoria"] = senha_provisoria
    _sync_store()
    return item


def enroll_student_by_code(codigo: str, email_aluno: str, nome_aluno: str | None = None) -> dict:
    code = str(codigo or "").strip().upper()
    if not code:
        raise ValueError("Informe o código da turma.")
    email = str(email_aluno or "").strip().lower()
    if not email:
        raise ValueError("Informe o e-mail do aluno.")

    with SessionLocal() as session:
        turma = _turma_query(session).filter(func.upper(ClassRoom.codigo) == code).first()
        if turma is None:
            raise ValueError(f"Nenhuma turma encontrada com o código '{code}'.")

        ja_matriculado = (
            session.query(Student)
            .filter(Student.email == email, Student.turma_id == turma.id)
            .first()
        )
        if ja_matriculado is not None:
            raise ValueError(f"Você já está matriculado na turma '{turma.nome}'.")

        nome_informado = str(nome_aluno).strip() if (nome_aluno and str(nome_aluno).strip()) else ""
        matricula_anterior = session.query(Student).filter(Student.email == email).first()
        nome_final = nome_informado or (matricula_anterior.nome if matricula_anterior else "Aluno Demo")

        session.add(Student(nome=nome_final, email=email, turma_id=turma.id))
        session.commit()
        turma = _turma_query(session).filter(ClassRoom.id == turma.id).first()
        item = _serialize_class(turma)

    _sync_store()
    return item


def list_student_classes(email_aluno: str) -> list[dict]:
    email = str(email_aluno or "").strip().lower()
    if not email:
        return []

    with SessionLocal() as session:
        matriculas = session.query(Student).filter(Student.email == email).order_by(Student.id).all()
        turma_ids = [m.turma_id for m in matriculas if m.turma_id]
        if not turma_ids:
            return []

        turmas = _turma_query(session).filter(ClassRoom.id.in_(turma_ids)).all()
        turmas_por_id = {turma.id: turma for turma in turmas}
        return [_serialize_class(turmas_por_id[tid]) for tid in turma_ids if tid in turmas_por_id]


def list_schools() -> list[dict]:
    with SessionLocal() as session:
        return [_serialize_school(item) for item in session.query(School).all()]


def list_classes() -> list[dict]:
    with SessionLocal() as session:
        turmas = _turma_query(session).all()
        return [_serialize_class(turma) for turma in turmas]


def list_students() -> list[dict]:
    with SessionLocal() as session:
        return [_serialize_student(item) for item in session.query(Student).all()]


def get_school_by_id(escola_id: int) -> dict | None:
    with SessionLocal() as session:
        escola = session.query(School).filter(School.id == int(escola_id)).first()
        if escola is None:
            return None
        return _serialize_school(escola)


def get_summary() -> dict:
    with SessionLocal() as session:
        total_tokens = session.query(func.coalesce(func.sum(School.tokens_usados), 0)).scalar() or 0
        total_custo = session.query(func.coalesce(func.sum(School.custo_total), 0.0)).scalar() or 0.0
        escolas = session.query(School).all()
        escolas_com_ia = sum(1 for e in escolas if bool(_safe_decrypt_secret(e.api_key_ia)))
        total_planos = session.query(Plan).count()
        total_quizzes = session.query(Quiz).count()
        total_submissoes = session.query(QuizSubmission).count()

        return {
            "total_escolas": len(escolas),
            "total_professores": session.query(Teacher).count(),
            "total_turmas": session.query(ClassRoom).count(),
            "total_alunos": session.query(func.count(func.distinct(Student.email))).scalar() or 0,
            "total_tokens": int(total_tokens),
            "total_custo": round(float(total_custo), 4),
            "escolas_com_ia": escolas_com_ia,
            "escolas_sem_ia": len(escolas) - escolas_com_ia,
            "total_planos": total_planos,
            "total_quizzes": total_quizzes,
            "total_submissoes": total_submissoes,
        }



def configurar_ia_escola(escola_id: int, payload: dict) -> dict:
    with SessionLocal() as session:
        escola = session.query(School).filter(School.id == int(escola_id)).first()
        if escola is None:
            raise ValueError("Escola não encontrada.")

        api_key = (payload.get("api_key_ia") or "").strip()
        provedor = (payload.get("provedor_ia") or "grok").strip() or "grok"
        modelo = (payload.get("modelo_ia") or "").strip() or None

        escola.api_key_ia = encrypt_secret(api_key) if api_key else None
        escola.provedor_ia = provedor
        escola.modelo_ia = modelo
        session.commit()
        session.refresh(escola)
        item = _serialize_school(escola)
    _sync_store()
    return item


def remover_configuracao_ia_escola(escola_id: int) -> dict:
    with SessionLocal() as session:
        escola = session.query(School).filter(School.id == int(escola_id)).first()
        if escola is None:
            raise ValueError("Escola não encontrada.")

        escola.api_key_ia = None
        escola.provedor_ia = "grok"
        escola.modelo_ia = None
        session.commit()
        session.refresh(escola)
        item = _serialize_school(escola)
    _sync_store()
    return item


def registrar_uso_api_escola(escola_id: int, provider: str, model: str | None, tokens_usados: int, custo: float, descricao: str) -> dict | None:
    if escola_id is None:
        return None

    with SessionLocal() as session:
        escola = session.query(School).filter(School.id == int(escola_id)).first()
        if escola is None:
            return None

        tokens = max(int(tokens_usados or 0), 0)
        custo_total = float(custo or 0.0)
        escola.tokens_usados = (escola.tokens_usados or 0) + tokens
        escola.custo_total = float(escola.custo_total or 0.0) + custo_total
        escola.uso_ia_ultima_data = datetime.utcnow()
        escola.provedor_ia = provider or escola.provedor_ia or "grok"
        if model:
            escola.modelo_ia = model

        consumo = ApiUsage(
            school_id=escola.id,
            provider=provider or "grok",
            model=model,
            tokens_usados=tokens,
            custo=custo_total,
            descricao=descricao,
            created_at=datetime.utcnow(),
        )
        session.add(consumo)
        session.commit()
        session.refresh(escola)
        retorno = _serialize_school(escola)
    _sync_store()
    return retorno


def get_school_uso_ia(escola_id: int) -> dict:
    with SessionLocal() as session:
        escola = session.query(School).filter(School.id == int(escola_id)).first()
        if escola is None:
            raise ValueError("Escola não encontrada.")

        consumos = session.query(ApiUsage).filter(ApiUsage.school_id == escola.id).order_by(ApiUsage.created_at.desc()).all()
        total_tokens = sum(item.tokens_usados for item in consumos)
        total_custo = sum(float(item.custo or 0.0) for item in consumos)
        return {
            "escola_id": escola.id,
            "nome": escola.nome,
            "provedor_ia": escola.provedor_ia,
            "modelo_ia": escola.modelo_ia,
            "totais": {
                "tokens": int(total_tokens),
                "custo": round(float(total_custo), 4),
                "registros": len(consumos),
            },
            "logs": [
                {
                    "id": item.id,
                    "provider": item.provider,
                    "model": item.model,
                    "tokens_usados": item.tokens_usados,
                    "custo": round(float(item.custo or 0.0), 4),
                    "descricao": item.descricao,
                    "created_at": item.created_at.isoformat() if item.created_at else None,
                }
                for item in consumos
            ],
        }


def create_plan_record(tema: str, turma_id: int | None, plano: dict) -> dict:
    with SessionLocal() as session:
        registro = Plan(tema=tema, turma_id=turma_id, conteudo=plano)
        session.add(registro)
        session.commit()
        session.refresh(registro)
        item = _serialize_plan(registro)
    _sync_store()
    return item


def create_quiz_record(tema: str, objetivo: str, quantidade: int, turma_id: int | None, quiz: dict) -> dict:
    with SessionLocal() as session:
        registro = Quiz(tema=tema, objetivo=objetivo, quantidade=quantidade, turma_id=turma_id, conteudo=quiz, status="rascunho")
        session.add(registro)
        session.commit()
        session.refresh(registro)
        item = _serialize_quiz(registro)
    _sync_store()
    return item


def get_conteudo_por_turma(turma_id: int, somente_publicados: bool = False) -> dict:
    with SessionLocal() as session:
        turma = session.query(ClassRoom).filter(ClassRoom.id == int(turma_id)).first()
        if turma is None:
            raise ValueError("Turma não encontrada.")

        planos = [
            _serialize_plan(item)
            for item in session.query(Plan).filter(Plan.turma_id == int(turma_id)).order_by(Plan.id.desc()).all()
        ]
        quiz_query = session.query(Quiz).filter(Quiz.turma_id == int(turma_id))
        if somente_publicados:
            quiz_query = quiz_query.filter(Quiz.status == 'publicado')
        quizzes = [_serialize_quiz(item) for item in quiz_query.order_by(Quiz.id.desc()).all()]

        return {
            "turma_id": int(turma_id),
            "turma_nome": turma.nome,
            "planos": planos,
            "quizzes": quizzes,
        }


def get_conteudo_por_aluno(email_aluno: str) -> dict:
    email = str(email_aluno or "").strip().lower()
    if not email:
        raise ValueError("E-mail do aluno não informado.")

    with SessionLocal() as session:
        matriculas = session.query(Student).filter(Student.email == email).order_by(Student.id).all()
        if not matriculas:
            primeira_turma = session.query(ClassRoom).first()
            if primeira_turma:
                return get_conteudo_por_turma(int(primeira_turma.id))
            return {
                "turma_id": None,
                "turma_nome": "Geral",
                "planos": [],
                "quizzes": [],
            }
        turma_ids = [m.turma_id for m in matriculas]

    if len(turma_ids) == 1:
        return get_conteudo_por_turma(int(turma_ids[0]))

    planos: list[dict] = []
    quizzes: list[dict] = []
    nomes: list[str] = []
    for turma_id in turma_ids:
        conteudo = get_conteudo_por_turma(int(turma_id))
        nomes.append(conteudo["turma_nome"])
        planos.extend({**item, "turma_nome": conteudo["turma_nome"]} for item in conteudo["planos"])
        quizzes.extend({**item, "turma_nome": conteudo["turma_nome"]} for item in conteudo["quizzes"])

    return {
        "turma_id": int(turma_ids[0]),
        "turma_nome": " + ".join(nomes),
        "planos": planos,
        "quizzes": quizzes,
    }


def dashboard_professor_summary() -> dict:
    dados = get_summary()
    with SessionLocal() as session:
        total_planos = session.query(Plan).count()
        total_quizzes = session.query(Quiz).count()

    return {
        "total_turmas": dados["total_turmas"],
        "total_alunos": dados["total_alunos"],
        "total_planos": total_planos,
        "total_quizzes": total_quizzes,
        "total_tokens": dados.get("total_tokens", 0),
        "total_custo": dados.get("total_custo", 0.0),
        "turmas": list_classes(),
    }


def create_quiz_submission(payload: dict) -> dict:
    email = str(payload.get("email_aluno") or "").strip().lower()
    turma_id = payload.get("turma_id")
    quiz_id = payload.get("quiz_id")
    nota_final = float(payload.get("nota_final") or 0.0)
    respostas_aluno = payload.get("respostas_aluno") or []
    gabarito_oficial = payload.get("gabarito_oficial") or []
    feedback_ia = payload.get("feedback_ia") or {}

    with SessionLocal() as session:
        valid_quiz_id = None
        if quiz_id is not None:
            quiz = session.query(Quiz).filter(Quiz.id == int(quiz_id)).first()
            if quiz:
                valid_quiz_id = quiz.id
                if not turma_id and quiz.turma_id:
                    turma_id = quiz.turma_id

        aluno_id = None
        if email:
            matriculas = session.query(Student).filter(Student.email == email).order_by(Student.id).all()
            aluno = None
            if turma_id:
                aluno = next((m for m in matriculas if m.turma_id == int(turma_id)), None)
            if aluno is None and matriculas:
                aluno = matriculas[0]
            if aluno:
                aluno_id = aluno.id
                if not turma_id:
                    turma_id = aluno.turma_id

        valid_turma_id = None
        if turma_id is not None:
            turma = session.query(ClassRoom).filter(ClassRoom.id == int(turma_id)).first()
            if turma:
                valid_turma_id = turma.id

        valid_aluno_id = None
        if aluno_id is not None:
            aluno_row = session.query(Student).filter(Student.id == int(aluno_id)).first()
            if aluno_row:
                valid_aluno_id = aluno_row.id

        submission = QuizSubmission(
            quiz_id=valid_quiz_id,
            turma_id=valid_turma_id,
            aluno_id=valid_aluno_id,
            email_aluno=email,
            nota_final=nota_final,
            respostas_aluno=respostas_aluno,
            gabarito_oficial=gabarito_oficial,
            feedback_ia=feedback_ia,
            created_at=datetime.utcnow(),
        )
        session.add(submission)
        session.commit()
        session.refresh(submission)
        item = _serialize_quiz_submission(submission)
    return item


def list_student_submissions(email_aluno: str) -> list[dict]:
    email = str(email_aluno or "").strip().lower()
    with SessionLocal() as session:
        items = (
            session.query(QuizSubmission)
            .filter(QuizSubmission.email_aluno == email)
            .order_by(QuizSubmission.created_at.desc())
            .all()
        )
        return [_serialize_quiz_submission(sub) for sub in items]


def update_quiz_status(quiz_id: int, novo_status: str) -> dict:
    with SessionLocal() as session:
        quiz = session.query(Quiz).filter(Quiz.id == int(quiz_id)).first()
        if quiz is None:
            raise ValueError("Quiz não encontrado.")
        quiz.status = novo_status
        session.commit()
        session.refresh(quiz)
        item = _serialize_quiz(quiz)
    _sync_store()
    return item


def get_turma_quiz_analytics(turma_id: int, quiz_id: int | None = None) -> dict:
    with SessionLocal() as session:
        turma = session.query(ClassRoom).filter(ClassRoom.id == int(turma_id)).first()
        if turma is None:
            raise ValueError("Turma não encontrada.")

        query = session.query(QuizSubmission).filter(QuizSubmission.turma_id == int(turma_id))
        if quiz_id is not None:
            query = query.filter(QuizSubmission.quiz_id == int(quiz_id))

        submissions = query.order_by(QuizSubmission.created_at.desc()).all()
        quizzes = session.query(Quiz).filter(Quiz.turma_id == int(turma_id)).all()

        total_submissoes = len(submissions)
        media_turma = (sum(sub.nota_final for sub in submissions) / total_submissoes) if total_submissoes > 0 else 0.0

        erros_por_questao = []
        if total_submissoes > 0:
            max_questoes = max((len(sub.gabarito_oficial or []) for sub in submissions), default=0)
            for q_idx in range(max_questoes):
                erros = 0
                total_respondidas = 0
                for sub in submissions:
                    respostas = sub.respostas_aluno or []
                    gabarito = sub.gabarito_oficial or []
                    if q_idx < len(gabarito) and q_idx < len(respostas):
                        total_respondidas += 1
                        if respostas[q_idx] != gabarito[q_idx]:
                            erros += 1
                taxa_erro = round((erros / total_respondidas * 100), 1) if total_respondidas > 0 else 0.0
                erros_por_questao.append({
                    "questao_numero": q_idx + 1,
                    "total_erros": erros,
                    "total_tentativas": total_respondidas,
                    "taxa_erro_percentual": taxa_erro,
                })

        alunos_em_atencao = []
        for sub in submissions:
            if sub.nota_final < 6.0:
                alunos_em_atencao.append({
                    "email": sub.email_aluno,
                    "nota": sub.nota_final,
                    "data": sub.created_at.isoformat() if sub.created_at else None,
                })

        return {
            "turma_id": turma.id,
            "turma_nome": turma.nome,
            "total_submissoes": total_submissoes,
            "media_turma": round(media_turma, 1),
            "total_quizzes": len(quizzes),
            "erros_por_questao": erros_por_questao,
            "alunos_em_atencao": alunos_em_atencao[:5],
            "ultimas_submissoes": [_serialize_quiz_submission(s) for s in submissions[:10]],
        }



def add_teacher_to_class(turma_id: int, email: str) -> dict:
    email = str(email or "").strip().lower()
    with SessionLocal() as session:
        turma = session.query(ClassRoom).filter(ClassRoom.id == int(turma_id)).first()
        if not turma:
            raise ValueError("Turma não encontrada.")
        
        prof = session.query(Teacher).filter(Teacher.email == email).first()
        if not prof:
            raise ValueError("Professor não encontrado com esse e-mail.")
            
        if prof.escola_id != turma.escola_id:
            raise ValueError("O professor não pertence à mesma escola desta turma.")
            
        already_in = any(p.id == prof.id for p in turma.teachers)
        if not already_in:
            turma.teachers.append(prof)
            session.commit()
            
        session.refresh(turma)
        item = _serialize_class(turma)
    _sync_store()
    return item
