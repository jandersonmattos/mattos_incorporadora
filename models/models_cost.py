from .models_core import *

class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String)
    lancamentos = relationship("Custo", back_populates="categoria")

class Recurso(Base):
    __tablename__ = "recursos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String)
    lancamentos = relationship("Custo", back_populates="recurso", viewonly=True)

class TipoArquivo(Base):
    __tablename__ = "tipos_arquivo"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String)
    arquivos = relationship("ArquivoProjeto", back_populates="tipo_arquivo")

class ItemEtapa(Base):
    __tablename__ = "itens_etapa"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String, nullable=False)
    projeto_id = Column(String, ForeignKey("projetos.id"))
    etapa_id = Column(UUID(as_uuid=True), ForeignKey("etapas_obra.id"), nullable=True)
    projeto = relationship("Projeto", back_populates="itens_etapa")
    etapa = relationship("EtapaObra", back_populates="itens")
    subitens = relationship(
        "Custo",
        back_populates="item",
        cascade="all, delete-orphan"
    )


class Custo(Base):
    __tablename__ = "custos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    descricao = Column(String)
    quantidade = Column(Float, default=1.0)
    valor_unitario = Column(Float, default=0.0)
    valor_previsto = Column(Float, default=0.0)
    valor_pago = Column(Float, default=0.0)
    data = Column(Date)
    projeto_id = Column(String, ForeignKey("projetos.id"))
    categoria_id = Column(UUID(as_uuid=True), ForeignKey("categorias.id"))
    recurso_nome = Column(String)
    recurso_id = Column(UUID(as_uuid=True), ForeignKey("recursos.id"), nullable=True)
    etapa_id = Column(UUID(as_uuid=True), ForeignKey("etapas_obra.id"))
    item_id = Column(UUID(as_uuid=True), ForeignKey("itens_etapa.id"), nullable=True)
    projeto = relationship("Projeto", back_populates="lancamentos")
    categoria = relationship("Categoria", back_populates="lancamentos")
    recurso = relationship("Recurso", back_populates="lancamentos")
    etapa = relationship("EtapaObra", back_populates="lancamentos")
    item = relationship("ItemEtapa", back_populates="subitens")
    @property
    def saldo_restante(self):
        return (self.valor_previsto or 0) - (self.valor_pago or 0)

class ArquivoProjeto(Base):
    __tablename__ = "arquivos_projeto"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome_arquivo = Column(String)
    caminho_arquivo = Column(String)
    projeto_id = Column(String, ForeignKey("projetos.id"))
    tipo_arquivo_id = Column(UUID(as_uuid=True), ForeignKey("tipos_arquivo.id"))
    projeto = relationship("Projeto", back_populates="arquivos")
    tipo_arquivo = relationship("TipoArquivo", back_populates="arquivos")
