from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from ..schemas import SubmissaoComDetalhes, DicaSocraticaRequest, EntrarTurmaCodigoRequest, TipoUsuario
from ..dependencies import verificar_papel_aluno, usuario_logado, garantir_dados_do_proprio_aluno
from ..services import processar_feedback_llm, gerar_dica_socratica, chat_tutor_livre_ia, gerar_quiz_ia
from ..store import (
    get_conteudo_por_aluno,
    get_conteudo_por_turma,
    create_quiz_submission,
    list_student_submissions,
    enroll_student_by_code,
    list_student_classes,
)
import logging

router = APIRouter(prefix="/api/v1/aluno", tags=["Fluxo do Aluno"])


@router.get("/conteudo-turma", dependencies=[Depends(verificar_papel_aluno)])
async def listar_conteudo_turma(
    turma_id: int | None = Query(default=None),
    email_aluno: str | None = Query(default=None),
    user=Depends(usuario_logado),
):
    garantir_dados_do_proprio_aluno(user, email_aluno)
    try:
        if email_aluno:
            return get_conteudo_por_aluno(email_aluno)
        if turma_id is None:
            raise ValueError("Informe turma_id ou email_aluno para buscar o conteúdo da turma.")
        if user.tipo == TipoUsuario.aluno.value:
            turmas_do_aluno = {turma["id"] for turma in list_student_classes(user.email)}
            if int(turma_id) not in turmas_do_aluno:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não está matriculado nesta turma.")
        return get_conteudo_por_turma(int(turma_id), somente_publicados=True)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/feedback-quiz", dependencies=[Depends(verificar_papel_aluno)])
async def gerar_feedback_pos_quiz(submissao: SubmissaoComDetalhes, user=Depends(usuario_logado)):
    garantir_dados_do_proprio_aluno(user, str(submissao.email_aluno))
    logging.info(f"ALUNO | {submissao.email_aluno} | Iniciando Correção IA e Persistência...")

    feedback_ia = await processar_feedback_llm(
        nota=submissao.nota_final,
        respostas_aluno=submissao.respostas_aluno,
        gabarito=submissao.gabarito_oficial
    )

    submissao_salva = create_quiz_submission({
        "email_aluno": str(submissao.email_aluno),
        "turma_id": submissao.turma_id,
        "quiz_id": submissao.quiz_id,
        "nota_final": submissao.nota_final,
        "respostas_aluno": submissao.respostas_aluno,
        "gabarito_oficial": submissao.gabarito_oficial,
        "feedback_ia": feedback_ia,
    })

    return {
        "status": "sucesso",
        "nota_processada": submissao.nota_final,
        "feedback_ia": feedback_ia,
        "submissao": submissao_salva,
    }


@router.post("/pedir-dica", dependencies=[Depends(verificar_papel_aluno)])
async def pedir_dica_socratica(payload: DicaSocraticaRequest):
    logging.info("ALUNO | Solicitando dica socrática à IA")
    resultado = await gerar_dica_socratica(
        pergunta=payload.pergunta,
        resposta_aluno=payload.resposta_aluno,
        tema=payload.tema,
        escola_id=payload.escola_id,
    )
    return {
        "status": "sucesso",
        "dica": resultado.get("dica"),
        "pergunta_orientadora": resultado.get("pergunta_orientadora"),
    }


@router.get("/historico-submissoes", dependencies=[Depends(verificar_papel_aluno)])
async def historico_submissoes_aluno(email_aluno: str = Query(...), user=Depends(usuario_logado)):
    garantir_dados_do_proprio_aluno(user, email_aluno)
    submissoes = list_student_submissions(email_aluno)
    return {
        "email_aluno": email_aluno,
        "total": len(submissoes),
        "submissoes": submissoes,
    }


@router.post("/entrar-turma", dependencies=[Depends(verificar_papel_aluno)])
async def entrar_turma_por_codigo(payload: EntrarTurmaCodigoRequest, user=Depends(usuario_logado)):
    garantir_dados_do_proprio_aluno(user, str(payload.email_aluno))
    logging.info(f"ALUNO | {payload.email_aluno} tentando entrar na turma com código {payload.codigo}")
    try:
        turma = enroll_student_by_code(
            codigo=payload.codigo,
            email_aluno=str(payload.email_aluno),
            nome_aluno=payload.nome_aluno,
        )
        return {
            "status": "sucesso",
            "mensagem": f"Parabéns! Você entrou na turma '{turma['nome']}' com sucesso.",
            "turma": turma,
        }
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/turmas", dependencies=[Depends(verificar_papel_aluno)])
async def listar_turmas_do_aluno(email_aluno: str = Query(...), user=Depends(usuario_logado)):
    garantir_dados_do_proprio_aluno(user, email_aluno)
    turmas = list_student_classes(email_aluno)
    return {
        "email_aluno": email_aluno,
        "total": len(turmas),
        "turmas": turmas,
    }

from pydantic import BaseModel
class ChatMensagem(BaseModel):
    role: str
    content: str

class ChatTutorRequest(BaseModel):
    mensagem: str
    historico: list[ChatMensagem] = []
    escola_id: int | None = None

@router.post("/chat-tutor", dependencies=[Depends(verificar_papel_aluno)])
async def chat_tutor_livre(payload: ChatTutorRequest):
    historico_dicts = [{"role": msg.role, "content": msg.content} for msg in payload.historico]
    resposta = await chat_tutor_livre_ia(payload.mensagem, historico_dicts, payload.escola_id)
    return {"status": "sucesso", "resposta": resposta}


class RevisaoRequest(BaseModel):
    tema: str
    escola_id: int | None = None

@router.post("/gerar-revisao", dependencies=[Depends(verificar_papel_aluno)])
async def gerar_revisao_aluno(payload: RevisaoRequest):
    quiz = await gerar_quiz_ia(
        tema=payload.tema,
        objetivo="Revisão focada em pontos de atenção detectados no histórico do aluno.",
        quantidade=3,
        nivel="Básico",
        disciplina="Geral",
        escola_id=payload.escola_id
    )
    return {"status": "sucesso", "quiz": quiz}
