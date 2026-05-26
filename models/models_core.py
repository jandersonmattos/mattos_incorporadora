from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Text, Float, ForeignKey, Table, BigInteger, desc
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
from database import Base

# Tabela pivô Fornecedor <-> Tipos
fornecedor_tipos = Table(
    "fornecedor_tipos",
    Base.metadata,
    Column("fornecedor_id", UUID(as_uuid=True), ForeignKey("fornecedores.id", ondelete="CASCADE"), primary_key=True),
    Column("tipo_id", UUID(as_uuid=True), ForeignKey("tipos_fornecedor.id", ondelete="CASCADE"), primary_key=True)
)
