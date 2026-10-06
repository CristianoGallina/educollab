from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .auth import get_current_user
from .schemas import TipoUsuario

security = HTTPBearer(auto_error=False)


def usuario_logado(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Resolve o usuário a partir do JWT. Sem token válido, responde 401."""
    return get_current_user(credentials)


def _resolver_tipo_usuario(user=Depends(usuario_logado)) -> str:
    return user.tipo


def verificar_papel_admin(x_tipo_usuario: str = Depends(_resolver_tipo_usuario)):
    if x_tipo_usuario != TipoUsuario.administrador.value:
        raise HTTPException(status_code=403, detail="Acesso Restrito: Exclusivo para administradores.")
    return x_tipo_usuario


def verificar_papel_professor(x_tipo_usuario: str = Depends(_resolver_tipo_usuario)):
    if x_tipo_usuario not in [TipoUsuario.professor.value, TipoUsuario.administrador.value]:
        raise HTTPException(status_code=403, detail="Acesso Restrito: Exclusivo para professores.")
    return x_tipo_usuario


def verificar_papel_aluno(x_tipo_usuario: str = Depends(_resolver_tipo_usuario)):
    if x_tipo_usuario not in [TipoUsuario.aluno.value, TipoUsuario.administrador.value]:
        raise HTTPException(status_code=403, detail="Acesso Restrito: Exclusivo para alunos.")
    return x_tipo_usuario


def garantir_dados_do_proprio_aluno(user, email_aluno: Optional[str]) -> None:
    """Aluno só pode ler/gravar dados do próprio e-mail; administrador não tem essa restrição."""
    if user.tipo == TipoUsuario.aluno.value and email_aluno is not None:
        if str(email_aluno).strip().lower() != str(user.email).strip().lower():
            raise HTTPException(status_code=403, detail="Você só pode acessar os seus próprios dados.")