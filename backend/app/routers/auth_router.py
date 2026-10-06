from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi import status
from fastapi.security import HTTPAuthorizationCredentials

from ..auth import create_access_token, get_current_user, hash_password, verify_password
from ..database import SessionLocal, User
from ..dependencies import security

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticação"])


@router.post("/registrar")
async def registrar_usuario(
    payload: dict = Body(...),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    nome = str(payload.get("nome") or "Usuário").strip()
    email = str(payload.get("email") or "").strip().lower()
    senha = str(payload.get("senha") or "")
    tipo = str(payload.get("tipo") or "aluno").strip().lower()

    if not email or not senha:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email e senha são obrigatórios.")
    if "@" not in email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Informe um e-mail válido.")
    if len(senha) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A senha deve ter pelo menos 6 caracteres.")
    if tipo not in {"administrador", "professor", "aluno"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de usuário inválido.")

    # Autocadastro público é permitido apenas para alunos.
    # Contas de professor e administrador só podem ser criadas por um administrador logado.
    if tipo != "aluno":
        solicitante = get_current_user(credentials)
        if solicitante.tipo != "administrador":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Somente administradores podem criar contas de professor ou administrador.",
            )

    with SessionLocal() as session:
        existente = session.query(User).filter(User.email == email).first()
        if existente:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Usuário já cadastrado.")

        usuario = User(
            nome=nome,
            email=email,
            senha_hash=hash_password(senha),
            tipo=tipo,
        )
        session.add(usuario)
        session.commit()
        session.refresh(usuario)

    return {
        "status": "sucesso",
        "mensagem": "Usuário cadastrado com sucesso.",
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "tipo": usuario.tipo,
        },
    }


@router.post("/login")
async def login_usuario(payload: dict = Body(...)):
    email = str(payload.get("email") or "").strip().lower()
    senha = str(payload.get("senha") or "")

    if not email or not senha:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email e senha são obrigatórios.")

    with SessionLocal() as session:
        usuario = session.query(User).filter(User.email == email).first()
        if not usuario:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas.")
        if not verify_password(senha, usuario.senha_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas.")

    token = create_access_token(usuario.email, usuario.tipo)
    return {
        "status": "sucesso",
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "tipo": usuario.tipo,
        },
    }
