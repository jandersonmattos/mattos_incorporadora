from sqlalchemy import Column, Integer, String, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
from database import Base


class Projeto(Base):
    __tablename__ = "projetos"

    id = Column(Integer, primary_key=True)
    nome = Column(String)
    data_inicio = Column(Date)
    data_fim = Column(Date, nullable=True)
    endereco = Column(String)

    quantidade_unidades = Column(Integer, default=1)

    lancamentos = relationship("Custo", back_populates="projeto")
    arquivos = relationship("ArquivoProjeto", back_populates="projeto")


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True)
    nome = Column(String)

    lancamentos = relationship("Custo", back_populates="categoria")


class Recurso(Base):
    __tablename__ = "recursos"

    id = Column(Integer, primary_key=True)
    nome = Column(String)

    # 🔥 não usamos mais no custo (mantido só histórico)
    lancamentos = relationship("Custo", back_populates="recurso", viewonly=True)


class TipoArquivo(Base):
    __tablename__ = "tipos_arquivo"

    id = Column(Integer, primary_key=True)
    nome = Column(String)

    arquivos = relationship("ArquivoProjeto", back_populates="tipo_arquivo")


class Custo(Base):
    __tablename__ = "custos"

    id = Column(Integer, primary_key=True)

    descricao = Column(String)

    quantidade = Column(Float, default=1.0)
    valor_unitario = Column(Float, default=0.0)

    valor_previsto = Column(Float, default=0.0)
    valor_pago = Column(Float, default=0.0)

    data = Column(Date)

    projeto_id = Column(Integer, ForeignKey("projetos.id"))
    categoria_id = Column(Integer, ForeignKey("categorias.id"))

    # 🔥 NOVO CAMPO (TEXTO LIVRE)
    recurso_nome = Column(String)

    # 🔥 manter temporariamente para migração (pode remover depois)
    recurso_id = Column(Integer, ForeignKey("recursos.id"), nullable=True)

    etapa_id = Column(Integer, ForeignKey("etapas_obra.id"))

    projeto = relationship("Projeto", back_populates="lancamentos")
    categoria = relationship("Categoria", back_populates="lancamentos")

    # 🔥 manter temporário
    recurso = relationship("Recurso", back_populates="lancamentos")

    etapa = relationship("EtapaObra", back_populates="lancamentos")

    @property
    def saldo_restante(self):
        return (self.valor_previsto or 0) - (self.valor_pago or 0)


class ArquivoProjeto(Base):
    __tablename__ = "arquivos_projeto"

    id = Column(Integer, primary_key=True)

    nome_arquivo = Column(String)
    caminho_arquivo = Column(String)

    projeto_id = Column(Integer, ForeignKey("projetos.id"))
    tipo_arquivo_id = Column(Integer, ForeignKey("tipos_arquivo.id"))

    projeto = relationship("Projeto", back_populates="arquivos")
    tipo_arquivo = relationship("TipoArquivo", back_populates="arquivos")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    senha_hash = Column(String, nullable=False)


class EtapaObra(Base):
    __tablename__ = "etapas_obra"

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)

    lancamentos = relationship("Custo", back_populates="etapa")