with open('backend/app/routers/admin_router.py', 'r', encoding='utf-8') as f:
    content = f.read()

endpoint = '''
from pydantic import BaseModel
class AdminChatRequest(BaseModel):
    mensagem: str
    historico: list = []

@router.post("/chat-copiloto")
async def chat_copiloto_admin(
    req: AdminChatRequest,
    usuario: dict = Depends(verificar_papel_admin)
):
    from ..services import _chamada_llm
    system_prompt = """Você é o Analista Executivo EduCollab.
Você ajuda diretores e gestores escolares a entender métricas de uso de IA, custos, risco de churn de escolas e desempenho acadêmico macro.
Responda sempre com uma postura executiva, clara e em Markdown."""
    historico_texto = "\\n".join([f"{msg['role']}: {msg['content']}" for msg in req.historico])
    human_prompt = f"""Histórico:
{historico_texto}

Dúvida do Gestor: {req.mensagem}"""
    resposta = await _chamada_llm(system_prompt, human_prompt, temperatura=0.6, escola_id=1)
    return {"resposta": resposta}
'''

if 'chat_copiloto_admin' not in content:
    with open('backend/app/routers/admin_router.py', 'a', encoding='utf-8') as f:
        f.write(endpoint)
print("done")
