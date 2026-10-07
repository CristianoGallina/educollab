import os

code = """
@router.get("/escolas/{escola_id}/detalhes", dependencies=[Depends(verificar_papel_admin)])
async def detalhes_escola_completo(escola_id: int):
    from ..store import list_school_details
    try:
        dados = list_school_details(escola_id)
        return dados
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

@router.delete("/escolas/{escola_id}", dependencies=[Depends(verificar_papel_admin)])
async def excluir_escola(escola_id: int):
    from ..store import delete_school
    try:
        res = delete_school(escola_id)
        return res
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

@router.delete("/professores/{professor_id}", dependencies=[Depends(verificar_papel_admin)])
async def excluir_professor(professor_id: int):
    from ..store import delete_teacher
    try:
        res = delete_teacher(professor_id)
        return res
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

@router.delete("/alunos/{aluno_id}", dependencies=[Depends(verificar_papel_admin)])
async def excluir_aluno(aluno_id: int):
    from ..store import delete_student
    try:
        res = delete_student(aluno_id)
        return res
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
"""

with open('backend/app/routers/admin_router.py', 'a', encoding='utf-8') as f:
    f.write(code)
print("Admin router updated")
