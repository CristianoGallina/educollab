import os

with open('backend/app/services.py', 'r', encoding='utf-8') as f:
    content = f.read()

search_prompt = '''    system_prompt = (
        "Você é um especialista em elaboração de avaliações diagnósticas e formativas alinhadas à BNCC. "
        "Gere um quiz didático em JSON com os campos: "
        "- tema (string)\\n"
        "- objetivo (string)\\n"
        "- habilidades_bncc (lista com 1 ou 2 códigos oficiais da BNCC e descrição)\\n"
        "- perguntas (lista de objetos, cada qual contendo: pergunta, opcoes [lista com 4 strings], resposta_correta [string idêntica a uma das opções], explicacao [justificativa didática]).\\n"
        "Retorne APENAS JSON válido sem marcações extras."
    )'''

replace_prompt = '''    system_prompt = (
        "Você é um especialista em elaboração de avaliações diagnósticas e formativas alinhadas à BNCC. "
        "Gere um quiz didático em JSON com os campos: "
        "- tema (string)\\n"
        "- objetivo (string)\\n"
        "- habilidades_bncc (lista com 1 ou 2 códigos oficiais da BNCC e descrição)\\n"
        f"- perguntas (lista com EXATAMENTE {quantidade} objetos, cada qual contendo: pergunta, opcoes [lista com 4 strings], resposta_correta [string idêntica a uma das opções], explicacao [justificativa didática]).\\n"
        f"MUITO IMPORTANTE: O nível de dificuldade das perguntas DEVE SER: {nivel}. Adapte o vocabulário e a complexidade para esse nível.\\n"
        "Retorne APENAS JSON válido sem marcações extras."
    )'''

if search_prompt in content:
    content = content.replace(search_prompt, replace_prompt)
    with open('backend/app/services.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("done backend")
else:
    print("search string not found in services.py")
