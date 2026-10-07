import os

code = """
def list_school_details(escola_id: int) -> dict:
    with SessionLocal() as session:
        school = _get_school_or_raise(escola_id)
        
        professores = session.query(Teacher).filter(Teacher.escola_id == escola_id).all()
        
        turmas = session.query(ClassRoom).filter(ClassRoom.escola_id == escola_id).all()
        turma_ids = [t.id for t in turmas]
        
        alunos = []
        if turma_ids:
            alunos = session.query(Student).filter(Student.turma_id.in_(turma_ids)).all()
            
        return {
            "professores": [_serialize_teacher(p) for p in professores],
            "alunos": [_serialize_student(a) for a in alunos]
        }

def delete_school(escola_id: int) -> dict:
    with SessionLocal() as session:
        school = session.query(School).filter(School.id == escola_id).first()
        if not school:
            raise ValueError("Escola não encontrada.")
            
        # Manually cascade delete to avoid FK errors
        # 1. Turmas and their contents
        turmas = session.query(ClassRoom).filter(ClassRoom.escola_id == escola_id).all()
        for t in turmas:
            # Submissions
            session.query(QuizSubmission).filter(QuizSubmission.turma_id == t.id).delete()
            # Quizzes
            session.query(Quiz).filter(Quiz.turma_id == t.id).delete()
            # Plans
            session.query(Plan).filter(Plan.turma_id == t.id).delete()
            # Subjects
            session.query(Subject).filter(Subject.turma_id == t.id).delete()
            # Students and their users
            students = session.query(Student).filter(Student.turma_id == t.id).all()
            for st in students:
                session.query(User).filter(User.email == st.email).delete()
                session.delete(st)
                
            # Class teachers mapping
            session.execute(class_teachers.delete().where(class_teachers.c.turma_id == t.id))
            
            session.delete(t)
            
        # 2. Teachers and their users
        teachers = session.query(Teacher).filter(Teacher.escola_id == escola_id).all()
        for prof in teachers:
            session.query(User).filter(User.email == prof.email).delete()
            session.delete(prof)
            
        # 3. API Usage
        session.query(ApiUsage).filter(ApiUsage.escola_id == escola_id).delete()
        
        # 4. School
        session.delete(school)
        session.commit()
        return {"mensagem": "Escola e todos os registros associados foram excluídos."}

def delete_teacher(professor_id: int) -> dict:
    with SessionLocal() as session:
        prof = session.query(Teacher).filter(Teacher.id == professor_id).first()
        if not prof:
            raise ValueError("Professor não encontrado.")
            
        session.execute(class_teachers.delete().where(class_teachers.c.professor_id == professor_id))
        session.query(User).filter(User.email == prof.email).delete()
        session.delete(prof)
        session.commit()
        return {"mensagem": "Professor excluído."}

def delete_student(aluno_id: int) -> dict:
    with SessionLocal() as session:
        aluno = session.query(Student).filter(Student.id == aluno_id).first()
        if not aluno:
            raise ValueError("Aluno não encontrado.")
            
        session.query(User).filter(User.email == aluno.email).delete()
        session.delete(aluno)
        session.commit()
        return {"mensagem": "Aluno excluído."}
"""

with open('backend/app/store.py', 'a', encoding='utf-8') as f:
    f.write(code)
print("Store updated")
