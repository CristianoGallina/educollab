from fastapi import APIRouter, Depends, Body, HTTPException, status

from ..dependencies import verificar_papel_admin, usuario_logado
from ..schemas import SchoolCreate, ProfessorCreate, SchoolConfigIA
from ..store import create_school, create_teacher, get_summary, configurar_ia_escola, remover_configuracao_ia_escola, get_school_uso_ia

router = APIRouter(prefix="/api/v1/admin", tags=["Administração"])


@router.get("/escolas", dependencies=[Depends(verificar_papel_admin)])
async def listar_escolas():
    from ..store import list_schools
    return {"escolas": list_schools()}


@router.post("/escolas", dependencies=[Depends(verificar_papel_admin)])
async def criar_escola(payload: SchoolCreate = Body(...)):
    try:
        escola = create_school(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"status": "sucesso", "mensagem": "Escola cadastrada com sucesso.", "escola": escola}


@router.post("/professores", dependencies=[Depends(verificar_papel_admin)])
async def criar_professor(payload: ProfessorCreate = Body(...)):
    try:
        professor = create_teacher(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"status": "sucesso", "mensagem": "Professor cadastrado com sucesso.", "professor": professor}


@router.get("/resumo", dependencies=[Depends(verificar_papel_admin)])
async def resumo_admin():
    return get_summary()


@router.post("/escolas/{escola_id}/configuracao-ia", dependencies=[Depends(verificar_papel_admin)])
async def configuracao_ia_escola(escola_id: int, payload: SchoolConfigIA = Body(...)):
    try:
        escola = configurar_ia_escola(escola_id, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"status": "sucesso", "mensagem": "Configuração da API da escola atualizada.", "escola": escola}


@router.delete("/escolas/{escola_id}/configuracao-ia", dependencies=[Depends(verificar_papel_admin)])
async def remover_configuracao_ia(escola_id: int):
    try:
        escola = remover_configuracao_ia_escola(escola_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"status": "sucesso", "mensagem": "Configuração da API da escola removida.", "escola": escola}


@router.get("/escolas/{escola_id}/uso-ia", dependencies=[Depends(verificar_papel_admin)])
async def uso_ia_escola(escola_id: int):
    try:
        dados = get_school_uso_ia(escola_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return dados

from pydantic import BaseModel
class AdminChatRequest(BaseModel):
    mensagem: str
    historico: list = []

@router.post("/chat-copiloto")
async def chat_copiloto_admin(
    req: AdminChatRequest,
    papel: str = Depends(verificar_papel_admin),
    user_info = Depends(usuario_logado)
):
    from ..services import _chamada_llm_json
    system_prompt = """Você é o Analista Executivo EduCollab.
Você ajuda diretores e gestores escolares a entender métricas de uso de IA, custos, risco de churn de escolas e desempenho acadêmico macro.
Responda sempre com uma postura executiva, clara e em Markdown."""
    historico_texto = "\n".join([f"{msg['role']}: {msg['content']}" for msg in req.historico])
    human_prompt = f"""Histórico:
{historico_texto}

Dúvida do Gestor: {req.mensagem}

Formato OBRIGATÓRIO de saída: JSON {{ "resposta": "sua resposta em markdown aqui" }}"""
    
    escola_id = getattr(user_info, 'escola_id', 1)
    resposta = await _chamada_llm_json(system_prompt, human_prompt, temperatura=0.6, escola_id=escola_id)
    try:
        import json
        dados = json.loads(resposta)
        return {"resposta": dados.get("resposta", resposta)}
    except:
        return {"resposta": resposta}

@router.get("/escolas/{escola_id}/detalhes", dependencies=[Depends(verificar_papel_admin)])
async def detalhes_escola_completo(escola_id: int):
    from ..store import list_school_details
    try:
        dados = list_school_details(escola_id)
        return dados
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

@router.delete("/escolas/{escola_id}", dependencies=[Depends(verificar_papel_admin)])
async def excluir_escola(escola_id: int):
    from ..store import delete_school
    try:
        res = delete_school(escola_id)
        return res
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

@router.delete("/professores/{professor_id}", dependencies=[Depends(verificar_papel_admin)])
async def excluir_professor(professor_id: int):
    from ..store import delete_teacher
    try:
        res = delete_teacher(professor_id)
        return res
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

@router.delete("/alunos/{aluno_id}", dependencies=[Depends(verificar_papel_admin)])
async def excluir_aluno(aluno_id: int):
    from ..store import delete_student
    try:
        res = delete_student(aluno_id)
        return res
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
