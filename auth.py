import bcrypt
import models

from sqlalchemy.orm import Session

def authenticate_user(
    db: Session,
    email: str,
    password: str
):
    user = db.query(models.Usuario).filter(
        models.Usuario.email == email
    ).first()

    if not user:
        return None

    if not bcrypt.checkpw(
        password.encode('utf-8'),
        user.senha_hash.encode('utf-8')
    ):
        return None

    return user