import os

with open('backend/app/services.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_prof = '''Nova mensagem do professor: {mensagem}"""

    resultado_str = await _chamada_llm(system_prompt, human_prompt, temperatura=0.7, escola_id=escola_id)
    return resultado_str'''

new_prof = '''Nova mensagem do professor: {mensagem}

Formato OBRIGATÓRIO de saída: JSON {"resposta": "sua resposta em markdown aqui"}"""

    resultado_str = await _chamada_llm_json(system_prompt, human_prompt, temperatura=0.7, escola_id=escola_id)
    try:
        import json
        dados = json.loads(resultado_str)
        return dados.get("resposta", resultado_str)
    except:
        return resultado_str'''

if old_prof in content:
    content = content.replace(old_prof, new_prof)
    print("Fixed Prof")

old_admin = '''Nova mensagem do gestor: {mensagem}"""

    resultado_str = await _chamada_llm(system_prompt, human_prompt, temperatura=0.6, escola_id=escola_id)
    return resultado_str'''

new_admin = '''Nova mensagem do gestor: {mensagem}

Formato OBRIGATÓRIO de saída: JSON {"resposta": "sua resposta em markdown aqui"}"""

    resultado_str = await _chamada_llm_json(system_prompt, human_prompt, temperatura=0.6, escola_id=escola_id)
    try:
        import json
        dados = json.loads(resultado_str)
        return dados.get("resposta", resultado_str)
    except:
        return resultado_str'''

if old_admin in content:
    content = content.replace(old_admin, new_admin)
    print("Fixed Admin")

with open('backend/app/services.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
