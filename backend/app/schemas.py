from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from enum import Enum


class TipoUsuario(str, Enum):
    aluno = "aluno"
    professor = "professor"
    administrador = "administrador"


class SchoolCreate(BaseModel):
    nome: str
    cidade: str
    estado: str
    diretor: Optional[str] = None
    api_key_ia: Optional[str] = None
    provedor_ia: str = "grok"
    modelo_ia: Optional[str] = None


class SchoolConfigIA(BaseModel):
    api_key_ia: Optional[str] = None
    provedor_ia: str = "grok"
    modelo_ia: Optional[str] = None


class ProfessorCreate(BaseModel):
    nome: str
    email: EmailStr
    disciplina: str
    escola_id: int


class AlunoCreate(BaseModel):
    nome: str
    email: EmailStr
    turma_id: int


class DisciplinaCreate(BaseModel):
    nome: str


class TurmaCreate(BaseModel):
    nome: str
    ano: str
    codigo: Optional[str] = None
    cor: Optional[str] = "bg-blue-500"
    escola_id: Optional[int] = None
    professor_id: Optional[int] = None
    disciplinas: Optional[List[str]] = None


class PlanoAulaCreate(BaseModel):
    tema_aula: str
    objetivos: Optional[List[str]] = None
    ano: Optional[str] = "Ensino Fundamental"
    nivel: Optional[str] = "Básico"
    duracao: Optional[str] = "40 min"
    turma_id: Optional[int] = None
    disciplina: Optional[str] = None
    habilidades_bncc: Optional[List[str]] = None


class QuizCreate(BaseModel):
    tema: str
    objetivo: str
    turma_id: Optional[int] = None
    quantidade: int = 5
    nivel: str = "Básico"
    disciplina: Optional[str] = None
    habilidades_bncc: Optional[List[str]] = None


class RegenerarQuestaoRequest(BaseModel):
    tema: str
    objetivo: Optional[str] = "Aplicar os conceitos centrais do tema."
    nivel: Optional[str] = "Básico"
    pergunta_anterior: Optional[str] = None
    turma_id: Optional[int] = None


class DicaSocraticaRequest(BaseModel):
    pergunta: str
    resposta_aluno: str
    tema: Optional[str] = None
    escola_id: Optional[int] = None


class SubmissaoComDetalhes(BaseModel):
    id_exercicio: str
    email_aluno: EmailStr
    nota_final: float
    respostas_aluno: list
    gabarito_oficial: list
    turma_id: Optional[int] = None
    quiz_id: Optional[int] = None


class FeedbackEstruturadoIA(BaseModel):
    pontos_fortes: list[str] = Field(description="Lista de 1 a 3 pontos fortes do aluno.")
    pontos_atencao: list[str] = Field(description="Lista de 1 a 3 pontos de atenção baseados no erro.")
    solucao_correta: Optional[list[str]] = Field(default=None, description="Explicação detalhada da solução correta.")
    recomendacao_estudo: str = Field(description="Uma recomendação prática com base na nota.")


class RecomendacaoIA(BaseModel):
    email_usuario: EmailStr
    id_conteudo: str
    score_relevancia: int
    motivo: str


class EntrarTurmaCodigoRequest(BaseModel):
    codigo: str
    email_aluno: EmailStr
    nome_aluno: Optional[str] = None