with open('backend/app/store.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_func = '''
def add_teacher_to_class(turma_id: int, email: str) -> dict:
    email = str(email or "").strip().lower()
    with SessionLocal() as session:
        turma = session.query(ClassRoom).filter(ClassRoom.id == int(turma_id)).first()
        if not turma:
            raise ValueError("Turma não encontrada.")
        
        prof = session.query(Teacher).filter(Teacher.email == email).first()
        if not prof:
            raise ValueError("Professor não encontrado com esse e-mail.")
            
        if prof.escola_id != turma.escola_id:
            raise ValueError("O professor não pertence à mesma escola desta turma.")
            
        already_in = any(p.id == prof.id for p in turma.teachers)
        if not already_in:
            turma.teachers.append(prof)
            session.commit()
            
        session.refresh(turma)
        item = _serialize_class(turma)
    _sync_store()
    return item
'''

if 'def add_teacher_to_class' not in content:
    content = content + '\n' + new_func

with open('backend/app/store.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Funcao add_teacher_to_class adicionada.")
