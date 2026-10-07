with open('backend/app/database.py', 'r', encoding='utf-8') as f:
    content = f.read()

assoc_table = '''
from sqlalchemy import Table
class_teachers = Table(
    'class_teachers',
    Base.metadata,
    mapped_column('turma_id', Integer, ForeignKey('classes.id'), primary_key=True),
    mapped_column('professor_id', Integer, ForeignKey('teachers.id'), primary_key=True)
)
'''
if 'class_teachers = Table(' not in content:
    content = content.replace('class Subject(Base):', assoc_table + '\nclass Subject(Base):')

content = content.replace('teacher: Mapped[Teacher | None] = relationship(back_populates="classes")', 'teachers: Mapped[list["Teacher"]] = relationship(secondary="class_teachers", back_populates="classes")')
content = content.replace('classes: Mapped[list["ClassRoom"]] = relationship(back_populates="teacher")', 'classes: Mapped[list["ClassRoom"]] = relationship(secondary="class_teachers", back_populates="teachers")')

migration = '''
    if "class_teachers" not in table_names:
        class_teachers.create(bind=engine)
        try:
            with engine.begin() as conn:
                conn.execute(text("INSERT INTO class_teachers (turma_id, professor_id) SELECT id, professor_id FROM classes WHERE professor_id IS NOT NULL ON CONFLICT DO NOTHING"))
        except Exception:
            pass
'''
if 'if "class_teachers" not in table_names:' not in content:
    content = content.replace('if "api_usage" not in table_names:', migration + '\n    if "api_usage" not in table_names:')

with open('backend/app/database.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Migration script applied to database.py")
