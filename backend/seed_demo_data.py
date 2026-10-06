from app.database import SessionLocal, School, Teacher, ClassRoom, Student


SEEDS = [
    {
        "school": {"nome": "Escola Estadual Nova Esperança", "cidade": "São Paulo", "estado": "SP", "diretor": "Prof. Helena Costa"},
        "teacher": {"nome": "Prof. Ana Souza", "email": "ana.souza@novaesperanca.edu.br", "disciplina": "Matemática"},
        "classroom": {"nome": "7º Ano A", "ano": "7º Ano", "codigo": "MAT7A-NE", "cor": "bg-blue-500"},
        "students": [
            {"nome": "Carlos Eduardo", "email": "carlos.eduardo@novaesperanca.edu.br"},
            {"nome": "Ana Beatriz", "email": "ana.beatriz@novaesperanca.edu.br"},
            {"nome": "Mateus Oliveira", "email": "mateus.oliveira@novaesperanca.edu.br"},
        ],
    },
    {
        "school": {"nome": "Colégio Integração", "cidade": "Campinas", "estado": "SP", "diretor": "Prof. Roberto Lima"},
        "teacher": {"nome": "Prof. Pedro Santos", "email": "pedro.santos@integracao.edu.br", "disciplina": "Ciências"},
        "classroom": {"nome": "8º Ano B", "ano": "8º Ano", "codigo": "CIE8B-INT", "cor": "bg-emerald-500"},
        "students": [
            {"nome": "Larissa Mendes", "email": "larissa.mendes@integracao.edu.br"},
            {"nome": "João Vitor", "email": "joao.vitor@integracao.edu.br"},
            {"nome": "Isabela Costa", "email": "isabela.costa@integracao.edu.br"},
        ],
    },
    {
        "school": {"nome": "Escola Cidadania Digital", "cidade": "Rio de Janeiro", "estado": "RJ", "diretor": "Prof. Daniela Reis"},
        "teacher": {"nome": "Prof. Camila Rocha", "email": "camila.rocha@cidadaniadigital.edu.br", "disciplina": "Português"},
        "classroom": {"nome": "9º Ano C", "ano": "9º Ano", "codigo": "POR9C-CD", "cor": "bg-fuchsia-500"},
        "students": [
            {"nome": "Luciana Souza", "email": "luciana.souza@cidadaniadigital.edu.br"},
            {"nome": "Rafael Nogueira", "email": "rafael.nogueira@cidadaniadigital.edu.br"},
            {"nome": "Marina Prado", "email": "marina.prado@cidadaniadigital.edu.br"},
        ],
    },
]


def ensure_school(session, payload):
    school = session.query(School).filter_by(nome=payload['nome']).first()
    if school:
        return school
    school = School(**payload)
    session.add(school)
    session.commit()
    session.refresh(school)
    return school


def ensure_teacher(session, school_id, payload, disciplina):
    teacher = session.query(Teacher).filter_by(email=payload['email']).first()
    if teacher:
        return teacher
    teacher = Teacher(
        nome=payload['nome'],
        email=payload['email'],
        disciplina=disciplina,
        escola_id=school_id,
    )
    session.add(teacher)
    session.commit()
    session.refresh(teacher)
    return teacher


def ensure_classroom(session, school_id, teacher_id, payload):
    classroom = session.query(ClassRoom).filter_by(codigo=payload['codigo']).first()
    if classroom:
        return classroom
    classroom = ClassRoom(
        nome=payload['nome'],
        ano=payload['ano'],
        codigo=payload['codigo'],
        cor=payload['cor'],
        escola_id=school_id,
        professor_id=teacher_id,
    )
    session.add(classroom)
    session.commit()
    session.refresh(classroom)
    return classroom


def ensure_student(session, turma_id, payload):
    student = session.query(Student).filter_by(email=payload['email']).first()
    if student:
        return student
    student = Student(
        nome=payload['nome'],
        email=payload['email'],
        turma_id=turma_id,
    )
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


def seed_demo_data():
    session = SessionLocal()
    created = []

    try:
        for item in SEEDS:
            school = ensure_school(session, item['school'])
            teacher = ensure_teacher(session, school.id, item['teacher'], item['teacher']['disciplina'])
            classroom = ensure_classroom(session, school.id, teacher.id, item['classroom'])
            for student in item['students']:
                aluno = ensure_student(session, classroom.id, student)
                created.append({
                    "tipo": "aluno",
                    "nome": aluno.nome,
                    "email": aluno.email,
                    "turma": classroom.nome,
                })
            created.append({
                "tipo": "turma",
                "nome": classroom.nome,
                "codigo": classroom.codigo,
                "professor": teacher.nome,
                "escola": school.nome,
            })
        session.commit()
    finally:
        session.close()

    return created


if __name__ == '__main__':
    registros = seed_demo_data()
    print('REGISTROS_INCLUIDOS', len(registros))
    for item in registros:
        print(item)
