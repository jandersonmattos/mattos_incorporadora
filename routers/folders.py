from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from uuid import UUID

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/projects/{project_id}/folders")
def get_project_folders(project_id: str, parent_id: str | None = None, db: Session = Depends(get_db)):
    valid_parent_id = None
    if parent_id:
        try:
            UUID(parent_id)
            valid_parent_id = parent_id
        except:
            valid_parent_id = None
    folders = db.query(models.ProjectFolder).filter(
        models.ProjectFolder.project_id == project_id,
        models.ProjectFolder.parent_folder_id == valid_parent_id
    ).order_by(models.ProjectFolder.name.asc()).all()
    files = db.query(models.ProjectFile).filter(
        models.ProjectFile.project_id == project_id,
        models.ProjectFile.folder_id == valid_parent_id
    ).order_by(models.ProjectFile.original_name.asc()).all()
    return {
        "folders": [
            {"id": str(folder.id), "name": folder.name, "parent_id": str(folder.parent_folder_id) if folder.parent_folder_id else None}
            for folder in folders
        ],
        "files": [
            {"id": str(file.id), "name": file.original_name, "url": file.file_url, "mime_type": file.mime_type}
            for file in files
        ]
    }

@router.post("/projects/{project_id}/folders")
def create_folder(project_id: str, data: dict, db: Session = Depends(get_db)):
    projeto = db.query(models.Projeto).filter(models.Projeto.id == project_id).first()
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    parent_id = data.get("parent_id") or None
    folder = models.ProjectFolder(
        project_id=project_id,
        parent_folder_id=parent_id,
        name=data.get("name"),
        created_by="Sistema"
    )
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return {"message": "Pasta criada com sucesso", "id": str(folder.id)}
