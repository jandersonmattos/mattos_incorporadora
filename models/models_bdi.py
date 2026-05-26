from .models_core import *

class BDI(Base):
    __tablename__ = "bdis"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String, nullable=False)
    formula = Column(Text, nullable=False)
    percentual_total = Column(Float, default=0)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    grupos = relationship("BDIGrupo", back_populates="bdi", cascade="all, delete-orphan", order_by="BDIGrupo.ordem")

class BDIGrupo(Base):
    __tablename__ = "bdi_grupos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bdi_id = Column(UUID(as_uuid=True), ForeignKey("bdis.id", ondelete="CASCADE"), nullable=False)
    codigo = Column(String(10), nullable=False)
    titulo = Column(String, nullable=False)
    ordem = Column(Integer, nullable=False, default=0)
    total_percentual = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    bdi = relationship("BDI", back_populates="grupos")
    itens = relationship("BDIGrupoItem", back_populates="grupo", cascade="all, delete-orphan", order_by="BDIGrupoItem.ordem")

class BDIGrupoItem(Base):
    __tablename__ = "bdi_grupo_itens"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grupo_id = Column(UUID(as_uuid=True), ForeignKey("bdi_grupos.id", ondelete="CASCADE"), nullable=False)
    descricao = Column(String, nullable=False)
    percentual = Column(Float, nullable=False, default=0)
    ordem = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    grupo = relationship("BDIGrupo", back_populates="itens")
