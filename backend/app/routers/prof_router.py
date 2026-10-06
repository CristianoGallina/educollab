from fastapi import APIRouter, Depends, Body, HTTPException, Query, status
from ..dependencies import verificar_papel_professor
from ..schemas import AlunoCreate, DisciplinaCreate, PlanoAulaCreate, QuizCreate, TurmaCreate, RegenerarQuestaoRequest
from ..services import gerar_plano_ia, gerar_quiz_ia, regenerar_questao_ia, analisar_raio_x_turma_ia
from ..store import (
    add_subject_to_class,
    create_class,
    create_student,
    list_classes,
    add_teacher_to_class,
    create_plan_record,
    create_quiz_record,
    dashboard_professor_summary,
    _get_turma_or_raise,
    registrar_uso_api_escola,
    get_conteudo_por_turma,
    get_turma_quiz_analytics,
    update_quiz_status,
)
import logging

router = APIRouter(prefix="/api/v1/professor", tags=["Fluxo do Professor / Motor IA"])


@router.get("/dashboard", dependencies=[Depends(verificar_papel_professor)])
async def dashboard_professor():
    return dashboard_professor_summary()


@router.get("/turma/{turma_id}/conteudo", dependencies=[Depends(verificar_papel_professor)])
async def listar_conteudo_turma_professor(turma_id: int):
    try:
        return get_conteudo_por_turma(int(turma_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/criar-turma", dependencies=[Depends(verificar_papel_professor)])
async def criar_turma(payload: dict = Body(...)):
    nome = str(payload.get("nome") or "Nova Turma").strip()
    ano = str(payload.get("ano") or "Ensino Fundamental").strip()
    codigo = str(payload.get("codigo") or "TURMA-001").strip().upper()
    cor = str(payload.get("cor") or "bg-blue-500").strip()
    escola_id = payload.get("escola_id")
    professor_id = payload.get("professor_id")

    try:
        turma = create_class({
            "nome": nome,
            "ano": ano,
            "codigo": codigo,
            "cor": cor,
            "escola_id": escola_id,
            "professor_id": professor_id,
            "disciplinas": payload.get("disciplinas") or [],
        })
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    logging.info(f"PROFESSOR | Turma criada: {nome} ({codigo})")
    return {
        "status": "sucesso",
        "mensagem": "Turma criada com sucesso.",
        "turma": turma,
    }


@router.post("/alunos", dependencies=[Depends(verificar_papel_professor)])
async def cadastrar_aluno(payload: AlunoCreate = Body(...)):
    try:
        aluno = create_student({
            "nome": payload.nome,
            "email": str(payload.email),
            "turma_id": payload.turma_id,
        })
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"status": "sucesso", "mensagem": "Aluno cadastrado com sucesso.", "aluno": aluno}


@router.post("/turma/{turma_id}/disciplinas", dependencies=[Depends(verificar_papel_professor)])
async def cadastrar_disciplina(turma_id: int, payload: DisciplinaCreate = Body(...)):
    try:
        turma = add_subject_to_class(turma_id, payload.nome)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"status": "sucesso", "mensagem": "Disciplina adicionada à turma.", "turma": turma}


@router.post("/gerar-plano", dependencies=[Depends(verificar_papel_professor)])
async def gerar_plano(payload: PlanoAulaCreate = Body(...)):
    if payload.turma_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="É obrigatório informar a turma_id para gerar o plano.")
    try:
        turma = _get_turma_or_raise(payload.turma_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    objetivos = payload.objetivos or ["Reconhecer os conceitos principais do tema.", "Aplicar o conteúdo em exercícios simples."]
    plano = await gerar_plano_ia(
        tema_aula=payload.tema_aula,
        objetivos=objetivos,
        ano=payload.ano or "Ensino Fundamental",
        nivel=payload.nivel or "Básico",
        duracao=payload.duracao or "40 min",
        disciplina=payload.disciplina,
        habilidades_bncc=payload.habilidades_bncc,
        escola_id=turma.escola_id,
    )
    if payload.turma_id is not None:
        plano["turma_id"] = payload.turma_id
        plano["material_gerado"] = [
            "Plano de aula",
            "Atividades de apoio",
            "Ficha de revisão para a turma",
            "Avaliação da aula"
        ]
    aviso_ia = plano.pop("aviso_ia", None)
    create_plan_record(payload.tema_aula, payload.turma_id, plano)
    tokens_estimados = max(80, len(str(plano).encode('utf-8')) // 4)
    custo_estimado = tokens_estimados * 0.00002
    registrar_uso_api_escola(turma.escola_id, "grok", "grok-2-latest", tokens_estimados, custo_estimado, f"Plano de aula: {payload.tema_aula}")
    return {"status": "sucesso", "mensagem": "Plano de aula gerado com sucesso.", "plano": plano, "aviso_ia": aviso_ia}


@router.post("/gerar-quiz", dependencies=[Depends(verificar_papel_professor)])
async def gerar_quiz(payload: QuizCreate = Body(...)):
    if payload.turma_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="É obrigatório informar a turma_id para gerar o quiz.")
    try:
        turma = _get_turma_or_raise(payload.turma_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    quiz = await gerar_quiz_ia(
        tema=payload.tema,
        objetivo=payload.objetivo,
        quantidade=payload.quantidade,
        nivel=payload.nivel,
        disciplina=payload.disciplina,
        habilidades_bncc=payload.habilidades_bncc,
        escola_id=turma.escola_id,
    )
    aviso_ia = quiz.pop("aviso_ia", None)
    if payload.turma_id is not None:
        quiz["turma_id"] = payload.turma_id
    registro = create_quiz_record(payload.tema, payload.objetivo, payload.quantidade, payload.turma_id, quiz)
    quiz["id"] = registro.get("id")
    tokens_estimados = max(80, len(str(quiz).encode('utf-8')) // 4)
    custo_estimado = tokens_estimados * 0.00002
    registrar_uso_api_escola(turma.escola_id, "grok", "grok-2-latest", tokens_estimados, custo_estimado, f"Quiz: {payload.tema}")
    return {"status": "sucesso", "mensagem": "Quiz gerado com sucesso.", "quiz": quiz, "quiz_id": registro.get("id"), "aviso_ia": aviso_ia}


@router.post("/regenerar-questao", dependencies=[Depends(verificar_papel_professor)])
async def regenerar_questao(payload: RegenerarQuestaoRequest = Body(...)):
    escola_id = None
    if payload.turma_id:
        try:
            turma = _get_turma_or_raise(payload.turma_id)
            escola_id = turma.escola_id
        except Exception:
            pass

    nova_questao = await regenerar_questao_ia(
        tema=payload.tema,
        objetivo=payload.objetivo or "Aplicar os conceitos do tema.",
        nivel=payload.nivel or "Básico",
        pergunta_anterior=payload.pergunta_anterior,
        escola_id=escola_id,
    )
    return {"status": "sucesso", "questao": nova_questao}


@router.post("/aprovar-quiz", dependencies=[Depends(verificar_papel_professor)])
async def aprovar_quiz(payload: dict = Body(...)):
    turma_id = payload.get("turma_id")
    if turma_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="É obrigatório informar a turma_id para aprovar o quiz.")

    try:
        turma = list_classes()
        turma_atual = next((item for item in turma if int(item["id"]) == int(turma_id)), None)
        if turma_atual is None:
            raise ValueError("Turma não encontrada.")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    quiz_payload = payload.get("quiz") or {
        "tema": payload.get("tema") or "Tema da aula",
        "objetivo": payload.get("objetivo") or "Aplicar os conceitos do tema.",
        "perguntas": [],
    }
    aprovado = bool(payload.get("aprovado", False))
    quiz_id = payload.get("quiz_id") or (quiz_payload.get("id") if isinstance(quiz_payload, dict) else None)

    if quiz_id:
        try:
            update_quiz_status(int(quiz_id), "publicado" if aprovado else "rascunho")
        except Exception:
            pass

    if aprovado:
        return {
            "status": "aprovado",
            "mensagem": "Quiz aprovado e atribuído à turma dos alunos correspondentes.",
            "turma_id": int(turma_id),
            "turma_nome": turma_atual.get("nome"),
            "alunos_na_turma": len(turma_atual.get("alunos") or []),
            "quiz": quiz_payload,
        }

    return {
        "status": "revisao",
        "mensagem": "O professor pediu ajustes. Você pode regenerar questões ou editar o conteúdo.",
        "turma_id": int(turma_id),
        "turma_nome": turma_atual.get("nome"),
        "alunos_na_turma": len(turma_atual.get("alunos") or []),
        "quiz": quiz_payload,
    }


@router.get("/turma/{turma_id}/raio-x-quiz", dependencies=[Depends(verificar_papel_professor)])
async def raio_x_turma(turma_id: int, quiz_id: int | None = Query(default=None)):
    try:
        turma = _get_turma_or_raise(turma_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    analytics = get_turma_quiz_analytics(int(turma_id), quiz_id=int(quiz_id) if quiz_id else None)
    tema = "Avaliações da Turma"
    if quiz_id:
        conteudo = get_conteudo_por_turma(int(turma_id))
        matching_quiz = next((q for q in conteudo.get("quizzes", []) if q.get("id") == int(quiz_id)), None)
        if matching_quiz:
            tema = matching_quiz.get("tema", tema)

    diagnostico_ia = await analisar_raio_x_turma_ia(
        turma_nome=turma.nome,
        tema_quiz=tema,
        total_alunos=analytics["total_submissoes"],
        media_turma=analytics["media_turma"],
        erros_por_questao=analytics["erros_por_questao"],
        escola_id=turma.escola_id,
    )
    analytics["diagnostico_ia"] = diagnostico_ia
    return {"status": "sucesso", "analytics": analytics}


@router.post("/processar-recomendacao", dependencies=[Depends(verificar_papel_professor)])
async def disparar_motor_recomendacao(payload: dict = Body(...)):
    tema = str(payload.get("tema_aula") or payload.get("tema") or "Aula de reforço").strip()
    objetivos = payload.get("objetivos") or []
    if isinstance(objetivos, str):
        objetivos_lista = [item.strip() for item in objetivos.split("\n") if item.strip()]
    elif isinstance(objetivos, list):
        objetivos_lista = [str(item).strip() for item in objetivos if str(item).strip()]
    else:
        objetivos_lista = ["Reconhecer os conceitos principais do tema."]

    turma_id = payload.get("turma_id")
    if turma_id is not None:
        try:
            _get_turma_or_raise(int(turma_id))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    plano = await gerar_plano_ia(tema, objetivos_lista, str(payload.get("ano") or "Ensino Fundamental"), str(payload.get("nivel") or "Básico"), str(payload.get("duracao") or "40 min"))
    if turma_id is not None:
        plano["turma_id"] = int(turma_id)
        plano["material_gerado"] = [
            "Plano de aula",
            "Atividades de apoio",
            "Ficha de revisão para a turma",
            "Avaliação da aula"
        ]
    create_plan_record(tema, int(turma_id) if turma_id is not None else None, plano)

    logging.info(f"PROFESSOR | Plano gerado para o tema: {tema} na turma {turma_id}")

    return {
        "status": "sucesso",
        "mensagem": "Plano de aula gerado com sucesso.",
        "plano": plano,
    }

@router.post("/turma/{turma_id}/professores", dependencies=[Depends(verificar_papel_professor)])
async def adicionar_professor_turma(turma_id: int, payload: dict = Body(...)):
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail do professor é obrigatório.")
    try:
        turma = add_teacher_to_class(turma_id, email)
        return {"status": "sucesso", "mensagem": "Professor adicionado à turma.", "turma": turma}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

from pydantic import BaseModel
class CopilotoChatRequest(BaseModel):
    mensagem: str
    historico: list = []

@router.post("/chat-copiloto")
async def chat_copiloto_endpoint(
    req: CopilotoChatRequest,
    usuario: dict = Depends(verificar_papel_professor)
):
    from ..services import chat_copiloto_professor
    escola_id = usuario.get("escola_id", 1)
    resposta = await chat_copiloto_professor(escola_id, req.mensagem, req.historico)
    return {"resposta": resposta}
