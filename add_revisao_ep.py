with open('backend/app/routers/aluno_router.py', 'r', encoding='utf-8') as f:
    content = f.read()

import_pattern = "from ..services import processar_feedback_llm, gerar_dica_socratica, chat_tutor_livre_ia"
if 'gerar_quiz_ia' not in content:
    content = content.replace(import_pattern, import_pattern + ", gerar_quiz_ia")

new_endpoint = '''
class RevisaoRequest(BaseModel):
    tema: str
    escola_id: int | None = None

@router.post("/gerar-revisao", dependencies=[Depends(verificar_papel_aluno)])
async def gerar_revisao_aluno(payload: RevisaoRequest):
    quiz = await gerar_quiz_ia(
        tema=payload.tema,
        objetivo="Revisão focada em pontos de atenção detectados no histórico do aluno.",
        quantidade=3,
        nivel="Básico",
        disciplina="Geral",
        escola_id=payload.escola_id
    )
    return {"status": "sucesso", "quiz": quiz}
'''

if 'gerar_revisao_aluno' not in content:
    content += '\n' + new_endpoint

with open('backend/app/routers/aluno_router.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Endpoint revisao added")
