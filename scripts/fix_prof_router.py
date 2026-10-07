import os

with open('backend/app/routers/prof_router.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'from ..dependencies import verificar_papel_professor',
    'from ..dependencies import verificar_papel_professor, usuario_logado'
)

old_str = """@router.post("/chat-copiloto")
async def chat_copiloto_endpoint(
    req: CopilotoChatRequest,
    usuario: dict = Depends(verificar_papel_professor)
):
    from ..services import chat_copiloto_professor
    escola_id = usuario.get("escola_id", 1)"""

new_str = """@router.post("/chat-copiloto")
async def chat_copiloto_endpoint(
    req: CopilotoChatRequest,
    papel: str = Depends(verificar_papel_professor),
    user_info = Depends(usuario_logado)
):
    from ..services import chat_copiloto_professor
    escola_id = getattr(user_info, 'escola_id', 1)"""

content = content.replace(old_str, new_str)

with open('backend/app/routers/prof_router.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
