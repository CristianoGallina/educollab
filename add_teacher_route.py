import re

with open('backend/app/routers/prof_router.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'add_teacher_to_class' not in content:
    content = content.replace('list_classes,', 'list_classes,\n    add_teacher_to_class,')

endpoint = '''
@router.post("/turma/{turma_id}/professores", dependencies=[Depends(verificar_papel_professor)])
async def adicionar_professor_turma(turma_id: int, payload: dict = Body(...)):
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail do professor é obrigatório.")
    try:
        turma = add_teacher_to_class(turma_id, email)
        return {"status": "sucesso", "mensagem": "Professor adicionado à turma.", "turma": turma}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
'''

if 'adicionar_professor_turma' not in content:
    content = content + '\n' + endpoint

with open('backend/app/routers/prof_router.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Endpoint adicionado.")
