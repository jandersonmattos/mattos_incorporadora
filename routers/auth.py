from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from auth import authenticate_user
import models
import bcrypt
import random
from datetime import datetime, timedelta
from email_service import enviar_codigo_recuperacao

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email e senha são obrigatórios")
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return {"token": "fake-jwt-token", "user": {"id": user.id, "username": user.username, "email": user.email}}

@router.post("/forgot-password")
def forgot_password(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email é obrigatório")
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not user:
        return {"message": "Se o email existir, enviaremos um código"}
    db.query(models.PasswordResetToken).filter(models.PasswordResetToken.usuario_id == user.id, models.PasswordResetToken.usado == False).update({models.PasswordResetToken.usado: True})
    db.commit()
    codigo = str(random.randint(100000, 999999))
    codigo_hash = bcrypt.hashpw(codigo.encode(), bcrypt.gensalt()).decode()
    token = models.PasswordResetToken(usuario_id=user.id, codigo_hash=codigo_hash, expira_em=datetime.utcnow() + timedelta(minutes=10), usado=False)
    db.add(token)
    db.commit()
    enviar_codigo_recuperacao(user.email, codigo)
    return {"message": "Código enviado"}

@router.post("/verify-reset-code")
def verify_code(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")
    codigo = data.get("codigo")
    if not email or not codigo:
        raise HTTPException(status_code=400, detail="Email e código são obrigatórios")
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Código inválido")
    token = db.query(models.PasswordResetToken).filter(models.PasswordResetToken.usuario_id == user.id, models.PasswordResetToken.usado == False).order_by(models.PasswordResetToken.id.desc()).first()
    if not token:
        raise HTTPException(status_code=400, detail="Código inválido")
    if token.expira_em < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Código expirado")
    if not bcrypt.checkpw(codigo.encode(), token.codigo_hash.encode()):
        raise HTTPException(status_code=400, detail="Código inválido")
    return {"valid": True}

@router.post("/reset-password")
def reset_password(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")
    codigo = data.get("codigo")
    nova_senha = data.get("nova_senha")
    if not email or not codigo or not nova_senha:
        raise HTTPException(status_code=400, detail="Todos os campos são obrigatórios")
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Usuário não encontrado")
    token = db.query(models.PasswordResetToken).filter(models.PasswordResetToken.usuario_id == user.id, models.PasswordResetToken.usado == False).order_by(models.PasswordResetToken.id.desc()).first()
    if not token:
        raise HTTPException(status_code=400, detail="Código inválido")
    if token.expira_em < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Código expirado")
    if not bcrypt.checkpw(codigo.encode(), token.codigo_hash.encode()):
        raise HTTPException(status_code=400, detail="Código inválido")
    senha_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()
    user.senha_hash = senha_hash
    token.usado = True
    db.commit()
    return {"message": "Senha alterada com sucesso"}
