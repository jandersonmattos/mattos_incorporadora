from .models_core import *


class TipoFornecedor(Base):
    __tablename__ = "tipos_fornecedor"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String, nullable=False, unique=True)
    fornecedores = relationship("Fornecedor", secondary=fornecedor_tipos, back_populates="tipos")

class Fornecedor(Base):
    __tablename__ = "fornecedores"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String, nullable=False)
    razao_social = Column(String)
    cpf_cnpj = Column(String)
    email = Column(String)
    site = Column(String)
    responsavel = Column(String)
    telefone = Column(String)
    celular = Column(String)
    cep = Column(String)
    endereco = Column(String)
    numero = Column(String)
    bairro = Column(String)
    complemento = Column(String)
    estado = Column(String)
    cidade = Column(String)
    observacoes = Column(Text)
    avaliacao = Column(Integer, default=0)
    banco = Column(String)
    agencia = Column(String)
    numero_conta = Column(String)
    chave_pix = Column(String)
    tipos = relationship("TipoFornecedor", secondary=fornecedor_tipos, back_populates="fornecedores")
