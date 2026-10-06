with open('backend/app/routers/prof_router.py', 'r', encoding='utf-8') as f:
    content = f.read()

endpoint = '''
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
'''

if 'chat_copiloto_endpoint' not in content:
    with open('backend/app/routers/prof_router.py', 'a', encoding='utf-8') as f:
        f.write(endpoint)
print("done")
