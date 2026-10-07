import re

with open('backend/app/routers/admin_router.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'@router\.post\("/chat-copiloto"\).*', '', content, flags=re.DOTALL)

new_str = '''@router.post("/chat-copiloto")
async def chat_copiloto_admin(
    req: AdminChatRequest,
    papel: str = Depends(verificar_papel_admin),
    user_info = Depends(usuario_logado)
):
    from ..services import _chamada_llm_json
    system_prompt = """Você é o Analista Executivo EduCollab.
Você ajuda diretores e gestores escolares a entender métricas de uso de IA, custos, risco de churn de escolas e desempenho acadêmico macro.
Responda sempre com uma postura executiva, clara e em Markdown."""
    historico_texto = "\\n".join([f"{msg['role']}: {msg['content']}" for msg in req.historico])
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
'''

content += new_str

if 'usuario_logado' not in content:
    content = content.replace('verificar_papel_admin', 'verificar_papel_admin, usuario_logado')

with open('backend/app/routers/admin_router.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
