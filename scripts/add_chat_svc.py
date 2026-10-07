with open('backend/app/services.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_service = '''
async def chat_tutor_livre_ia(mensagem: str, historico: list, escola_id: int | None = None) -> str:
    system_prompt = """Você é um Tutor Socrático amigável e encorajador para alunos do ensino fundamental e médio.
Sua regra de ouro: NUNCA dê a resposta pronta ou faça o trabalho pelo aluno.
Seu objetivo é fazer o aluno pensar. Use perguntas orientadoras, analogias simples e encorajamento.
Responda sempre de forma curta e direta (máx 2-3 parágrafos curtos)."""

    # Formatar o histórico para o prompt
    historico_texto = "\\n".join([f"{msg['role']}: {msg['content']}" for msg in historico])
    
    human_prompt = f"""Histórico recente da conversa:
{historico_texto}

Nova mensagem do aluno: {mensagem}

Responda no papel de Tutor Socrático. Formato obrigatório: JSON {"\\"resposta\\": \\"...\\"}"""

    resultado_str = await _chamada_llm_json(system_prompt, human_prompt, temperatura=0.6, escola_id=escola_id)
    try:
        import json
        dados = json.loads(resultado_str)
        return dados.get("resposta", "Me conte mais sobre o que você está estudando hoje.")
    except Exception:
        return "Tive um problema ao formular a resposta. Pode tentar perguntar de outra forma?"
'''

if 'chat_tutor_livre_ia' not in content:
    content += '\n' + new_service

with open('backend/app/services.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Service added")
