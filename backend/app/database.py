import os
from datetime import datetime
from typing import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker
from sqlalchemy import Integer, String, ForeignKey, JSON, Float, DateTime, UniqueConstraint

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:adminpassword@localhost:5432/educollab")
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, future=True, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class School(Base):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String, nullable=False)
    cidade: Mapped[str] = mapped_column(String, nullable=False)
    estado: Mapped[str] = mapped_column(String, nullable=False)
    diretor: Mapped[str | None] = mapped_column(String, nullable=True)
    api_key_ia: Mapped[str | None] = mapped_column(String, nullable=True)
    provedor_ia: Mapped[str] = mapped_column(String, nullable=False, default="grok")
    modelo_ia: Mapped[str | None] = mapped_column(String, nullable=True)
    tokens_usados: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    custo_total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    uso_ia_ultima_data: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    teachers: Mapped[list["Teacher"]] = relationship(back_populates="school")
    classes: Mapped[list["ClassRoom"]] = relationship(back_populates="school")
    consumos_api: Mapped[list["ApiUsage"]] = relationship(back_populates="school")


class ApiUsage(Base):
    __tablename__ = "api_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str | None] = mapped_column(String, nullable=True)
    tokens_usados: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    custo: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    descricao: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    school: Mapped[School] = relationship(back_populates="consumos_api")


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    disciplina: Mapped[str] = mapped_column(String, nullable=False)
    escola_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False)

    school: Mapped[School] = relationship(back_populates="teachers")
    classes: Mapped[list["ClassRoom"]] = relationship(secondary="class_teachers", back_populates="teachers")


class ClassRoom(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String, nullable=False)
    ano: Mapped[str] = mapped_column(String, nullable=False)
    codigo: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    cor: Mapped[str | None] = mapped_column(String, nullable=True)
    escola_id: Mapped[int | None] = mapped_column(ForeignKey("schools.id"), nullable=True)
    professor_id: Mapped[int | None] = mapped_column(ForeignKey("teachers.id"), nullable=True)

    school: Mapped[School | None] = relationship(back_populates="classes")
    teachers: Mapped[list["Teacher"]] = relationship(secondary="class_teachers", back_populates="classes")
    students: Mapped[list["Student"]] = relationship(back_populates="class_room")
    subjects: Mapped[list["Subject"]] = relationship(back_populates="class_room")
    plans: Mapped[list["Plan"]] = relationship(back_populates="class_room")
    quizzes: Mapped[list["Quiz"]] = relationship(back_populates="class_room")



from sqlalchemy import Table, Column, Integer, ForeignKey
class_teachers = Table(
    'class_teachers',
    Base.metadata,
    Column('turma_id', Integer, ForeignKey('classes.id'), primary_key=True),
    Column('professor_id', Integer, ForeignKey('teachers.id'), primary_key=True)
)

class Subject(Base):
    __tablename__ = "class_subjects"
    __table_args__ = (UniqueConstraint("turma_id", "nome", name="uq_turma_disciplina"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String, nullable=False)
    turma_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), nullable=False)

    class_room: Mapped[ClassRoom] = relationship(back_populates="subjects")


class Student(Base):
    """Matrícula do aluno em uma turma: um mesmo e-mail pode ter várias linhas (uma por turma)."""

    __tablename__ = "students"
    __table_args__ = (UniqueConstraint("email", "turma_id", name="uq_aluno_email_turma"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    turma_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), nullable=False)

    class_room: Mapped[ClassRoom] = relationship(back_populates="students")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String, nullable=False)
    tipo: Mapped[str] = mapped_column(String, nullable=False)


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    tema: Mapped[str] = mapped_column(String, nullable=False)
    turma_id: Mapped[int | None] = mapped_column(ForeignKey("classes.id"), nullable=True)
    conteudo: Mapped[dict] = mapped_column(JSON, nullable=False)

    class_room: Mapped[ClassRoom | None] = relationship(back_populates="plans")


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    tema: Mapped[str] = mapped_column(String, nullable=False)
    objetivo: Mapped[str] = mapped_column(String, nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    turma_id: Mapped[int | None] = mapped_column(ForeignKey("classes.id"), nullable=True)
    conteudo: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="publicado")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    class_room: Mapped[ClassRoom | None] = relationship(back_populates="quizzes")
    submissions: Mapped[list["QuizSubmission"]] = relationship(back_populates="quiz", cascade="all, delete-orphan")


class QuizSubmission(Base):
    __tablename__ = "quiz_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    quiz_id: Mapped[int | None] = mapped_column(ForeignKey("quizzes.id"), nullable=True)
    turma_id: Mapped[int | None] = mapped_column(ForeignKey("classes.id"), nullable=True)
    aluno_id: Mapped[int | None] = mapped_column(ForeignKey("students.id"), nullable=True)
    email_aluno: Mapped[str] = mapped_column(String, nullable=False)
    nota_final: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    respostas_aluno: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    gabarito_oficial: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    feedback_ia: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    quiz: Mapped[Quiz | None] = relationship(back_populates="submissions")
    class_room: Mapped[ClassRoom | None] = relationship()
    student: Mapped[Student | None] = relationship()


def _seed_demo_data_if_needed() -> None:
    with SessionLocal() as session:
        if session.query(School).count() == 0:
            from .reset_and_seed import reset_and_populate_db
            reset_and_populate_db()



def init_db() -> None:
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    if "schools" in table_names:
        school_columns = {column["name"] for column in inspector.get_columns("schools")}
        for column_name, column_type in {
            "api_key_ia": "VARCHAR",
            "provedor_ia": "VARCHAR",
            "modelo_ia": "VARCHAR",
            "tokens_usados": "INTEGER",
            "custo_total": "FLOAT",
            "uso_ia_ultima_data": "TIMESTAMP",
        }.items():
            if column_name not in school_columns:
                try:
                    with engine.begin() as conn:
                        conn.execute(text(f"ALTER TABLE schools ADD COLUMN {column_name} {column_type}"))
                except Exception:
                    pass

    if "students" in table_names:
        # Migração: o e-mail deixa de ser único globalmente (aluno pode estar em várias turmas).
        for statement in (
            "ALTER TABLE students DROP CONSTRAINT IF EXISTS students_email_key",
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_aluno_email_turma ON students (email, turma_id)",
        ):
            try:
                with engine.begin() as conn:
                    conn.execute(text(statement))
            except Exception:
                pass

    if "quizzes" in table_names:
        quiz_columns = {column["name"] for column in inspector.get_columns("quizzes")}
        if "status" not in quiz_columns:
            try:
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE quizzes ADD COLUMN status VARCHAR DEFAULT 'publicado'"))
            except Exception:
                pass
        if "created_at" not in quiz_columns:
            try:
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE quizzes ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
            except Exception:
                pass

    
    if "class_teachers" not in table_names:
        class_teachers.create(bind=engine)
        try:
            with engine.begin() as conn:
                conn.execute(text("INSERT INTO class_teachers (turma_id, professor_id) SELECT id, professor_id FROM classes WHERE professor_id IS NOT NULL ON CONFLICT DO NOTHING"))
        except Exception:
            pass

    if "api_usage" not in table_names:
        ApiUsage.__table__.create(bind=engine)

    if "class_subjects" not in table_names:
        Subject.__table__.create(bind=engine)

    if "quiz_submissions" not in table_names:
        QuizSubmission.__table__.create(bind=engine)

    try:
        _seed_demo_data_if_needed()
    except Exception as exc:
        import logging
        logging.warning(f"Erro ao popular dados de demo: {exc}")


def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


try:
    init_db()
except Exception as exc:
    import logging
    logging.warning(f"init_db() falhou na importação inicial (banco pode não estar pronto ainda): {exc}")

