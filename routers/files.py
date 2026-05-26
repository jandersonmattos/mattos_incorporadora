from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form
)
from sqlalchemy.orm import Session
from database import SessionLocal
import models
import os
import uuid
import shutil

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

@router.put("/folders/{folder_id}")
def rename_folder(folder_id: str, data: dict, db: Session = Depends(get_db)):
    folder = db.query(models.ProjectFolder).filter(models.ProjectFolder.id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Pasta não encontrada")
    folder.name = data.get("name", folder.name)
    db.commit()
    db.refresh(folder)
    return {"message": "Pasta renomeada com sucesso", "id": str(folder.id)}

@router.delete("/folders/{folder_id}")
def delete_folder(folder_id: str, db: Session = Depends(get_db)):
    folder = db.query(models.ProjectFolder).filter(models.ProjectFolder.id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Pasta não encontrada")
    db.delete(folder)
    db.commit()
    return {"message": "Pasta deletada com sucesso"}

@router.post("/projects/{project_id}/files/upload")
async def upload_project_file(
    project_id: str,

    file: UploadFile = File(...),

    folder_id: str | None = Form(None),

    db: Session = Depends(get_db)
):

    try:

        extension = os.path.splitext(
            file.filename
        )[1]

        generated_name = (
            f"{uuid.uuid4()}{extension}"
        )

        file_path = os.path.join(
            UPLOAD_DIR,
            generated_name
        )

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        project_file = models.ProjectFile(
            project_id=project_id,

            folder_id=folder_id,

            original_name=file.filename,

            file_url=f"/uploads/{generated_name}",

            mime_type=file.content_type
        )

        db.add(project_file)

        db.commit()

        db.refresh(project_file)

        return {
            "message":
                "Arquivo enviado com sucesso",

            "file": {
                "id":
                    str(project_file.id),

                "name":
                    project_file.original_name,

                "url":
                    project_file.file_url,

                "mime_type":
                    project_file.mime_type
            }
        }

    except Exception as e:

        db.rollback()

        print(e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.delete("/files/{file_id}")
def delete_file(file_id: str, db: Session = Depends(get_db)):
    file = db.query(models.ProjectFile).filter(models.ProjectFile.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    db.delete(file)
    db.commit()
    return {"message": "Arquivo deletado com sucesso"}
