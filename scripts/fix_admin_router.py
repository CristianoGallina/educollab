import os

with open('backend/app/routers/admin_router.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'from ..dependencies import verificar_papel_admin',
    'from ..dependencies import verificar_papel_admin, usuario_logado'
)

old_str = """@router.post("/chat-copiloto")
async def chat_copiloto_admin_endpoint(
    req: AdminCopilotoChatRequest,
    usuario: dict = Depends(verificar_papel_admin)
):
    from ..services import chat_copiloto_admin
    escola_id = usuario.get("escola_id", 1)"""

new_str = """@router.post("/chat-copiloto")
async def chat_copiloto_admin_endpoint(
    req: AdminCopilotoChatRequest,
    papel: str = Depends(verificar_papel_admin),
    user_info = Depends(usuario_logado)
):
    from ..services import chat_copiloto_admin
    escola_id = getattr(user_info, 'escola_id', 1)"""

content = content.replace(old_str, new_str)

with open('backend/app/routers/admin_router.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
