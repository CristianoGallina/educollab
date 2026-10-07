import os

with open('backend/app/routers/admin_router.py', 'r', encoding='utf-8') as f:
    c = f.read()

old_func = """    system_prompt = \"\"\"Você é o Analista Executivo EduCollab.
Você ajuda diretores e gestores escolares a entender métricas de uso de IA, custos, risco de churn de escolas e desempenho acadêmico macro.
Responda sempre com uma postura executiva, clara e em Markdown.\"\"\"
    historico_texto = "\\n".join([f"{msg['role']}: {msg['content']}" for msg in req.historico])
    human_prompt = f\"\"\"Histórico:"""

new_func = """    from ..store import list_schools, get_summary
    dados_escolas = list_schools()
    resumo = get_summary()
    
    escolas_str = "\\n".join([f"- {e['nome']} (ID {e['id']}): {e.get('tokens_usados', 0)} tokens usados, Custo R$ {e.get('custo_total', 0)}" for e in dados_escolas])
    
    system_prompt = f\"\"\"Você é o Analista Executivo EduCollab.
Você ajuda diretores e gestores escolares a entender métricas de uso de IA, custos, risco de churn de escolas e desempenho acadêmico macro.
Use os seguintes DADOS REAIS do banco de dados para basear suas análises:
- Total Escolas na Rede: {resumo['total_escolas']}
- Tokens Totais Usados na Rede: {resumo['total_tokens']}
- Custo Total da Rede: R$ {resumo['total_custo']}
Detalhes do Uso por Escola:
{escolas_str}

Responda sempre com uma postura executiva, baseando-se RIGOROSAMENTE nos dados acima quando perguntado sobre escolas ou custos. Não invente dados.\"\"\"
    historico_texto = "\\n".join([f"{msg['role']}: {msg['content']}" for msg in req.historico])
    human_prompt = f\"\"\"Histórico:"""

c = c.replace(old_func, new_func)

with open('backend/app/routers/admin_router.py', 'w', encoding='utf-8') as f:
    f.write(c)
print('Patched chat context')
