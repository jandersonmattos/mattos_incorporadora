from .models_core import *
from sqlalchemy import LargeBinary


class EtapaObra(Base):
    __tablename__ = "etapas_obra"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    nome = Column(
        String,
        nullable=False,
        unique=True
    )

    lancamentos = relationship(
        "Custo",
        back_populates="etapa"
    )

    projetos = relationship(
        "ProjetoEtapa",
        back_populates="etapa",
        cascade="all, delete"
    )

    itens = relationship(
        "ItemEtapa",
        back_populates="etapa"
    )


class Projeto(Base):
    __tablename__ = "projetos"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    nome = Column(
        String,
        nullable=False
    )

    categoria = Column(
        String,
        default="Residencial"
    )

    status = Column(
        String,
        default="Planejamento"
    )

    data_inicio = Column(Date)

    data_fim = Column(
        Date,
        nullable=True
    )

    endereco = Column(String)
    numero = Column(String)
    bairro = Column(String)
    cidade = Column(String)
    estado = Column(String)
    cep = Column(String)

    descricao = Column(Text)

    proprietario = Column(String)
    proprietario_email = Column(String)
    proprietario_telefone = Column(String)

    area_construida = Column(
        Float,
        default=0
    )

    quantidade_unidades = Column(
        Integer,
        default=1
    )

    valor_venda = Column(
        Float,
        default=0.0
    )

    imagem = Column(
        LargeBinary,
        nullable=True
    )

    lancamentos = relationship(
        "Custo",
        back_populates="projeto"
    )

    arquivos = relationship(
        "ArquivoProjeto",
        back_populates="projeto"
    )

    unidades = relationship(
        "Unidade",
        back_populates="projeto",
        cascade="all, delete"
    )

    etapas = relationship(
        "ProjetoEtapa",
        back_populates="projeto",
        cascade="all, delete"
    )

    itens_etapa = relationship(
        "ItemEtapa",
        back_populates="projeto"
    )


class ProjetoEtapa(Base):
    __tablename__ = "projeto_etapas"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    projeto_id = Column(
        String,
        ForeignKey(
            "projetos.id",
            ondelete="CASCADE"
        )
    )

    # ETAPA GLOBAL/PADRÃO
    etapa_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "etapas_obra.id",
            ondelete="CASCADE"
        ),
        nullable=True
    )

    # ETAPA CUSTOMIZADA DA OBRA
    nome_customizado = Column(
        String,
        nullable=True
    )

    ordem = Column(
        Integer,
        default=0
    )

    concluida = Column(
        Boolean,
        default=False
    )

    # Percentual de execução da etapa (0 a 100)
    progresso = Column(
        Float,
        nullable=False,
        default=0.0
    )

    # =========================================
    # PERIODO PREVISTO
    # =========================================

    data_inicio_prevista = Column(
        Date,
        nullable=True
    )

    data_fim_prevista = Column(
        Date,
        nullable=True
    )

    # =========================================
    # PERIODO REAL
    # =========================================

    data_inicio_real = Column(
        Date,
        nullable=True
    )

    data_fim_real = Column(
        Date,
        nullable=True
    )

    projeto = relationship(
        "Projeto",
        back_populates="etapas"
    )

    etapa = relationship(
        "EtapaObra",
        back_populates="projetos"
    )

class Unidade(Base):
    __tablename__ = "unidades"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    numero = Column(String)

    valor_venda = Column(
        Float,
        default=0.0
    )

    projeto_id = Column(
        String,
        ForeignKey("projetos.id")
    )

    projeto = relationship(
        "Projeto",
        back_populates="unidades"
    )