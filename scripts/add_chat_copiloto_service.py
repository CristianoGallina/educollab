with open('backend/app/services.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_service = '''
async def chat_copiloto_professor(escola_id: int, mensagem: str, historico: list) -> str:
    system_prompt = """Você é o Copiloto Pedagógico EduCollab, um assistente especializado em educação e pedagogia.
Seu objetivo é ajudar professores a criar planos de aula, gerar questões, analisar dados preditivos da turma, sugerir agrupamentos produtivos e responder a qualquer dúvida educacional.
Responda de forma clara, prática e no formato de texto limpo (Markdown). Seja sempre encorajador e consultivo."""
    
    historico_texto = "\\n".join([f"{msg['role']}: {msg['content']}" for msg in historico])
    human_prompt = f"""Histórico da conversa:
{historico_texto}

Nova mensagem do professor: {mensagem}"""

    resultado_str = await _chamada_llm(system_prompt, human_prompt, temperatura=0.7, escola_id=escola_id)
    return resultado_str
'''
if 'chat_copiloto_professor' not in content:
    with open('backend/app/services.py', 'a', encoding='utf-8') as f:
        f.write(new_service)
print("done")
