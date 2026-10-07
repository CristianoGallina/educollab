with open('backend/app/routers/aluno_router.py', 'r', encoding='utf-8') as f:
    content = f.read()

import_pattern = "from ..services import processar_feedback_llm, gerar_dica_socratica"
if 'chat_tutor_livre_ia' not in content:
    content = content.replace(import_pattern, import_pattern + ", chat_tutor_livre_ia")

new_endpoint = '''
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
'''

if 'chat_tutor_livre(' not in content:
    content += '\n' + new_endpoint

with open('backend/app/routers/aluno_router.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Endpoint added")
